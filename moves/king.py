from board import BoardRepresentation
from .white_king_capturable import Check_White
from .black_king_capturable import Check_Black

class KingMove:
	@staticmethod
	def white_king_capturable_by_pawn(board : str) -> bool:
		pos = board.index('K')
		r = pos // 8
		c = pos % 8
		if r < 7:
			if(c > 0 and board[(r-1)*8 + (c-1)] == 'p'):
				return True
			if(c < 7 and board[(r-1)*8 + (c+1)] == 'p'):
				return True
		return False
	
	@staticmethod
	def black_king_capturable_by_pawn(board : str) -> bool:
		pos = board.index('k')
		r = pos // 8
		c = pos % 8
		if(r > 0):
			if(c > 0 and board[(r+1)*8 + (c-1)] == 'P'):
				return True
			if(c < 7 and board[(r+1)*8 + (c+1)] == 'P'):
				return True
		return False

	def get_moves(board: BoardRepresentation, position: int) -> list:
		r = position // 8
		c = position % 8
		moves = []
		directions = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1),           (0, 1),
			(1, -1),  (1, 0),  (1, 1)
		]
		for dr, dc in directions:
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
			clone_board[move] = 'K' if board.white_turn else 'k'
			clone_board_str = ''.join(clone_board)
			if board.white_turn:
				if not Check_White.white_king_capturable(clone_board_str):
					valid_moves.append(move)
			else:
				if not Check_Black.black_king_capturable(clone_board_str):
					valid_moves.append(move)
					
		return valid_moves
