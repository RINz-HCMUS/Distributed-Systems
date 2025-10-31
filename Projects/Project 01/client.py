import os, sys, logging

# LOG FILE PATH
log_path = "logs/grpc_warnings.log"
# Check and create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")
log_file = open(log_path, "w", encoding="utf-8")
sys.stderr = log_file  # redirect toàn bộ stderr

# Block GRPC/ABSEIL warnings to log file
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""
logging.getLogger().setLevel(logging.ERROR)

# ---------------------------------------------------------------
import grpc
import threading
from colorama import Fore, Style, init
import chat_pb2, chat_pb2_grpc

os.system("")
init(autoreset=True, convert=True)


# HIGHLIGHT FUNCTIONS
def print_user(name, me):
    """USER NAME: green if me, cyan if others."""
    if name == me:
        print(Fore.GREEN + name + Style.RESET_ALL, end="")
    else:
        print(Fore.CYAN + name + Style.RESET_ALL, end="")

def print_group(name):
    """GROUP NAME: yellow."""
    print(Fore.YELLOW + name + Style.RESET_ALL, end="")

def print_system(msg):
    """SYSTEM MESSAGE: purple."""
    print(Fore.MAGENTA + msg + Style.RESET_ALL)

def print_error(msg):
    """ERROR MESSAGE: red."""
    print(Fore.RED + msg + Style.RESET_ALL)


# ==== MESSAGE LISTENING ====

def listen_for_messages(stub, username):
    responses = stub.StreamMessages(chat_pb2.ConnectRequest(username=username))
    try:
        for msg in responses:
            ts = msg.timestamp
            sender = msg.sender
            group = msg.group
            text = msg.msg

            print() 

            if msg.type == "private":
                print(f"[{ts}] [from ", end="")
                print_user(sender, username)
                print(f"] {text}")

            elif msg.type == "group":
                print(f"[{ts}] [group ", end="")
                print_group(group)
                print("] [", end="")
                print_user(sender, username)
                print(f"] {text}")

            else:  # system or unknown
                print_system(f"[{ts}] {text}")

            # Reprint prompt
            print(">> ", end="", flush=True)

    except grpc.RpcError:
        pass


# ==== MAIN FUNCTION ====

def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        username = input("Enter your username: ").strip()

        print_system("Connecting...")
        threading.Thread(target=listen_for_messages, args=(stub, username), daemon=True).start()

        print_system(f"Welcome, {username}!")
        print_system("Type commands or 'help' to see available commands.")

        while True:
            cmd = input(">> ").strip()
            if not cmd:
                continue

            response = stub.SendCommand(chat_pb2.CommandRequest(username=username, command=cmd))
            message = response.message

            if "error" in message.lower() or "invalid" in message.lower() or "❌" in message:
                print_error(message)
            else:
                print(message)

            if cmd == "logout":
                break

    log_file.close()

if __name__ == "__main__":
    main()
