from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import product
from typing import Optional, Any


class BoardLogic:
    """
    Handle game logic of the board. Keeps current state of marks board state (i.e. win/draw).
    """

    board_size: int
    state: "BoardState"
    _tiles: dict[tuple[int, int], "BoardLogicTile"]

    def __init__(self, board_size: int):
        if board_size < 3 or board_size > 5:
            raise Exception(f"Invalid board size: {self.board_size}. Supported board sizes: 3, 4 and 5.")

        self.board_size = board_size
        self.state = BoardState()

        self._initialize_tiles()

    def _initialize_tiles(self) -> None:
        """Generate mapping of coordinates to the tiles of the board."""
        self._tiles = {}

        for row, col in product(range(self.board_size), range(self.board_size)):
            self._tiles[(row, col)] = BoardLogicTile(row=row, column=col)

    def update(self, coordinates: tuple[int, int], mark: "BoardLogicTile.MarkEnum") -> bool:
        """
        Updates tile and board state after making a mark ob the board.

        :return: True if board state changed
        """
        tile = self._get_tile_by_coordinates(*coordinates)
        # Update the board only if tile has no mark.
        if tile.mark is None:
            tile.mark = mark
            self._set_board_state_after_last_mark(tile)
            return True
        return False

    def _set_board_state_after_last_mark(self, marked_tile: "BoardLogicTile") -> None:
        """
        Sets board's proper state depending on the last mark.
        We only need to check rows, cols and diagonals for the last checked mark.
        """
        if marked_tile.mark is None:
            return

        self.state.add_marked_tile(marked_tile)

        tiles_row = self._get_tiles_from_row(marked_tile.row)
        if self._check_if_all_tiles_marked_as(tiles_row, marked_tile.mark):
            self.state.set_win_status(winning_group=tiles_row, winning_group_type=BoardState.WinningGroupTypeEnum.ROW)

        tiles_column = self._get_tiles_from_column(marked_tile.column)
        if self._check_if_all_tiles_marked_as(tiles_column, marked_tile.mark):
            self.state.set_win_status(
                winning_group=tiles_column, winning_group_type=BoardState.WinningGroupTypeEnum.COLUMN
            )

        main_diagonal_tiles = self._get_tiles_from_main_diagonal()
        if self._check_if_all_tiles_marked_as(main_diagonal_tiles, marked_tile.mark):
            self.state.set_win_status(
                winning_group=main_diagonal_tiles, winning_group_type=BoardState.WinningGroupTypeEnum.DIAGONAL_MAIN
            )

        secondary_diagonal_tiles = self._get_tiles_from_secondary_diagonal()
        if self._check_if_all_tiles_marked_as(secondary_diagonal_tiles, marked_tile.mark):
            self.state.set_win_status(
                winning_group=secondary_diagonal_tiles,
                winning_group_type=BoardState.WinningGroupTypeEnum.DIAGONAL_SECONDARY,
            )

        if all([t.mark for t in self._tiles.values()]) and self.state.game_status == BoardState.GameStatusEnum.IN_PLAY:
            self.state.set_draw_status()

    def _get_tiles_from_row(self, row: int) -> list["BoardLogicTile"]:
        return [tile for coord, tile in self._tiles.items() if coord[0] == row]

    def _get_tiles_from_column(self, column: int) -> list["BoardLogicTile"]:
        return [tile for coord, tile in self._tiles.items() if coord[1] == column]

    def _get_tiles_from_main_diagonal(self) -> list["BoardLogicTile"]:
        main_diagonal = [(i, i) for i in range(self.board_size)]
        return [self._get_tile_by_coordinates(row, col) for row, col in main_diagonal]

    def _get_tiles_from_secondary_diagonal(self) -> list["BoardLogicTile"]:
        secondary_diagonal = [(i, self.board_size - 1 - i) for i in range(self.board_size)]
        return [self._get_tile_by_coordinates(row, col) for row, col in secondary_diagonal]

    @staticmethod
    def _check_if_all_tiles_marked_as(tiles: list["BoardLogicTile"], mark: "BoardLogicTile.MarkEnum") -> bool:
        """Check if all tiles are marked the same as provided mark."""
        return all([t.mark == mark for t in tiles])

    def _get_tile_by_coordinates(self, x: int, y: int) -> "BoardLogicTile":
        return self._tiles[(x, y)]


@dataclass
class BoardLogicTile:
    """
    Representation of a single board tile.
    Keep coordinates of a tile and information about mark.
    """

    row: int
    column: int
    mark: Optional["BoardLogicTile.MarkEnum"] = None

    def __init__(self, *args: Any, row: int, column: int, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.row = row
        self.column = column

    class MarkEnum(Enum):
        X = auto()
        O = auto()  # noqa: E741


@dataclass
class BoardState:
    """
    Stores the state of the board.
    Has all data needed to detect win/draw status and do drawing on the board.
    """

    class WinningGroupTypeEnum(Enum):
        ROW = auto()
        COLUMN = auto()
        DIAGONAL_MAIN = auto()
        DIAGONAL_SECONDARY = auto()

    class GameStatusEnum(Enum):
        WIN = auto()
        DRAW = auto()
        IN_PLAY = auto()

    game_status: GameStatusEnum = GameStatusEnum.IN_PLAY
    winning_group: Optional[list[BoardLogicTile]] = None
    winning_group_type: Optional[WinningGroupTypeEnum] = None
    marked_tiles: list[BoardLogicTile] = field(default_factory=list)

    def set_win_status(self, winning_group: list[BoardLogicTile], winning_group_type: WinningGroupTypeEnum) -> None:
        self.game_status = BoardState.GameStatusEnum.WIN
        self.winning_group = winning_group
        self.winning_group_type = winning_group_type

    def set_draw_status(self) -> None:
        self.game_status = BoardState.GameStatusEnum.DRAW
        self.winning_group = None
        self.winning_group_type = None

    def add_marked_tile(self, marked_tile: BoardLogicTile) -> None:
        self.marked_tiles.append(marked_tile)
