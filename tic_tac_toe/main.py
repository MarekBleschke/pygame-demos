import pygame

from tic_tac_toe.game_manager import GameManager
from tic_tac_toe.constans import SCREEN_SIZE, BACKGROUND_COLOR

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

game_manager = GameManager(main_screen=screen)
game_manager.init_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            game_manager.handle_click(pygame.mouse.get_pos())

    screen.fill(BACKGROUND_COLOR)
    game_manager.draw()

    pygame.display.flip()

    clock.tick(60)
