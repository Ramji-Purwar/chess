from board import BoardRepresentation
from moves.bishop import BishopMove
from moves.rook import RookMove
from moves.queen import QueenMove
from moves.knight import KnightMove
from moves.king import KingMove
from moves.pawn import PawnMoves

class MoveValidator:
	@staticmethod
	def get_valid_moves(board: BoardRepresentation, pos: int, piece: str) -> list:
		piece_map = {
			'p': PawnMoves.get_moves,
			'P': PawnMoves.get_moves,
			'r': RookMove.get_moves,
			'R': RookMove.get_moves,
			'n': KnightMove.get_moves,
			'N': KnightMove.get_moves,
			'b': BishopMove.get_moves,
			'B': BishopMove.get_moves,
			'q': QueenMove.get_moves,
			'Q': QueenMove.get_moves,
			'k': KingMove.get_moves,
			'K': KingMove.get_moves,
		}
		if piece in piece_map:
			return piece_map[piece](board, pos)
		return []
