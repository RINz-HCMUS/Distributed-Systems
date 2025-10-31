import grpc
import threading
import sys
import os
import chat_pb2, chat_pb2_grpc

# ==== LUỒNG NGHE TIN NHẮN ====

def listen_for_messages(stub, username):
    responses = stub.StreamMessages(chat_pb2.ConnectRequest(username=username))
    try:
        for msg in responses:
            ts = msg.timestamp
            sender = msg.sender
            group = msg.group
            text = msg.msg

            print()  # xuống dòng cho đẹp

            if msg.type == "private":
                print(f"[{ts}] [from {sender}] {text}")

            elif msg.type == "group":
                print(f"[{ts}] [group {group}] [{sender}] {text}")

            else:  # system or unknown
                print(f"[{ts}] {text}")

            # In lại prompt
            print(">> ", end="", flush=True)

    except grpc.RpcError:
        pass


# ==== HÀM CHÍNH ====

def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        username = input("Enter your username: ").strip()

        print("Connecting...")
        threading.Thread(target=listen_for_messages, args=(stub, username), daemon=True).start()

        print(f"Welcome, {username}!")
        print("Type commands or 'help' to see available commands.")

        while True:
            cmd = input(">> ").strip()
            if not cmd:
                continue

            # --- NGĂN USER GỬI TIN CHO CHÍNH MÌNH ---
            if cmd.startswith("msg user"):
                parts = cmd.split()
                if len(parts) >= 3:
                    target = parts[2]
                    if target == username:
                        print("⚠️  You cannot send a message to yourself.")
                        continue

            # Gửi lệnh đến server
            response = stub.SendCommand(chat_pb2.CommandRequest(username=username, command=cmd))
            message = response.message

            # Nếu là lỗi → in nguyên dòng
            if "error" in message.lower() or "invalid" in message.lower() or "❌" in message:
                print(message)
            else:
                print(message)

            if cmd == "logout":
                break


if __name__ == "__main__":
    main()
