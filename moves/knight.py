from board import BoardRepresentation
from .white_king_capturable import Check_White
from .black_king_capturable import Check_Black

class KnightMove:
	@staticmethod
	def get_moves(board: BoardRepresentation, position: int) -> list:
		r = position // 8
		c = position % 8
		moves = []
		knight_moves = [
			(2, 1), (2, -1), (-2, 1), (-2, -1),
			(1, 2), (1, -2), (-1, 2), (-1, -2)
		]
		for dr, dc in knight_moves:
			nr, nc = r + dr, c + dc
			if 0 <= nr < 8 and 0 <= nc < 8:
				target = board.board[nr*8 + nc]
				if board.white_turn:
					if target == '.' or target in 'rnbqkp':
						moves.append(nr*8 + nc)
				else:
					if target == '.' or target in 'RNBQKP':
						moves.append(nr*8 + nc)

		valid_moves = []
		for move in moves:
			clone_board = list(board.board)
			clone_board[r*8 + c] = '.'
			clone_board[move] = 'N' if board.white_turn else 'n'
			clone_board_str = ''.join(clone_board)
			if board.white_turn:
				if not Check_White.white_king_capturable(clone_board_str):
					valid_moves.append(move)
			else:
				if not Check_Black.black_king_capturable(clone_board_str):
					valid_moves.append(move)
		return valid_moves
