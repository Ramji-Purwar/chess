from board import BoardRepresentation
from .white_king_capturable import Check_White
from .black_king_capturable import Check_Black

class RookMove:
	@staticmethod
	def get_moves(board: BoardRepresentation, position: int) -> list:
		r = position // 8
		c = position % 8
		moves = []
		directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
		for dr, dc in directions:
			nr, nc = r + dr, c + dc
			while 0 <= nr < 8 and 0 <= nc < 8:
				target = board.board[nr*8 + nc]
				if board.white_turn:
					if target == '.':
						moves.append(nr*8 + nc)
					elif target in 'rnbqkp':
						moves.append(nr*8 + nc)
						break
					else:
						break
				else:
					if target == '.':
						moves.append(nr*8 + nc)
					elif target in 'RNBQKP':
						moves.append(nr*8 + nc)
						break
					else:
						break
				nr += dr
				nc += dc

		valid_moves = []
		for move in moves:
			clone_board = list(board.board)
			clone_board[r*8 + c] = '.'
			clone_board[move] = 'R' if board.white_turn else 'r'
			clone_board_str = ''.join(clone_board)
			if board.white_turn:
				if not Check_White.white_king_capturable(clone_board_str):
					valid_moves.append(move)
			else:
				if not Check_Black.black_king_capturable(clone_board_str):
					valid_moves.append(move)
		return valid_moves
