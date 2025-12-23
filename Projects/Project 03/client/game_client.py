import socket
import threading
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from common.protocol import send_msg, recv_msg
from common.constants import *

class GameClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.my_id = None
        self.username = None
        self.logged_in = False

        # -------- GAME STATE --------
        self.players = {}
        self.bullets = []
        self.events = []

        # -------- MAP (FROM SERVER) --------
        self.map = None

        # -------- AUTH --------
        self.auth_message = ""
        self.auth_error = False

        # -------- RANKING --------
        self.ranking_top = []
        self.my_rank = None
        self.my_score = None

    def connect(self):
        self.sock.connect((HOST, PORT))
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        while True:
            msg = recv_msg(self.sock)
            if not msg:
                break

            t = msg.get("type")
            payload = msg.get("payload", {})

            if t == "LOGIN_RESULT":
                if payload.get("status") == "success":
                    self.my_id = payload["player_id"]
                    self.logged_in = True
                    self.auth_message = "Đăng nhập thành công"
                    self.auth_error = False
                else:
                    self.auth_message = self._map_reason(payload.get("reason"))
                    self.auth_error = True

            elif t == "REGISTER_RESULT":
                if payload.get("status") == "success":
                    self.auth_message = "Đăng ký thành công! Hãy đăng nhập"
                    self.auth_error = False
                else:
                    self.auth_message = self._map_reason(payload.get("reason"))
                    self.auth_error = True

            elif t == "MAP_DATA":
                self.map = payload

            elif t == "GAME_UPDATE":
                self.players = payload.get("players", {})
                self.bullets = payload.get("bullets", [])
                self.events = payload.get("events", [])

            elif t == "RANKING_RESULT":
                self.ranking_top = payload.get("top", [])
                self.my_rank = payload.get("my_rank")
                self.my_score = payload.get("my_score")

    def _map_reason(self, reason):
        return {
            "user_not_found": "Tài khoản không tồn tại",
            "wrong_password": "Sai mật khẩu",
            "user_exists": "Tài khoản đã tồn tại"
        }.get(reason, "Lỗi không xác định")

    # -------- REQUESTS --------

    def login(self, u, p):
        self.username = u
        send_msg(self.sock, {
            "action": "LOGIN",
            "username": u,
            "password": p
        })

    def register(self, u, p):
        send_msg(self.sock, {
            "action": "REGISTER",
            "username": u,
            "password": p
        })

    def request_ranking(self):
        send_msg(self.sock, {"action": "GET_RANKING"})

    def move(self, d):
        send_msg(self.sock, {"action": "MOVE", "direction": d})

    def shoot(self):
        send_msg(self.sock, {"action": "SHOOT"})
