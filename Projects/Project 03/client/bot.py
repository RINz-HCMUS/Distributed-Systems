import sys
import os
import time
import random
import threading

# =====================================================
# THÊM ĐƯỜNG DẪN ĐỂ IMPORT ĐƯỢC MODULE
# =====================================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from client.game_client import GameClient
from common.constants import *

class AutoBot:
    def __init__(self, bot_name):
        self.client = GameClient()
        self.name = bot_name
        self.password = "123456"
        self.running = True
        
        # Trạng thái di chuyển của Bot
        self.current_dir = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.last_dir_change = time.time()
        self.change_interval = random.uniform(0.5, 2.0) # Đổi hướng mỗi 0.5 - 2 giây

    def start(self):
        print(f"[{self.name}] Connecting to server...")
        try:
            self.client.connect()
        except Exception as e:
            print(f"[{self.name}] Connection failed: {e}")
            return

        # --- AUTO REGISTER & LOGIN ---
        # Thử đăng ký trước (nếu chưa có tk), sau đó đăng nhập
        print(f"[{self.name}] Registering/Logging in...")
        self.client.register(self.name, self.password)
        time.sleep(0.5) # Đợi server xử lý đăng ký
        
        self.client.login(self.name, self.password)
        time.sleep(0.5) # Đợi server xử lý đăng nhập

        if not self.client.logged_in:
            print(f"[{self.name}] Login failed! Reason: {self.client.auth_message}")
            return
        
        print(f"[{self.name}] Ready to fight!")
        self._bot_loop()

    def _bot_loop(self):
        # Giả lập vòng lặp game (60 FPS)
        while self.running:
            time.sleep(1 / FPS) 

            # 1. Logic Di Chuyển (Movement)
            # Bot sẽ giữ một hướng đi trong khoảng thời gian ngẫu nhiên, sau đó đổi hướng
            now = time.time()
            if now - self.last_dir_change > self.change_interval:
                # Chọn hướng mới ngẫu nhiên
                self.current_dir = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
                
                # Reset bộ đếm thời gian
                self.last_dir_change = now
                self.change_interval = random.uniform(0.5, 1.5)
            
            # Gửi lệnh di chuyển liên tục (giống như người chơi giữ phím)
            self.client.move(self.current_dir)

            # 2. Logic Bắn Súng (Shooting)
            # Xác suất bắn mỗi khung hình (khoảng 2% mỗi frame ~ 1-2 viên/giây)
            if random.random() < 0.02:
                self.client.shoot()

if __name__ == "__main__":
    # Tạo số lượng bot tùy thích bằng tham số dòng lệnh
    # Ví dụ chạy: python client/bot.py 3 (sẽ tạo 3 bot)
    
    num_bots = 1
    if len(sys.argv) > 1:
        try:
            num_bots = int(sys.argv[1])
        except:
            pass

    threads = []
    print(f"--- LAUNCHING {num_bots} BOTS ---")

    for i in range(num_bots):
        # Đặt tên Bot ngẫu nhiên: Bot_123, Bot_999...
        bot_name = f"Bot_{random.randint(1000, 9999)}"
        bot = AutoBot(bot_name)
        
        # Chạy mỗi bot trên 1 luồng riêng để không chặn nhau
        t = threading.Thread(target=bot.start, daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.2) # Delay nhẹ để không spam server lúc connect

    # Giữ chương trình chính chạy để các luồng bot hoạt động
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping bots...")