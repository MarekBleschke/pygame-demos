import pygame

from tic_tac_toe.board_display import BoardDisplay
from tic_tac_toe.constans import FONT_HEADER, FONT_HEADER_COLOR, BACKGROUND_COLOR, BOARD_LINE_COLOR
from tic_tac_toe.board_logic import BoardLogic, BoardState, BoardLogicTile
from tic_tac_toe.header import Header
from tic_tac_toe.player import Player


class GameManager:
    """
    Handle game state and other game modules.
    """

    main_screen: pygame.Surface
    board_logic: BoardLogic
    board_display: BoardDisplay
    header: Header
    players: tuple[Player, Player]

    _current_player_index: int = 0

    def __init__(self, main_screen: pygame.Surface):
        self.main_screen = main_screen

    def init_game(self) -> None:
        self.board_logic = BoardLogic(board_size=3)
        self.board_display = BoardDisplay(
            main_screen=self.main_screen, board_size=3, background_color=BACKGROUND_COLOR, line_color=BOARD_LINE_COLOR
        )
        self.header = Header(main_screen=self.main_screen, font=FONT_HEADER, font_color=FONT_HEADER_COLOR)
        self.players = (Player("Player A", BoardLogicTile.MarkEnum.X), Player("Player B", BoardLogicTile.MarkEnum.O))
        self.header.text_current_player(self._current_player)

    def handle_click(self, click_position: tuple[int, int]) -> None:
        coordinates_for_position = self.board_display.get_coordinates_for_position(position=click_position)
        # Click position outside the board
        if coordinates_for_position is None:
            return

        state_changed = self.board_logic.update(coordinates_for_position, self._current_player.mark)

        # We don't need to do anything if the board state did not change, i.e. clicking on already marked tile.
        if not state_changed:
            return

        if self.board_logic.state.game_status == BoardState.GameStatusEnum.WIN:
            self.header.text_winning_player(self._current_player)
        elif self.board_logic.state.game_status == BoardState.GameStatusEnum.DRAW:
            self.header.text_draw()
        else:
            self._change_player()
            self.header.text_current_player(self._current_player)

    def draw(self) -> None:
        self.header.draw()
        self.board_display.draw(self.board_logic.state)

    @property
    def _current_player(self) -> Player:
        return self.players[self._current_player_index]

    def _change_player(self) -> None:
        self._current_player_index = (self._current_player_index + 1) % 2
