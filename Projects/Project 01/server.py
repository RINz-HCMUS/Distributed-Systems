import grpc
import chat_pb2
import chat_pb2_grpc
import logging
import data_manager as dm
from concurrent import futures
from datetime import datetime

logging.basicConfig(filename="server.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")


class ChatServer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.user_sessions = {}  # username → {"stream", "status", "groups"}

    # ---------- USER REGISTER ----------
    def RegisterUser(self, request, context):
        username = request.username
        dm.add_user(username)

        # Nếu đã online rồi → từ chối
        if username in self.user_sessions and self.user_sessions[username]["status"] == "online":
            msg = f"{username} is already online."
            logging.warning(msg)
            return chat_pb2.RegisterReply(message=msg, success=False)

        dm.update_user_status(username, "online")
        self.user_sessions[username] = {
            "stream": None,
            "status": "online",
            "groups": []
        }

        online_list = [u for u, s in self.user_sessions.items() if s["status"] == "online" and u != username]
        dm.log_event("USER_LOGIN", username, message=f"{username} logged in.")
        return chat_pb2.RegisterReply(message=f"Welcome {username}!", success=True,
                                      online_users=online_list)

    # ---------- USER STATUS ----------
    def GetUserStatus(self, request, context):
        users = dm.load_users()
        resp = chat_pb2.UserStatusResponse()
        for u, info in users.items():
            us = resp.users.add()
            us.username = u
            us.status = info["status"]
            us.last_seen = info["last_seen"]
            us.groups.extend(info["groups"])
        return resp

    # ---------- GROUP MANAGEMENT ----------
    def CreateGroup(self, request, context):
        dm.create_group(request.group_name, request.creator)
        return chat_pb2.ServerReply(message=f"Group {request.group_name} created.", success=True)

    def AddToGroup(self, request, context):
        dm.add_member_to_group(request.group_name, request.username)
        return chat_pb2.ServerReply(message=f"{request.username} added to {request.group_name}.", success=True)

    def LeaveGroup(self, request, context):
        dm.remove_member_from_group(request.group_name, request.username)
        return chat_pb2.ServerReply(message=f"{request.username} left {request.group_name}.", success=True)

    # ---------- MESSAGING ----------
    def SendMessage(self, request_iterator, context):
        current_user = None
        try:
            for msg in request_iterator:
                current_user = msg.sender
                if msg.is_group:
                    dm.log_event("MESSAGE_GROUP", msg.sender, msg.receiver, msg.message)
                else:
                    dm.log_event("MESSAGE_PRIVATE", msg.sender, msg.receiver, msg.message)
                yield msg
        except Exception as e:
            logging.error(f"SendMessage error: {e}")
        finally:
            if current_user:
                dm.update_user_status(current_user, "offline")
                self.user_sessions[current_user]["status"] = "offline"
                logging.info(f"{current_user} disconnected.")

    # ---------- HISTORY ----------
    def GetPrivateHistory(self, request, context):
        history = dm.get_private_history(request.username, request.target,
                                         request.days or 3, request.limit or 10)
        resp = chat_pb2.HistoryResponse()
        for h in history:
            e = resp.messages.add()
            e.timestamp = h["timestamp"]
            e.actor = h["actor"]
            e.target = h["target"]
            e.message = h["message"]
        return resp

    def GetGroupHistory(self, request, context):
        history = dm.get_group_history(request.target,
                                       request.days or 3, request.limit or 20)
        resp = chat_pb2.HistoryResponse()
        for h in history:
            e = resp.messages.add()
            e.timestamp = h["timestamp"]
            e.actor = h["actor"]
            e.target = h["target"]
            e.message = h["message"]
        return resp


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServer(), server)
    server.add_insecure_port("[::]:50051")
    print("🚀 Chat server started at port 50051.")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
