import json, os
from datetime import datetime

# ===== PATHS =====
DATA_DIR = "data"
LOG_DIR = "logs"
USERS_PATH = os.path.join(DATA_DIR, "users.json")
GROUPS_PATH = os.path.join(DATA_DIR, "groups.json")
CHATLOG_PATH = os.path.join(LOG_DIR, "chatlog.jsonl")
SERVERLOG_PATH = os.path.join(LOG_DIR, "serverlog.jsonl")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True) 

# ===== HELPER =====
def _ordered_dict(entry: dict):
    """Đảm bảo key 'timestamp' luôn đứng đầu."""
    ts = entry.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ordered = {"timestamp": ts}
    for k, v in entry.items():
        if k != "timestamp":
            ordered[k] = v
    return ordered

# ===== USER =====
def get_users():
    return json.load(open(USERS_PATH, "r", encoding="utf-8")) if os.path.exists(USERS_PATH) else {}

def save_users(users):
    json.dump(users, open(USERS_PATH, "w", encoding="utf-8"), indent=4)

# ===== GROUP =====
def get_groups():
    return json.load(open(GROUPS_PATH, "r", encoding="utf-8")) if os.path.exists(GROUPS_PATH) else {}

def save_groups(groups):
    json.dump(groups, open(GROUPS_PATH, "w", encoding="utf-8"), indent=4)

# ===== CHAT LOG =====
def append_chat_log(entry):
    ordered = _ordered_dict(entry)
    with open(CHATLOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ordered, ensure_ascii=False) + "\n")

def get_incoming_messages(username, n=10):
    """Chỉ lấy tin nhắn ĐẾN user."""
    if not os.path.exists(CHATLOG_PATH):
        return []
    lines = [json.loads(l) for l in open(CHATLOG_PATH, "r", encoding="utf-8")]
    groups = get_groups()
    messages = [
        l for l in lines
        if (l["type"] == "private" and l.get("to") == username)
        or (l["type"] == "group" and username in groups.get(l.get("group"), {}).get("members", []))
    ]
    return messages[-n:]

def get_history(username, target, kind="user", n=10):
    """Lịch sử tin nhắn giữa user và target (user/group)."""
    if not os.path.exists(CHATLOG_PATH):
        return []
    lines = [json.loads(l) for l in open(CHATLOG_PATH, "r", encoding="utf-8")]
    if kind == "user":
        return [
            l for l in lines
            if l["type"] == "private" and ((l["from"] == username and l["to"] == target) or (l["from"] == target and l["to"] == username))
        ][-n:]
    elif kind == "group":
        return [
            l for l in lines
            if l["type"] == "group" and l.get("group") == target
        ][-n:]
    return []

# ===== SERVER LOG =====
def append_server_log(entry):
    ordered = _ordered_dict(entry)
    with open(SERVERLOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(ordered, ensure_ascii=False) + "\n")
