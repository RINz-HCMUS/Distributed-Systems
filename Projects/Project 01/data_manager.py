import os
import json
import threading
from datetime import datetime, timedelta

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
LOG_FILE = os.path.join(DATA_DIR, "chatlog.jsonl")

lock = threading.Lock()

# ========== INITIALIZATION ==========
def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, default in [(USERS_FILE, {}), (GROUPS_FILE, {}), (LOG_FILE, None)]:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                if default is not None:
                    json.dump(default, f, indent=4)


# ========== LOGGING ==========
def log_event(event_type, actor, target=None, message=None, metadata=None):
    ensure_dir()
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "type": event_type,
        "actor": actor,
        "target": target,
        "message": message,
        "metadata": metadata or {}
    }
    with lock, open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ========== USER MANAGEMENT ==========
def load_users():
    ensure_dir()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with lock, open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_user(username):
    users = load_users()
    if username not in users:
        users[username] = {
            "username": username,
            "status": "offline",
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "groups": []
        }
        save_users(users)
        log_event("USER_REGISTER", username, message="User registered.")
    return users


def update_user_status(username, status):
    users = load_users()
    if username in users:
        users[username]["status"] = status
        users[username]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        log_event("USER_STATUS", username, message=f"{username} -> {status}")


# ========== GROUP MANAGEMENT ==========
def load_groups():
    ensure_dir()
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_groups(groups):
    with lock, open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=4, ensure_ascii=False)


def create_group(group_name, creator):
    groups = load_groups()
    if group_name not in groups:
        groups[group_name] = {
            "group_name": group_name,
            "admin": creator,
            "members": [creator],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_groups(groups)
        log_event("GROUP_CREATE", creator, target=group_name,
                  message=f"Group {group_name} created by {creator}.")
    return groups


def add_member_to_group(group, user):
    groups = load_groups()
    if group in groups and user not in groups[group]["members"]:
        groups[group]["members"].append(user)
        save_groups(groups)
        log_event("GROUP_ADD_MEMBER", user, target=group,
                  message=f"{user} joined {group}.")


def remove_member_from_group(group, user):
    groups = load_groups()
    if group in groups and user in groups[group]["members"]:
        groups[group]["members"].remove(user)
        save_groups(groups)
        log_event("GROUP_REMOVE_MEMBER", user, target=group,
                  message=f"{user} left {group}.")


# ========== HISTORY RETRIEVAL ==========
def get_private_history(userA, userB, days=3, limit=10):
    ensure_dir()
    cutoff = datetime.now() - timedelta(days=days)
    results = []
    if not os.path.exists(LOG_FILE): return results

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = list(f)

    for line in reversed(lines):
        entry = json.loads(line)
        if entry["type"] == "MESSAGE_PRIVATE" and (
            (entry["actor"] == userA and entry["target"] == userB)
            or (entry["actor"] == userB and entry["target"] == userA)
        ):
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts >= cutoff:
                results.append(entry)
                if len(results) >= limit: break
    return list(reversed(results))


def get_group_history(group, days=3, limit=20):
    ensure_dir()
    cutoff = datetime.now() - timedelta(days=days)
    results = []
    if not os.path.exists(LOG_FILE): return results

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = list(f)

    for line in reversed(lines):
        entry = json.loads(line)
        if entry["target"] == group and (
            entry["type"].startswith("MESSAGE_GROUP") or
            entry["type"].startswith("GROUP_")
        ):
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts >= cutoff:
                results.append(entry)
                if len(results) >= limit: break
    return list(reversed(results))
