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
            # ===== Help =====
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
                    "list users\n"
                    "list groups\n"
                    "history user <name> [n]\n"
                    "history group <name> [n]\n"
                    "inbox [n]\n"
                    "logout\n"
                    "--------------------------------------------------"
                )
                return chat_pb2.CommandReply(message=msg)

            # ===== Logout =====
            if command == "logout":
                users = get_users()
                if username in users:
                    users[username]["online"] = False
                    users[username]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_users(users)
                append_server_log({"category": "system", "event": "logout", "user": username})
                return chat_pb2.CommandReply(message="Logged out successfully.")

            # ===== List users =====
            if command.startswith("list users"):
                users = get_users()
                online = [u for u, d in users.items() if d.get("online")]
                msg = "Online users:\n" + "\n".join(f"- {u}" for u in online)
                return chat_pb2.CommandReply(message=msg)

            # ===== List groups =====
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

            # ===== Create group =====
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

            # ===== Add member =====
            if parts[:2] == ["add", "member"] and len(parts) >= 4:
                gname, uname = parts[2], parts[3]
                groups = get_groups()
                users = get_users()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
                if uname not in users:
                    return chat_pb2.CommandReply(message="User not found.")
                if uname in groups[gname]["members"]:
                    return chat_pb2.CommandReply(message="User already in group.")
                groups[gname]["members"].append(uname)
                save_groups(groups)
                users[uname]["groups"].append(gname)
                save_users(users)
                append_server_log({"category": "group", "event": "add_member", "group": gname, "user": uname})
                return chat_pb2.CommandReply(message=f"Added {uname} to {gname}.")

            # ===== Send private message =====
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

            # ===== Send group message =====
            if parts[:2] == ["msg", "group"] and len(parts) >= 4:
                gname = parts[2]
                groups = get_groups()
                if gname not in groups:
                    return chat_pb2.CommandReply(message="Group not found.")
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

            # ===== Inbox =====
            if parts[0] == "inbox":
                n = int(parts[1]) if len(parts) > 1 else 10
                messages = get_incoming_messages(username, n)
                if not messages:
                    return chat_pb2.CommandReply(message="No incoming messages.")
                lines = []
                for e in messages:
                    if e["type"] == "private":
                        lines.append(f"[{e['timestamp']}] [from {e['from']}] {e['msg']}")
                    elif e["type"] == "group":
                        lines.append(f"[{e['timestamp']}] [group {e['group']}] [{e['from']}] {e['msg']}")
                return chat_pb2.CommandReply(message="\n".join(lines))

            # ===== History =====
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

            if parts[:2] == ["history", "group"] and len(parts) >= 3:
                target = parts[2]
                n = int(parts[3]) if len(parts) >= 4 else 10
                messages = get_history(username, target, "group", n)
                if not messages:
                    return chat_pb2.CommandReply(message=f"No group history for {target}.")
                lines = [
                    f"[{e['timestamp']}] [{e['group']}] [{'you' if e['from']==username else e['from']}] {e['msg']}"
                    for e in messages
                ]
                return chat_pb2.CommandReply(message="\n".join(lines))

            # ===== Invalid command =====
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
