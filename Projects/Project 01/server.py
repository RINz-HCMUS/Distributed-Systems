import grpc
import time
import threading
from concurrent import futures
from datetime import datetime
import chat_pb2, chat_pb2_grpc
from data_manager import *

clients = {}
lock = threading.Lock()

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def SendCommand(self, request, context):
        username = request.username
        command = request.command.strip()
        parts = command.split()

        if not username:
            return chat_pb2.CommandReply(message="Username required")

        try:
            # ===== HELP =====
            if command == "help":
                msg = (
                    "Available commands:\n"
                    "--------------------------------------------------\n"
                    "msg user <username> <message> /end/\n"
                    "msg group <group> <message> /end/\n"
                    "create group <name>\n"
                    "add member <group> <user>\n"
                    "remove member <group> <user>\n"
                    "leave group <group>\n"
                    "delete group <group>\n"
                    "list users\n"
                    "list groups\n"
                    "history user <name> [n]\n"
                    "history group <name> [n]\n"
                    "inbox [n]\n"
                    "sent [n]\n"
                    "logout\n"
                    "--------------------------------------------------"
                )
                return chat_pb2.CommandReply(message=msg)

            # ===== LOGOUT =====
            if command == "logout":
                users = get_users()
                if username in users:
                    users[username]["online"] = False
                    users[username]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_users(users)
                append_server_log({"category": "system", "event": "logout", "user": username})
                return chat_pb2.CommandReply(message="Logged out successfully.")

            # ===== LIST USERS =====
            if command.startswith("list users"):
                users = get_users()
                online = [u for u, d in users.items() if d.get("online")]
                msg = "Online users:\n" + "\n".join(f"- {u}" for u in online) if online else "Online users:\n- (none)"
                return chat_pb2.CommandReply(message=msg)

            # ===== LIST GROUPS =====
            if command.startswith("list groups"):
                users = get_users()
                groups = get_groups()
                joined = users.get(username, {}).get("groups", [])
                if not joined:
                    return chat_pb2.CommandReply(message="You haven't joined any groups.")
                lines = []
                for g in joined:
                    admin = groups[g]["admin"]
                    tag = "<admin: you>" if admin == username else f"<admin: {admin}>"
                    lines.append(f"- {g} {tag}")
                return chat_pb2.CommandReply(message="\n".join(lines))

            # ===== CREATE GROUP =====
            if parts[:2] == ["create", "group"] and len(parts) >= 3:
                gname = parts[2]
                groups = get_groups()
                if gname in groups:
                    return chat_pb2.CommandReply(message="Group already exists.")
                groups[gname] = {"admin": username, "members": [username]}
                save_groups(groups)
                users = get_users()
                users.setdefault(username, {"groups": []})
                users[username]["groups"].append(gname)
                save_users(users)
                append_server_log({"category": "group", "event": "create", "group": gname, "admin": username})
                return chat_pb2.CommandReply(message=f"Group '{gname}' created.")

            # ===== ADD MEMBER (any member can add) =====
            if parts[:2] == ["add", "member"] and len(parts) >= 4:
                gname, uname = parts[2], parts[3]
                groups = get_groups()
                users = get_users()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if username not in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message="You must be a member to add someone.")
                if uname not in users:
                    return chat_pb2.CommandReply(message="User not found.")
                if uname in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message="User already in group.")
                groups[gname]["members"].append(uname)
                save_groups(groups)
                users[uname].setdefault("groups", [])
                users[uname]["groups"].append(gname)
                save_users(users)
                append_server_log({"category": "group", "event": "add_member", "group": gname, "user": uname, "by": username})
                return chat_pb2.CommandReply(message=f"Added {uname} to {gname}.")

            # ===== REMOVE MEMBER (only admin) =====
            if parts[:2] == ["remove", "member"] and len(parts) >= 4:
                gname, uname = parts[2], parts[3]
                groups = get_groups()
                users = get_users()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if groups[gname]["admin"] != username:
                    return chat_pb2.CommandReply(message="Only the admin can remove members.")
                if uname not in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message=f"{uname} is not a member of {gname}.")
                if uname == username:
                    return chat_pb2.CommandReply(message="Admin cannot remove themselves. Use delete group instead.")
                groups[gname]["members"].remove(uname)
                save_groups(groups)
                if uname in users and gname in users[uname].get("groups", []):
                    users[uname]["groups"].remove(gname)
                    save_users(users)
                append_server_log({"category": "group", "event": "remove_member", "group": gname, "user": uname, "by": username})
                return chat_pb2.CommandReply(message=f"Removed {uname} from {gname}.")

            # ===== LEAVE GROUP (any member; admin special case) =====
            if parts[:2] == ["leave", "group"] and len(parts) >= 3:
                gname = parts[2]
                groups = get_groups()
                users = get_users()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if username not in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message="You are not a member of this group.")

                # Admin case
                if groups[gname]["admin"] == username:
                    if len(groups[gname]["members"]) > 1:
                        return chat_pb2.CommandReply(message="Admin cannot leave while other members remain. Remove them or delete group instead.")
                    else:
                        del groups[gname]
                        save_groups(groups)
                        if gname in users[username]["groups"]:
                            users[username]["groups"].remove(gname)
                            save_users(users)
                        append_server_log({"category": "group", "event": "auto_delete", "group": gname, "by": username})
                        return chat_pb2.CommandReply(message=f"You left group {gname}. Group deleted as you were the last member.")

                # Normal member
                groups[gname]["members"].remove(username)
                save_groups(groups)
                if gname in users[username].get("groups", []):
                    users[username]["groups"].remove(gname)
                    save_users(users)
                append_server_log({"category": "group", "event": "leave_group", "group": gname, "user": username})
                return chat_pb2.CommandReply(message=f"You left group {gname}.")

            # ===== DELETE GROUP (only admin) =====
            if parts[:2] == ["delete", "group"] and len(parts) >= 3:
                gname = parts[2]
                groups = get_groups()
                users = get_users()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if groups[gname]["admin"] != username:
                    return chat_pb2.CommandReply(message="Only the admin can delete this group.")
                for m in groups[gname]["members"]:
                    if m in users and gname in users[m].get("groups", []):
                        users[m]["groups"].remove(gname)
                del groups[gname]
                save_groups(groups)
                save_users(users)
                append_server_log({"category": "group", "event": "delete_group", "group": gname, "by": username})
                return chat_pb2.CommandReply(message=f"Group {gname} deleted successfully.")

            # ===== MSG USER =====
            if parts[:2] == ["msg", "user"] and len(parts) >= 4:
                to_user = parts[2]
                if to_user not in get_users():
                    return chat_pb2.CommandReply(message=f"User {to_user} not found.")
                msg = command.split(to_user, 1)[1].replace("/end/", "").strip()
                if not msg:
                    return chat_pb2.CommandReply(message="Message cannot be empty.")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry = {"timestamp": timestamp, "type": "private", "from": username, "to": to_user, "msg": msg}
                append_chat_log(entry)
                if to_user in clients:
                    clients[to_user].put(entry)
                return chat_pb2.CommandReply(message=f"Sent to {to_user}.")

            # ===== MSG GROUP =====
            if parts[:2] == ["msg", "group"] and len(parts) >= 4:
                gname = parts[2]
                groups = get_groups()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if username not in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message="You are not a member of this group.")
                msg = command.split(gname, 1)[1].replace("/end/", "").strip()
                if not msg:
                    return chat_pb2.CommandReply(message="Message cannot be empty.")
                members = groups[gname]["members"]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry = {"timestamp": timestamp, "type": "group", "group": gname, "from": username, "msg": msg}
                append_chat_log(entry)
                for m in members:
                    if m != username and m in clients:
                        clients[m].put(entry)
                return chat_pb2.CommandReply(message=f"Sent to group {gname}.")

            # ===== INBOX =====
            if parts[0] == "inbox":
                n = int(parts[1]) if len(parts) > 1 else 10
                messages = get_incoming_messages(username, n)
                if not messages:
                    return chat_pb2.CommandReply(message="No incoming messages.")
                groups = get_groups()
                filtered = []
                for e in messages:
                    if e["type"] == "private" and e.get("to") == username:
                        filtered.append(e)
                    elif e["type"] == "group" and e.get("from") != username and username in groups.get(e.get("group"), {}).get("members", []):
                        filtered.append(e)
                if not filtered:
                    return chat_pb2.CommandReply(message="No incoming messages.")
                lines = []
                for e in filtered[-n:]:
                    if e["type"] == "private":
                        lines.append(f"[{e['timestamp']}] [from {e['from']}] {e['msg']}")
                    elif e["type"] == "group":
                        lines.append(f"[{e['timestamp']}] [group {e['group']}] [{e['from']}] {e['msg']}")
                return chat_pb2.CommandReply(message="\n".join(lines))

            # ===== SENT =====
            if parts[0] == "sent":
                n = int(parts[1]) if len(parts) > 1 else 10
                import os, json
                from data_manager import CHATLOG_PATH
                if not os.path.exists(CHATLOG_PATH):
                    return chat_pb2.CommandReply(message="No sent messages found.")
                lines = [json.loads(l) for l in open(CHATLOG_PATH, "r", encoding="utf-8")]
                sent_msgs = [
                    e for e in lines
                    if (e["type"] == "private" and e.get("from") == username)
                    or (e["type"] == "group" and e.get("from") == username)
                ]
                if not sent_msgs:
                    return chat_pb2.CommandReply(message="No sent messages.")
                out = []
                for e in sent_msgs[-n:]:
                    if e["type"] == "private":
                        out.append(f"[{e['timestamp']}] [to {e['to']}] {e['msg']}")
                    else:
                        out.append(f"[{e['timestamp']}] [group {e['group']}] [to all] {e['msg']}")
                return chat_pb2.CommandReply(message="\n".join(out))

            # ===== HISTORY USER =====
            if parts[:2] == ["history", "user"] and len(parts) >= 3:
                target = parts[2]
                n = int(parts[3]) if len(parts) >= 4 else 10
                messages = get_history(username, target, "user", n)
                if not messages:
                    return chat_pb2.CommandReply(message=f"No history with {target}.")
                lines = [
                    f"[{e['timestamp']}] [{'you' if e['from']==username else e['from']}] {e['msg']}"
                    for e in messages
                ]
                return chat_pb2.CommandReply(message="\n".join(lines))

            # ===== HISTORY GROUP =====
            if parts[:2] == ["history", "group"] and len(parts) >= 3:
                gname = parts[2]
                n = int(parts[3]) if len(parts) >= 4 else 10
                groups = get_groups()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if username not in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message="You are not a member of this group.")
                messages = get_history(username, gname, "group", n)
                if not messages:
                    return chat_pb2.CommandReply(message=f"No group history for {gname}.")
                lines = [
                    f"[{e['timestamp']}] [{e['group']}] [{'you' if e['from']==username else e['from']}] {e['msg']}"
                    for e in messages
                ]
                return chat_pb2.CommandReply(message="\n".join(lines))

            # ===== INVALID =====
            append_server_log({"category": "command", "event": "invalid_command", "user": username, "input": command})
            return chat_pb2.CommandReply(message=f"❌ Invalid command: '{command}'. Type 'help'.")

        except Exception as e:
            print("🔥 SERVER ERROR:", e)
            append_server_log({"category": "error", "message": str(e), "function": "SendCommand", "input": command})
            return chat_pb2.CommandReply(message="⚠️ Server error. Please try again.")

    def StreamMessages(self, request, context):
        import queue
        username = request.username
        q = queue.Queue()
        clients[username] = q

        users = get_users()
        users.setdefault(username, {"online": True, "groups": []})
        users[username]["online"] = True
        save_users(users)
        append_server_log({"category": "system", "event": "login", "user": username})

        try:
            while True:
                entry = q.get()
                yield chat_pb2.ChatMessage(
                    timestamp=entry["timestamp"],
                    type=entry["type"],
                    sender=entry.get("from", ""),
                    receiver=entry.get("to", ""),
                    group=entry.get("group", ""),
                    msg=entry.get("msg", ""),
                )
        except Exception as e:
            append_server_log({"category": "error", "message": str(e), "function": "StreamMessages"})
        finally:
            if username in clients:
                del clients[username]
            users = get_users()
            if username in users:
                users[username]["online"] = False
                users[username]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_users(users)
            append_server_log({"category": "system", "event": "disconnect", "user": username})


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("✅ Server started on port 50051.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Server stopped.")


if __name__ == "__main__":
    serve()
