import pygame
from common.constants import *

class SettingsUI:
    def __init__(self, screen, keymap):
        self.screen = screen
        self.keymap = keymap
        self.font = pygame.font.SysFont("Arial", 20)
        self.small = pygame.font.SysFont("Arial", 14)

        self.actions = list(keymap.keys())
        self.selected = 0
        self.waiting = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.waiting:
                self.keymap[self.actions[self.selected]] = event.key
                self.waiting = False
            else:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.actions)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.actions)
                elif event.key == pygame.K_RETURN:
                    self.waiting = True
                elif event.key == pygame.K_ESCAPE:
                    return "BACK"
        return None

    def draw(self):
        self.screen.fill((20, 20, 20))
        self.screen.blit(self.font.render("SETTINGS", True, WHITE),
                         (DESIGN_WIDTH//2 - 60, 50))

        y = 120
        for i, act in enumerate(self.actions):
            color = GREEN if i == self.selected else WHITE
            key_name = pygame.key.name(self.keymap[act])
            self.screen.blit(
                self.font.render(f"{act:<8}: {key_name}", True, color),
                (DESIGN_WIDTH//2 - 150, y)
            )
            y += 35

        hint = "Press key..." if self.waiting else "ENTER=Change | ESC=Back"
        self.screen.blit(self.small.render(hint, True, GRAY),
                         (DESIGN_WIDTH//2 - 120, y + 10))
