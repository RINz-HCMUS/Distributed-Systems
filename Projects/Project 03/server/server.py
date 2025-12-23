import socket
import threading
import time
import random
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from common.constants import *
from common.protocol import send_msg
from common.logger import Logger
from server.map_manager import MapManager
from server.user_manager import UserManager
from server.client_handler import ClientHandler


class GameServer:
    def __init__(self):
        Logger.setup("server")

        self.players = {}
        self.clients = {}
        self.bullets = []
        self.events = []

        self.next_pid = 1
        self.running = True

        self.map_mgr = MapManager()
        self.user_mgr = UserManager()

        self.server_sock = None

    # =================================================
    # START / STOP
    # =================================================

    def start(self):
        print(f"[SERVER] Starting server on {HOST}:{PORT}...")
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((HOST, PORT))
        self.server_sock.listen()

        print(f"[SERVER] Server started and listening for connections.")

        threading.Thread(target=self._game_loop, daemon=True).start()

        try:
            while self.running:
                sock, addr = self.server_sock.accept()
                ClientHandler(sock, addr, self).start()
        finally:
            self.shutdown()

    def shutdown(self):
        print("[SERVER] Shutting down server...")
        self.running = False
        for sock in self.clients.values():
            try:
                sock.close()
            except:
                pass
        if self.server_sock:
            self.server_sock.close()

    # =================================================
    # PLAYER MANAGEMENT
    # =================================================

    def add_player(self, username, sock):
        pid = self.next_pid
        self.next_pid += 1

        x, y = self._find_safe_spawn()

        self.players[pid] = {
            "id": pid,
            "username": username,
            "x": x,
            "y": y,
            "dir": random.choice(["UP", "DOWN", "LEFT", "RIGHT"]),
            "score": 0,
            "total_score": self.user_mgr.get_total_score(username)
        }

        self.clients[pid] = sock
        self._add_event(f"{username} joined the match")

        # SEND MAP ONCE
        send_msg(sock, {
            "type": "MAP_DATA",
            "payload": self.map_mgr.export_map()
        })
        print(f"[SERVER] Player '{username}' (ID: {pid}) connected.")
        return pid

    def remove_player(self, pid):
        if pid in self.players:
            self._add_event(f"{self.players[pid]['username']} left the match")
            del self.players[pid]
        if pid in self.clients:
            del self.clients[pid]

        print(f"[SERVER] Player ID: {pid} disconnected.")
        
    # =================================================
    # COLLISION HELPERS
    # =================================================

    def _cell_occupied(self, cx, cy, ignore_pid=None):
        for pid, p in self.players.items():
            if pid == ignore_pid:
                continue
            px = int(p["x"] // CELL_SIZE)
            py = int(p["y"] // CELL_SIZE)
            if px == cx and py == cy:
                return True
        return False

    # =================================================
    # ACTIONS
    # =================================================

    def handle_move(self, pid, direction):
        if pid not in self.players:
            return

        p = self.players[pid]
        p["dir"] = direction

        dx = dy = 0
        if direction == "UP":
            dy = -PLAYER_SPEED
        elif direction == "DOWN":
            dy = PLAYER_SPEED
        elif direction == "LEFT":
            dx = -PLAYER_SPEED
        elif direction == "RIGHT":
            dx = PLAYER_SPEED

        nx = p["x"] + dx
        ny = p["y"] + dy

        cx = int(nx // CELL_SIZE)
        cy = int(ny // CELL_SIZE)

        if self.map_mgr.is_wall_cell(cx, cy):
            return

        if self._cell_occupied(cx, cy, ignore_pid=pid):
            return

        p["x"] = nx
        p["y"] = ny

    def handle_shoot(self, pid):
        if pid not in self.players:
            return

        p = self.players[pid]
        active = sum(1 for b in self.bullets if b["owner"] == pid)
        if active >= MAX_BULLETS_PER_PLAYER:
            return

        self.bullets.append({
            "owner": pid,
            "x": p["x"],
            "y": p["y"],
            "dir": p["dir"],
            "travel": 0
        })

        p["score"] -= 1

    # =================================================
    # GAME LOOP
    # =================================================

    def _game_loop(self):
        while self.running:
            time.sleep(1 / FPS)
            self._update_bullets()
            self._broadcast_state()

    # =================================================
    # BULLETS
    # =================================================

    def _update_bullets(self):
        alive = []
        for b in self.bullets:
            if b["dir"] == "UP":
                b["y"] -= BULLET_SPEED
            elif b["dir"] == "DOWN":
                b["y"] += BULLET_SPEED
            elif b["dir"] == "LEFT":
                b["x"] -= BULLET_SPEED
            elif b["dir"] == "RIGHT":
                b["x"] += BULLET_SPEED

            b["travel"] += BULLET_SPEED

            if b["travel"] > MAX_BULLET_RANGE:
                continue
            if self.map_mgr.is_collision(b["x"], b["y"]):
                continue
            if self._check_hit(b):
                continue

            alive.append(b)

        self.bullets = alive

    def _check_hit(self, bullet):
        for pid, p in self.players.items():
            if pid == bullet["owner"]:
                continue

            if abs(p["x"] - bullet["x"]) < TANK_SIZE and \
               abs(p["y"] - bullet["y"]) < TANK_SIZE:
                self._kill_player(pid, bullet["owner"])
                return True
        return False

    # =================================================
    # KILL + INSTANT RESPAWN
    # =================================================

    def _kill_player(self, victim_id, killer_id):
        victim = self.players[victim_id]
        killer = self.players[killer_id]

        victim["score"] -= 5
        killer["score"] += 11

        self.user_mgr.add_score(victim["username"], -5)
        self.user_mgr.add_score(killer["username"], +11)

        self._add_event(
            f"{killer['username']} killed {victim['username']}"
        )

        pos = self._find_safe_spawn()
        if pos:
            victim["x"], victim["y"] = pos
            victim["dir"] = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

    # =================================================
    # SPAWN
    # =================================================

    def _find_safe_spawn(self):
        for _ in range(100):
            cx = random.randint(1, COLS - 2)
            cy = random.randint(1, ROWS - 2)

            if self.map_mgr.is_wall_cell(cx, cy):
                continue
            if self._cell_occupied(cx, cy):
                continue

            return cx * CELL_SIZE, cy * CELL_SIZE
        return 0, 0

    # =================================================
    # BROADCAST
    # =================================================

    def _broadcast_state(self):
        msg = {
            "type": "GAME_UPDATE",
            "payload": {
                "players": self.players,
                "bullets": self.bullets,
                "events": self.events[-10:]
            }
        }

        dead = []
        for pid, sock in self.clients.items():
            try:
                send_msg(sock, msg)
            except:
                dead.append(pid)

        for pid in dead:
            self.remove_player(pid)

    def _add_event(self, text):
        self.events.append({"time": time.time(), "text": text})
        if len(self.events) > 50:
            self.events.pop(0)


if __name__ == "__main__":
    GameServer().start()
