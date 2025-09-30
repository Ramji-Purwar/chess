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

	@staticmethod
	def kings_adjacent(board_str: str, new_king_pos: int) -> bool:
		if 'K' in board_str and 'k' in board_str:
			white_king_pos = board_str.index('K')
			black_king_pos = board_str.index('k')
			
			white_r, white_c = white_king_pos // 8, white_king_pos % 8
			black_r, black_c = black_king_pos // 8, black_king_pos % 8
			
			row_diff = abs(white_r - black_r)
			col_diff = abs(white_c - black_c)
			
			return (row_diff <= 1 and col_diff <= 1) and not (row_diff == 0 and col_diff == 0)
		return False

	@staticmethod
	def can_castle_kingside(board: BoardRepresentation) -> bool:
		if board.white_turn:
			if board.white_king_moved or board.white_right_rook_moved:
				return False
			
			if board.board[61] != '.' or board.board[62] != '.':
				return False
			
			if Check_White.white_king_capturable(board.board):
				return False
			
			clone_board = list(board.board)
			clone_board[60] = '.' 
			clone_board[61] = 'K' 
			if Check_White.white_king_capturable(''.join(clone_board)):
				return False
			
			clone_board = list(board.board)
			clone_board[60] = '.' 
			clone_board[62] = 'K' 
			if Check_White.white_king_capturable(''.join(clone_board)):
				return False
			
			return True
		else:
			if board.black_king_moved or board.black_right_rook_moved:
				return False
			
			if board.board[5] != '.' or board.board[6] != '.':
				return False
			
			if Check_Black.black_king_capturable(board.board):
				return False
			
			clone_board = list(board.board)
			clone_board[4] = '.' 
			clone_board[5] = 'k' 
			if Check_Black.black_king_capturable(''.join(clone_board)):
				return False
			
			clone_board = list(board.board)
			clone_board[4] = '.' 
			clone_board[6] = 'k' 
			if Check_Black.black_king_capturable(''.join(clone_board)):
				return False
			
			return True

	@staticmethod
	def can_castle_queenside(board: BoardRepresentation) -> bool:
		if board.white_turn:
			if board.white_king_moved or board.white_left_rook_moved:
				return False
			
			if board.board[57] != '.' or board.board[58] != '.' or board.board[59] != '.':
				return False
			
			if Check_White.white_king_capturable(board.board):
				return False
			
			clone_board = list(board.board)
			clone_board[60] = '.'  
			clone_board[59] = 'K'  
			if Check_White.white_king_capturable(''.join(clone_board)):
				return False
			
			clone_board = list(board.board)
			clone_board[60] = '.'
			clone_board[58] = 'K' 
			if Check_White.white_king_capturable(''.join(clone_board)):
				return False
			
			return True
		else:
			if board.black_king_moved or board.black_left_rook_moved:
				return False
			
			if board.board[1] != '.' or board.board[2] != '.' or board.board[3] != '.':
				return False
			
			if Check_Black.black_king_capturable(board.board):
				return False
			
			clone_board = list(board.board)
			clone_board[4] = '.'  
			clone_board[3] = 'k'  
			if Check_Black.black_king_capturable(''.join(clone_board)):
				return False
			
			clone_board = list(board.board)
			clone_board[4] = '.'  
			clone_board[2] = 'k'  
			if Check_Black.black_king_capturable(''.join(clone_board)):
				return False
			
			return True

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

		if board.white_turn and position == 60:
			if KingMove.can_castle_kingside(board):
				moves.append(62) 
			if KingMove.can_castle_queenside(board):
				moves.append(58)  
		elif not board.white_turn and position == 4:
			if KingMove.can_castle_kingside(board):
				moves.append(6) 
			if KingMove.can_castle_queenside(board):
				moves.append(2) 

		valid_moves = []
		for move in moves:
			is_castling = False
			if board.white_turn and position == 60: 
				if move == 62:  
					is_castling = True
				elif move == 58:
					is_castling = True
			elif not board.white_turn and position == 4:
				if move == 6:  
					is_castling = True
				elif move == 2: 
					is_castling = True
			
			if is_castling:
				valid_moves.append(move)
			else:
				clone_board = list(board.board)
				clone_board[r*8 + c] = '.'
				clone_board[move] = 'K' if board.white_turn else 'k'
				clone_board_str = ''.join(clone_board)
				
				if KingMove.kings_adjacent(clone_board_str, move):
					continue
				
				if board.white_turn:
					if not Check_White.white_king_capturable(clone_board_str):
						valid_moves.append(move)
				else:
					if not Check_Black.black_king_capturable(clone_board_str):
						valid_moves.append(move)
					
		return valid_moves
