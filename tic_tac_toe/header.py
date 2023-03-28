import pygame.font

from tic_tac_toe.player import Player


class Header:
    font: pygame.font.Font
    font_color: pygame.Color
    main_screen: pygame.Surface
    text: pygame.Surface

    def __init__(self, main_screen: pygame.Surface, font: pygame.font.Font, font_color: pygame.Color):
        self.main_screen = main_screen
        self.font = font
        self.font_color = font_color

    def draw(self) -> None:
        text_pos = self.text.get_rect(centerx=600 / 2, y=40)
        self.main_screen.blit(self.text, text_pos)

    def text_current_player(self, player: Player) -> None:
        self.text = self.font.render(f"Current player: {player.name}", True, self.font_color)

    def text_winning_player(self, player: Player) -> None:
        self.text = self.font.render(f"{player.name} has won", True, self.font_color)

    def text_draw(self) -> None:
        self.text = self.font.render("DRAW", True, self.font_color)
