import pygame
from common.constants import *

# =========================
# SIMPLE UI COMPONENTS
# =========================

def draw_box(screen, rect, color, radius=8):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=radius)

class InputBox:
    def __init__(self, x, y, w, h, placeholder="", password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.password = password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB,
                                   pygame.K_LSHIFT, pygame.K_RSHIFT):
                if event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, screen, font):
        color = (70, 70, 90) if self.active else (60, 60, 60)
        draw_box(screen, self.rect, color)

        display = (
            "*" * len(self.text) if self.password else self.text
        ) or self.placeholder

        txt_color = WHITE if self.text else GRAY
        txt = font.render(display, True, txt_color)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
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
# LOGIN UI
# =========================

class LoginUI:
    def __init__(self, screen, client):
        self.screen = screen
        self.client = client

        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small = pygame.font.SysFont("Arial", 16)

        self._build_layout()
        self.username.active = True

    # -------------------------------------------------

    def _build_layout(self):
        w, h = self.screen.get_size()
        cx = w // 2 - 150

        self.username = InputBox(cx, int(h * 0.40), 300, 45, "Username")
        self.password = InputBox(cx, int(h * 0.48), 300, 45, "Password", password=True)

        self.btn_login = Button(cx, int(h * 0.58), 140, 45, "Đăng nhập")
        self.btn_register = Button(cx + 160, int(h * 0.58), 140, 45, "Đăng ký")

    # -------------------------------------------------

    def handle_event(self, event):
        self.username.handle_event(event)
        self.password.handle_event(event)

        if event.type == pygame.KEYDOWN:

            # TAB: đổi ô
            if event.key == pygame.K_TAB:
                self.username.active = not self.username.active
                self.password.active = not self.password.active

            # SHIFT: đăng ký
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.client.register(
                    self.username.text,
                    self.password.text
                )

            # ENTER: đăng nhập
            elif event.key == pygame.K_RETURN:
                self.client.login(
                    self.username.text,
                    self.password.text
                )

        # Mouse click
        if self.btn_login.clicked(event):
            self.client.login(
                self.username.text,
                self.password.text
            )

        if self.btn_register.clicked(event):
            self.client.register(
                self.username.text,
                self.password.text
            )

    # -------------------------------------------------

    def draw(self):
        self.screen.fill((25, 25, 35))

        w, h = self.screen.get_size()

        title = self.font.render("MAZE BATTLE", True, WHITE)
        self.screen.blit(
            title,
            title.get_rect(center=(w // 2, int(h * 0.25)))
        )

        self.username.draw(self.screen, self.small)
        self.password.draw(self.screen, self.small)

        self.btn_login.draw(self.screen, self.small)
        self.btn_register.draw(self.screen, self.small)

        if self.client.auth_message:
            color = RED if self.client.auth_error else GREEN
            msg = self.small.render(self.client.auth_message, True, color)
            self.screen.blit(
                msg,
                msg.get_rect(center=(w // 2, int(h * 0.70)))
            )
