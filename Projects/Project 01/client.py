# ===============================================
# 🧩 CLIENT.PY — HOÀN TOÀN TẮT CẢNH BÁO GRPC/ABSL
# ===============================================

import os, sys, logging

# --- GHI WARNING GRPC / ABSEIL RA FILE LOG ---
log_path = "logs/grpc_warnings.log"
# kiểm tra và tạo thư mục logs nếu chưa tồn tại
if not os.path.exists("logs"):
    os.makedirs("logs")
log_file = open(log_path, "w", encoding="utf-8")
sys.stderr = log_file  # redirect toàn bộ stderr

# --- NGĂN ABSL/GRPC GHI RA MÀN HÌNH ---
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""
logging.getLogger().setLevel(logging.ERROR)

# === PHẢI ĐẶT SAU KHI TẮT LOGGING MỚI IMPORT GRPC ===
import grpc
import threading
from colorama import Fore, Style, init
import chat_pb2, chat_pb2_grpc

# --- BẬT ANSI COLOR CHO WINDOWS ---
os.system("")
init(autoreset=True, convert=True)



# ==== TÔ MÀU ====

def print_user(name, me):
    """In tên user: xanh lá nếu là mình, xanh dương nếu là người khác."""
    if name == me:
        print(Fore.GREEN + name + Style.RESET_ALL, end="")
    else:
        print(Fore.CYAN + name + Style.RESET_ALL, end="")

def print_group(name):
    """In tên group màu vàng."""
    print(Fore.YELLOW + name + Style.RESET_ALL, end="")

def print_system(msg):
    """In thông báo hệ thống màu tím."""
    print(Fore.MAGENTA + msg + Style.RESET_ALL)

def print_error(msg):
    """In lỗi màu đỏ nguyên dòng."""
    print(Fore.RED + msg + Style.RESET_ALL)


# ==== LUỒNG NGHE TIN NHẮN ====

def listen_for_messages(stub, username):
    responses = stub.StreamMessages(chat_pb2.ConnectRequest(username=username))
    try:
        for msg in responses:
            ts = msg.timestamp
            sender = msg.sender
            group = msg.group
            text = msg.msg

            print()  # Xuống dòng cho đẹp

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

            # In lại prompt
            print(">> ", end="", flush=True)

    except grpc.RpcError:
        pass


# ==== HÀM CHÍNH ====

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

    # 🔚 Đóng file log khi thoát
    log_file.close()


if __name__ == "__main__":
    main()
# ===============================================
# 🛠 CLIENT.PY — GHI WARNING GRPC RA FILE LOG RIÊNG
# ===============================================

import os, sys

# ⚙️ GHI WARNING GRPC / ABSEIL VÀO FILE LOG
log_file = open("grpc_warnings.log", "w", encoding="utf-8")
sys.stderr = log_file  # Chuyển toàn bộ stderr sang file log trước khi import grpc

import grpc
import threading
from colorama import Fore, Style, init
import chat_pb2, chat_pb2_grpc


# --- BẬT ANSI COLOR CHO WINDOWS ---
os.system("")  # Bật hỗ trợ màu trong CMD/PowerShell
init(autoreset=True, convert=True)


# ==== TÔ MÀU ====

def print_user(name, me):
    """In tên user: xanh lá nếu là mình, xanh dương nếu là người khác."""
    if name == me:
        print(Fore.GREEN + name + Style.RESET_ALL, end="")
    else:
        print(Fore.CYAN + name + Style.RESET_ALL, end="")

def print_group(name):
    """In tên group màu vàng."""
    print(Fore.YELLOW + name + Style.RESET_ALL, end="")

def print_system(msg):
    """In thông báo hệ thống màu tím."""
    print(Fore.MAGENTA + msg + Style.RESET_ALL)

def print_error(msg):
    """In lỗi màu đỏ nguyên dòng."""
    print(Fore.RED + msg + Style.RESET_ALL)


# ==== LUỒNG NGHE TIN NHẮN ====

def listen_for_messages(stub, username):
    responses = stub.StreamMessages(chat_pb2.ConnectRequest(username=username))
    try:
        for msg in responses:
            ts = msg.timestamp
            sender = msg.sender
            group = msg.group
            text = msg.msg

            print()  # Xuống dòng cho đẹp

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

            # In lại prompt
            print(">> ", end="", flush=True)

    except grpc.RpcError:
        pass


# ==== HÀM CHÍNH ====

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

    # 🔚 Đóng file log khi thoát
    log_file.close()


if __name__ == "__main__":
    main()
