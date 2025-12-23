import pygame
from common.constants import *

class RankingUI:
    def __init__(self, screen, client):
        self.screen = screen
        self.client = client
        self.font = pygame.font.SysFont("Arial", 18)
        self.small = pygame.font.SysFont("Arial", 14)
        self.client.request_ranking()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "BACK"
        return None

    def draw(self):
        self.screen.fill((15, 15, 30))
        self.screen.blit(self.font.render("RANKING - TOP 25", True, WHITE),
                         (DESIGN_WIDTH//2 - 100, 30))

        y = 80
        for r in self.client.ranking_top:
            line = f"{r['rank']:>2}. {r['username']:<15} {r['score']:>6}"
            self.screen.blit(self.small.render(line, True, WHITE),
                             (DESIGN_WIDTH//2 - 150, y))
            y += 18

        y += 20
        rank = "TOP25+" if self.client.my_rank and self.client.my_rank > 25 else self.client.my_rank
        self.screen.blit(
            self.small.render(f"Your rank: {rank}", True, GREEN),
            (DESIGN_WIDTH//2 - 150, y)
        )
        self.screen.blit(
            self.small.render(f"Your total score: {self.client.my_score}", True, GREEN),
            (DESIGN_WIDTH//2 - 150, y + 20)
        )

        self.screen.blit(
            self.small.render("ESC - Back", True, GRAY),
            (20, DESIGN_HEIGHT - 30)
        )
