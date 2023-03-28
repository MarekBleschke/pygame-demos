from dataclasses import dataclass

from tic_tac_toe.board_logic import BoardLogicTile


@dataclass
class Player:
    name: str
    mark: BoardLogicTile.MarkEnum
