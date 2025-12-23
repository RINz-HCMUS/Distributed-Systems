import pygame
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from common.constants import *

PANEL_BG = (28, 28, 40)
PANEL_BORDER = (90, 90, 120)
TEXT = (230, 230, 230)
SUBTEXT = (180, 180, 180)
HIGHLIGHT = (255, 220, 120)

TANK_SCALE = 0.75
BARREL_SCALE = 0.45
BULLET_SCALE = 0.5
BARREL_PUSH = 0.30


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 14)
        self.small = pygame.font.SysFont("Arial", 12)

        self.floor = pygame.image.load("client/assets/map_floor.png").convert()
        self.wall = pygame.image.load("client/assets/map_wall.png").convert()

        self._load_assets()

    # =========================================================
    # ASSETS
    # =========================================================

    def _load_assets(self):
        tank_self = pygame.image.load("client/assets/tank_body_self.png").convert_alpha()
        tank_enemy = pygame.image.load("client/assets/tank_body_enemy.png").convert_alpha()
        barrel_self = pygame.image.load("client/assets/tank_barrel_self.png").convert_alpha()
        barrel_enemy = pygame.image.load("client/assets/tank_barrel_enemy.png").convert_alpha()
        bullet_self = pygame.image.load("client/assets/bullet_self.png").convert_alpha()
        bullet_enemy = pygame.image.load("client/assets/bullet_enemy.png").convert_alpha()

        ts = int(TANK_SIZE * TANK_SCALE)
        self.tank_self = pygame.transform.smoothscale(tank_self, (ts, ts))
        self.tank_enemy = pygame.transform.smoothscale(tank_enemy, (ts, ts))

        bw = int(barrel_self.get_width() * BARREL_SCALE)
        bh = int(barrel_self.get_height() * BARREL_SCALE)
        self.barrel_self = pygame.transform.smoothscale(barrel_self, (bw, bh))
        self.barrel_enemy = pygame.transform.smoothscale(barrel_enemy, (bw, bh))

        buw = int(bullet_self.get_width() * BULLET_SCALE)
        buh = int(bullet_self.get_height() * BULLET_SCALE)
        self.bullet_self = pygame.transform.smoothscale(bullet_self, (buw, buh))
        self.bullet_enemy = pygame.transform.smoothscale(bullet_enemy, (buw, buh))

        self.tank_half = TANK_SIZE // 2
        self.bullet_half = buh // 2
        self.barrel_push = int(self.tank_half * BARREL_PUSH)

    # =========================================================
    # LAYOUT
    # =========================================================

    def compute_layout(self):
        w, h = self.screen.get_size()

        left_w = int(w * SCOREBOARD_RATIO)
        right_w = w - left_w

        map_h = int(h * MAP_HEIGHT_RATIO)
        bottom_h = h - map_h

        self.rect_scoreboard = pygame.Rect(0, 0, left_w, h)

        self.rect_map = pygame.Rect(left_w, 0, right_w, map_h)

        info_w = int(right_w * INFO_RATIO)
        event_w = right_w - info_w

        self.rect_info = pygame.Rect(left_w, map_h, info_w, bottom_h)
        self.rect_event = pygame.Rect(left_w + info_w, map_h, event_w, bottom_h)

    # =========================================================

    def draw_game(self, client):
        self.compute_layout()
        self.draw_scoreboard(client)
        self.draw_map(client)
        self.draw_info(client)
        self.draw_event_log(client)

    # =========================================================
    # MAP
    # =========================================================

    def draw_map(self, client):
        ox, oy = self.rect_map.topleft
        grid = client.map["grid"]

        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                px = ox + x * CELL_SIZE
                py = oy + y * CELL_SIZE
                self.screen.blit(self.floor, (px, py))
                if ch == "#":
                    self.screen.blit(self.wall, (px, py))

        for pid, p in client.players.items():
            self.draw_tank(p, pid == str(client.my_id), ox, oy)

        for b in client.bullets:
            self.draw_bullet(b, b["owner"] == client.my_id, ox, oy)

    # =========================================================

    def draw_tank(self, p, is_self, ox, oy):
        body = self.tank_self if is_self else self.tank_enemy
        barrel = self.barrel_self if is_self else self.barrel_enemy

        cx = ox + int(p["x"])
        cy = oy + int(p["y"])
        self.screen.blit(body, body.get_rect(center=(cx, cy)))

        if p["dir"] == "UP":
            angle, off = 0, (0, -self.barrel_push)
        elif p["dir"] == "DOWN":
            angle, off = 180, (0, self.barrel_push)
        elif p["dir"] == "LEFT":
            angle, off = 90, (-self.barrel_push, 0)
        else:
            angle, off = -90, (self.barrel_push, 0)

        rot = pygame.transform.rotate(barrel, angle)
        self.screen.blit(rot, rot.get_rect(center=(cx + off[0], cy + off[1])))

    def draw_bullet(self, b, is_self, ox, oy):
        img = self.bullet_self if is_self else self.bullet_enemy

        if b["dir"] == "UP":
            off = (0, -self.tank_half - self.bullet_half)
        elif b["dir"] == "DOWN":
            off = (0, self.tank_half + self.bullet_half)
        elif b["dir"] == "LEFT":
            off = (-self.tank_half - self.bullet_half, 0)
        else:
            off = (self.tank_half + self.bullet_half, 0)

        cx = ox + int(b["x"]) + off[0]
        cy = oy + int(b["y"]) + off[1]
        self.screen.blit(img, img.get_rect(center=(cx, cy)))

    # =========================================================
    # SCOREBOARD
    # =========================================================

    def draw_scoreboard(self, client):
        pygame.draw.rect(self.screen, PANEL_BG, self.rect_scoreboard)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.rect_scoreboard, 2)

        x = self.rect_scoreboard.x + PADDING
        y = self.rect_scoreboard.y + PADDING
        self.screen.blit(self.font.render("Scoreboard (Top 25)", True, TEXT), (x, y))
        y += 26

        players = sorted(client.players.values(), key=lambda p: p["score"], reverse=True)
        my_rank = None

        for i, p in enumerate(players[:SCOREBOARD_LIMIT]):
            if p["id"] == client.my_id:
                my_rank = i + 1
                color = HIGHLIGHT
            else:
                color = SUBTEXT
            txt = f"{i+1:>2}. {p['username']} ({p['score']})"
            self.screen.blit(self.small.render(txt, True, color), (x, y))
            y += 18

        if my_rank is None:
            for i, p in enumerate(players):
                if p["id"] == client.my_id:
                    my_rank = i + 1
                    break

        y = self.rect_scoreboard.bottom - 22
        rank_txt = f"Your rank: {my_rank if my_rank <= SCOREBOARD_LIMIT else '25+'}"
        self.screen.blit(self.small.render(rank_txt, True, HIGHLIGHT), (x, y))

    # =========================================================
    # INFO
    # =========================================================

    def draw_info(self, client):
        pygame.draw.rect(self.screen, PANEL_BG, self.rect_info)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.rect_info, 2)

        x = self.rect_info.x + PADDING
        y = self.rect_info.y + PADDING
        self.screen.blit(self.font.render("Info", True, TEXT), (x, y))
        y += 26

        me = client.players.get(str(client.my_id))
        if not me:
            return

        for line in [
            f"Name: {me['username']}",
            f"Score: {me['score']}",
        ]:
            self.screen.blit(self.small.render(line, True, SUBTEXT), (x, y))
            y += 18

    # =========================================================
    # EVENT LOG
    # =========================================================

    def draw_event_log(self, client):
        pygame.draw.rect(self.screen, PANEL_BG, self.rect_event)
        pygame.draw.rect(self.screen, PANEL_BORDER, self.rect_event, 2)

        x = self.rect_event.x + PADDING
        y = self.rect_event.y + PADDING
        self.screen.blit(self.font.render("Event Log", True, TEXT), (x, y))
        y += 26

        for e in client.events[:EVENT_LOG_LINES]:
            self.screen.blit(self.small.render(e["text"], True, SUBTEXT), (x, y))
            y += 18
