import pygame
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from common.constants import *
from client.game_client import GameClient
from client.ui_login import LoginUI
from client.ui_menu import MenuUI
from client.ui_manager import UIManager
from client.ui_settings import SettingsUI

# ==================================================
# INIT
# ==================================================
pygame.init()

# ---- WINDOW SIZE (KHÔNG DÙNG DESIGN_WIDTH NỮA) ----
INIT_WIDTH = int(MAP_WIDTH * 1.35)
INIT_HEIGHT = int(MAP_HEIGHT * 1.30)

screen = pygame.display.set_mode(
    (INIT_WIDTH, INIT_HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

client = GameClient()
client.connect()

login_ui = LoginUI(screen, client)
menu_ui = MenuUI(screen)
game_ui = UIManager(screen)
settings_ui = None

# ==================================================
# STATE
# ==================================================
STATE = "LOGIN"
running = True

# ==================================================
# INPUT
# ==================================================
KEY_BIND = {
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "SHOOT": pygame.K_SPACE,
}

key_state = {
    "UP": False,
    "DOWN": False,
    "LEFT": False,
    "RIGHT": False,
}

# ==================================================
# MAIN LOOP
# ==================================================
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---------------- LOGIN ----------------
        if STATE == "LOGIN":
            login_ui.handle_event(event)

        # ---------------- MENU ----------------
        elif STATE == "MENU":
            action = menu_ui.handle_event(event)
            if action == "PLAY":
                STATE = "GAME"

        # ---------------- GAME ----------------
        elif STATE == "GAME":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_ui = SettingsUI(screen, KEY_BIND)
                    STATE = "SETTINGS"

                for k, key in KEY_BIND.items():
                    if event.key == key:
                        if k == "SHOOT":
                            client.shoot()
                        elif k in key_state:
                            key_state[k] = True

            elif event.type == pygame.KEYUP:
                for k, key in KEY_BIND.items():
                    if event.key == key and k in key_state:
                        key_state[k] = False

        # ---------------- SETTINGS ----------------
        elif STATE == "SETTINGS":
            if settings_ui.handle_event(event) == "BACK":
                STATE = "GAME"

    # -------- CONTINUOUS MOVE --------
    if STATE == "GAME":
        for k, pressed in key_state.items():
            if pressed:
                client.move(k)

    # ==================================================
    # DRAW
    # ==================================================
    screen.fill((15, 15, 25))

    if STATE == "LOGIN":
        login_ui.draw()
        if client.logged_in:
            STATE = "MENU"

    elif STATE == "MENU":
        menu_ui.draw()

    elif STATE == "GAME":
        game_ui.draw_game(client)

    elif STATE == "SETTINGS":
        settings_ui.draw()

    pygame.display.flip()
    clock.tick(FPS)

# ==================================================
# CLEAN EXIT
# ==================================================
pygame.quit()
sys.exit()
