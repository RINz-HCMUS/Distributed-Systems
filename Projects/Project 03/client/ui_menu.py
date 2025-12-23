import pygame
from common.constants import *

# =========================
# SIMPLE UI COMPONENTS
# =========================

def draw_box(screen, rect, color, radius=8):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=radius)

class Button:
    def __init__(self, rect, text):
        self.rect = rect
        self.text = text

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, screen, font):
        draw_box(screen, self.rect, (80, 80, 120))
        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

# =========================
# MENU UI
# =========================

class MenuUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 26, bold=True)
        self.small = pygame.font.SysFont("Arial", 14)

        self._build_layout()

    # -------------------------------------------------

    def _build_layout(self):
        w, h = self.screen.get_size()
        cx = w // 2
        cy = h // 2

        bw, bh = 260, 50
        gap = 14

        self.buttons = {
            "PLAY": Button(
                pygame.Rect(cx - bw // 2, cy - bh * 2 - gap, bw, bh),
                "PLAY"
            ),
            "RANKING": Button(
                pygame.Rect(cx - bw // 2, cy - bh - gap, bw, bh),
                "RANKING"
            ),
            "SETTINGS": Button(
                pygame.Rect(cx - bw // 2, cy, bw, bh),
                "SETTINGS"
            ),
            "INFO": Button(
                pygame.Rect(cx - bw // 2, cy + bh + gap, bw, bh),
                "INFO"
            ),
            "QUIT": Button(
                pygame.Rect(cx - bw // 2, cy + bh * 2 + gap, bw, bh),
                "QUIT"
            ),
        }

    # -------------------------------------------------

    def handle_event(self, event):
        # ENTER = PLAY
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "PLAY"
            if event.key == pygame.K_ESCAPE:
                return "QUIT"

        # Mouse
        for name, btn in self.buttons.items():
            if btn.clicked(event):
                return name

        return None

    # -------------------------------------------------

    def draw(self):
        self.screen.fill((20, 20, 30))

        w, h = self.screen.get_size()

        # Title
        title = self.font.render("MAIN MENU", True, WHITE)
        self.screen.blit(
            title,
            title.get_rect(center=(w // 2, int(h * 0.25)))
        )

        # Buttons
        for btn in self.buttons.values():
            btn.draw(self.screen, self.font)

        # Hint
        hint = self.small.render(
            "ENTER: Play   |   ESC: Quit", True, GRAY
        )
        self.screen.blit(
            hint,
            hint.get_rect(center=(w // 2, int(h * 0.80)))
        )
