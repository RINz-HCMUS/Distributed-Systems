import grpc
import threading
from colorama import Fore, Style, init
import chat_pb2, chat_pb2_grpc

init(autoreset=True)

def color_user(name, me):
    return f"{Fore.CYAN}{name}{Style.RESET_ALL}" if name == me else f"{Fore.GREEN}{name}{Style.RESET_ALL}"

def color_group(name):
    return f"{Fore.YELLOW}{name}{Style.RESET_ALL}"

def color_system(msg):
    return f"{Fore.MAGENTA}{msg}{Style.RESET_ALL}"

def color_error(msg):
    return f"{Fore.RED}{msg}{Style.RESET_ALL}"

def listen_for_messages(stub, username):
    responses = stub.StreamMessages(chat_pb2.ConnectRequest(username=username))
    for msg in responses:
        if msg.type == "private":
            sender = color_user(msg.sender, username)
            print(f"\n[{msg.timestamp}] [from {sender}] {msg.msg}")
        elif msg.type == "group":
            sender = color_user(msg.sender, username)
            group = color_group(msg.group)
            print(f"\n[{msg.timestamp}] [group {group}] [{sender}] {msg.msg}")
        else:
            print(color_system(f"\n[{msg.timestamp}] {msg.msg}"))
        print(">> ", end="", flush=True)

def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        username = input("Enter your username: ").strip()
        print(color_system(f"Welcome, {username}! Connecting..."))
        threading.Thread(target=listen_for_messages, args=(stub, username), daemon=True).start()
        while True:
            cmd = input(">> ").strip()
            if not cmd:
                continue
            response = stub.SendCommand(chat_pb2.CommandRequest(username=username, command=cmd))
            if "error" in response.message.lower():
                print(color_error(response.message))
            else:
                print(response.message)
            if cmd == "logout":
                break

if __name__ == "__main__":
    main()
