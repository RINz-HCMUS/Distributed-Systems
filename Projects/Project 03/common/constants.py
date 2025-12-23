import os

# =========================
# NETWORK
# =========================
HOST = "127.0.0.1"
PORT = 5555
HEADER_SIZE = 4
BUF_SIZE = 4096
FORMAT = "utf-8"

# =========================
# GAME LOOP
# =========================
FPS = 60
TITLE = "Maze Battle Multiplayer"

# =========================
# MAP CONFIG
# =========================
CELL_SIZE = 40
COLS = 32
ROWS = 16

MAP_WIDTH = COLS * CELL_SIZE
MAP_HEIGHT = ROWS * CELL_SIZE

# =========================
# PLAYER
# =========================
TANK_SIZE = CELL_SIZE
PLAYER_SPEED = 4
MAX_BULLETS_PER_PLAYER = 4
RESPAWN_DELAY = 3.0

# =========================
# BULLET
# =========================
BULLET_SPEED = PLAYER_SPEED * 4
BULLET_SIZE = 8
MAX_BULLET_RANGE = max(COLS, ROWS) * CELL_SIZE

# =========================
# UI LAYOUT 
# =========================
SCOREBOARD_RATIO = 0.22    
RIGHT_PANEL_RATIO = 0.78   

MAP_HEIGHT_RATIO = 0.72    
BOTTOM_HEIGHT_RATIO = 0.28  

INFO_RATIO = 0.40
EVENT_RATIO = 0.60

EVENT_LOG_LINES = 6
SCOREBOARD_LIMIT = 25

PADDING = 10

# =========================
# COLORS
# =========================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# =========================
# LOGGING
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
