import grpc
import chat_pb2
import chat_pb2_grpc
import threading

class ChatClient:
    def __init__(self, username):
        self.username = username
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.register()

    # ----- Register -----
    def register(self):
        response = self.stub.RegisterUser(chat_pb2.UserInfo(username=self.username))
        print(response.message)
        if not response.success:
            exit(0)
        if response.online_users:
            print("👥 Online users:")
            for u in response.online_users:
                print(f"- {u}")
        threading.Thread(target=self.listen_messages, daemon=True).start()
        self.main_menu()

    # ----- Listen messages -----
    def listen_messages(self):
        def gen():
            while True:
                sender = input("To (user/group): ")
                msg = input("Message: ")
                is_group = input("Group? (y/n): ").lower() == "y"
                yield chat_pb2.ChatMessage(sender=self.username,
                                           receiver=sender,
                                           message=msg,
                                           is_group=is_group)
        responses = self.stub.SendMessage(gen())
        for r in responses:
            print(f"\n[{r.sender} → {r.receiver}] {r.message}")

    # ----- Commands -----
    def list_users(self):
        resp = self.stub.GetUserStatus(chat_pb2.UserInfo(username=self.username))
        print("\n🧭 Users:")
        for u in resp.users:
            print(f"- {u.username:10} | {u.status:7} | Last seen: {u.last_seen}")

    def get_private_history(self):
        user2 = input("Enter user to view history: ")
        req = chat_pb2.HistoryRequest(username=self.username, target=user2, days=3, limit=10, is_group=False)
        resp = self.stub.GetPrivateHistory(req)
        print("\n📜 Private chat history:")
        for msg in resp.messages:
            print(f"[{msg.timestamp}] {msg.actor} → {msg.target}: {msg.message}")

    def get_group_history(self):
        group = input("Enter group name: ")
        req = chat_pb2.HistoryRequest(username=self.username, target=group, days=3, limit=20, is_group=True)
        resp = self.stub.GetGroupHistory(req)
        print(f"\n📜 History of {group}:")
        for msg in resp.messages:
            print(f"[{msg.timestamp}] {msg.actor}: {msg.message}")

    def main_menu(self):
        while True:
            print("\n=== Commands ===")
            print("1. /list  - Show user list")
            print("2. /hist  - Private chat history")
            print("3. /ghist - Group chat history")
            print("4. /exit  - Quit\n")
            cmd = input("Command: ")
            if cmd == "/list": self.list_users()
            elif cmd == "/hist": self.get_private_history()
            elif cmd == "/ghist": self.get_group_history()
            elif cmd == "/exit": print("Bye!"); break


if __name__ == "__main__":
    name = input("Enter username: ")
    ChatClient(name)
