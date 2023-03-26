from dataclasses import dataclass
from itertools import product
from typing import Optional

import pygame

from tic_tac_toe.board_logic import BoardState, BoardLogicTile


class BoardDisplay:
    main_screen: pygame.Surface
    board_size: int
    width: int
    height: int
    board_surface: pygame.Surface
    board_position: tuple[int, int]
    line_color: pygame.Color
    line_width: int = 3
    padding: "BoardPadding"
    _tiles: dict[tuple[int, int], "BoardDisplayTile"]

    def __init__(self, main_screen: pygame.Surface, board_size: int, background_color: pygame.Color,
                 line_color: pygame.Color):
        if board_size < 3 or board_size > 5:
            raise Exception(f"Invalid board size: {self.board_size}. Supported board sizes: 3, 4 and 5.")
        self.main_screen = main_screen
        self.board_size = board_size
        self.width = self.main_screen.get_width()
        self.height = 400
        self.board_surface = pygame.Surface((self.width, self.height))
        self.board_position = (0, self.main_screen.get_height() - self.height - 50)  # Board position on the main screen
        self.line_color = line_color
        self.padding = BoardPadding(left=140, top=40, right=140, bottom=40)

        self.board_surface.fill(background_color)

        self._initialize_tiles()

    def _initialize_tiles(self):
        """ Generate mapping of coordinates to the tiles of the board. """
        self._tiles = {}
        tile_width = (self.width - self.padding.left - self.padding.right) / self.board_size
        tile_height = (self.height - self.padding.top - self.padding.bottom) / self.board_size

        for row, col in product(range(self.board_size), range(self.board_size)):
            self._tiles[(row, col)] = BoardDisplayTile(
                self.padding.left + col * tile_width,
                self.padding.top + row * tile_height,
                tile_width,
                tile_height,
                row=row,
                column=col
            )

    def draw(self, board_state: BoardState):
        self._draw_board_lines()
        self._draw_marked_tiles(board_state.marked_tiles)
        if board_state.game_status == BoardState.GameStatusEnum.WIN:
            self._draw_winning_strikethrough(board_state)
        self.main_screen.blit(self.board_surface, self.board_position)

    def get_coordinates_for_position(self, position: tuple[int, int]) -> Optional[tuple[int, int]]:
        """ Return tile coordinates for position on main screen. """
        board_position = self._convert_screen_position_to_board_position(position)
        for coords, tile in self._tiles.items():
            if tile.collidepoint(board_position):
                return tile.row, tile.column
        return None

    def _draw_board_lines(self) -> None:
        # horizontal lines
        for row_number in range(self.board_size - 1):
            # horizontal top
            t1 = self._get_tile_by_coordinates(row_number, 0)
            t2 = self._get_tile_by_coordinates(row_number, self.board_size - 1)
            pygame.draw.line(
                self.board_surface,
                self.line_color,
                (t1.left, t1.bottom),
                (t2.right, t2.bottom),
                self.line_width
            )
        # vertical lines
        for column_number in range(self.board_size - 1):
            t1 = self._get_tile_by_coordinates(0, column_number)
            t2 = self._get_tile_by_coordinates(self.board_size - 1, column_number)
            pygame.draw.line(
                self.board_surface,
                self.line_color,
                (t1.right, t1.top),
                (t2.right, t2.bottom),
                self.line_width
            )

    def _draw_marked_tiles(self, marked_tiles: list[BoardLogicTile]) -> None:
        for game_board_tile in marked_tiles:
            tile = self._get_tile_by_coordinates(game_board_tile.row, game_board_tile.column)
            rect = tile.inflate(-10, -10)
            if game_board_tile.mark == BoardLogicTile.MarkEnum.X:
                pygame.draw.line(self.board_surface, "black", rect.topleft, rect.bottomright, 6)
                pygame.draw.line(self.board_surface, "black", rect.bottomleft, rect.topright, 6)
            if game_board_tile.mark == BoardLogicTile.MarkEnum.O:
                pygame.draw.circle(self.board_surface, "black", rect.center, rect.width / 2, 6)

    def _draw_winning_strikethrough(self, board_state: BoardState) -> None:
        if not board_state.game_status == BoardState.GameStatusEnum.WIN:
            return
        sorted_winning_group = self._get_sorted_winning_group(board_state)
        start_tile = self._get_tile_by_coordinates(sorted_winning_group[0].row,
                                                   sorted_winning_group[0].column)
        end_tile = self._get_tile_by_coordinates(sorted_winning_group[-1].row,
                                                 sorted_winning_group[-1].column)
        if board_state.winning_group_type == BoardState.WinningGroupTypeEnum.ROW:
            start_pos = (start_tile.left, start_tile.centery)
            end_pos = (end_tile.right, end_tile.centery)
        elif board_state.winning_group_type == BoardState.WinningGroupTypeEnum.COLUMN:
            start_pos = (start_tile.centerx, start_tile.top)
            end_pos = (end_tile.centerx, end_tile.bottom)
        elif board_state.winning_group_type == BoardState.WinningGroupTypeEnum.DIAGONAL_MAIN:
            start_pos = start_tile.topleft
            end_pos = end_tile.bottomright
        elif board_state.winning_group_type == BoardState.WinningGroupTypeEnum.DIAGONAL_SECONDARY:
            start_pos = start_tile.bottomleft
            end_pos = end_tile.topright
        else:
            return
        pygame.draw.line(self.board_surface, "red", start_pos, end_pos, 6)

    @staticmethod
    def _get_sorted_winning_group(board_state: BoardState) -> list[BoardLogicTile]:
        """ Sort tiles of row, column or diagonal. """
        if board_state.winning_group_type == BoardState.WinningGroupTypeEnum.ROW:
            return sorted(board_state.winning_group, key=lambda t: t.column)
        elif board_state.winning_group_type == BoardState.WinningGroupTypeEnum.COLUMN:
            return sorted(board_state.winning_group, key=lambda t: t.row)
        elif board_state.winning_group_type == BoardState.WinningGroupTypeEnum.DIAGONAL_MAIN:
            return sorted(board_state.winning_group, key=lambda t: (t.row, t.column))
        elif board_state.winning_group_type == BoardState.WinningGroupTypeEnum.DIAGONAL_SECONDARY:
            return sorted(board_state.winning_group, key=lambda t: (t.row, t.column), reverse=True)
        else:
            return board_state.winning_group

    def _convert_screen_position_to_board_position(self, pos: tuple[int, int]) -> tuple[int, int]:
        board_pos = (pos[0] - self.board_position[0], pos[1] - self.board_position[1])
        return board_pos

    def _get_tile_by_coordinates(self, x, y) -> pygame.Rect:
        """(0, 0) is on top left position of the board."""
        return self._tiles[(x, y)]


@dataclass
class BoardPadding:
    left: int
    top: int
    right: int
    bottom: int


class BoardDisplayTile(pygame.Rect):
    def __init__(self, *args, row, column, **kwargs):
        super().__init__(*args, **kwargs)
        self.row = row
        self.column = column
