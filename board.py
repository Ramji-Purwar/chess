class BoardRepresentation:
	def __init__(self):
		self.board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
		self.white_turn = True
		self.white_king_moved = False
		self.black_king_moved = False
		self.white_left_rook_moved = False
		self.white_right_rook_moved = False
		self.black_left_rook_moved = False
		self.black_right_rook_moved = False

		self.en_passant_target = None 
		self.en_passant_pawn = None  

		self.position_white_king = [60]
		self.position_white_queen = [59]
		self.position_white_rooks = [56, 63]
		self.position_white_bishops = [58, 61]
		self.position_white_knights = [57, 62]
		self.position_white_pawns = [48, 49, 50, 51, 52, 53, 54, 55]

		self.position_black_king = [4]
		self.position_black_queen = [3]
		self.position_black_rooks = [0, 7]
		self.position_black_bishops = [2, 5]
		self.position_black_knights = [1, 6]
		self.position_black_pawns = [8, 9, 10, 11, 12, 13, 14, 15]      

		self.position_empty = [i for i in range(16, 48)]
		
		self.piece_map = {
			"K": "white_king", 
			"Q": "white_queen", 
			"R": "white_rook",
			"B": "white_bishop", 
			"N": "white_knight", 
			"P": "white_pawn",
			"k": "black_king", 
			"q": "black_queen", 
			"r": "black_rook",
			"b": "black_bishop", 
			"n": "black_knight", 
			"p": "black_pawn",
			".": "empty"
		}

	def make_move(self, st_pos: int, end_pos: int):

		piece = self.board[st_pos]
		captured_piece = self.board[end_pos]

		old_en_passant_target = self.en_passant_target
		old_en_passant_pawn = self.en_passant_pawn
		self.en_passant_target = None
		self.en_passant_pawn = None

		if piece == "K":
			self.white_king_moved = True
		elif piece == "k":
			self.black_king_moved = True
		elif piece == "R":
			if st_pos == 56:
				self.white_left_rook_moved = True
			elif st_pos == 63:
				self.white_right_rook_moved = True
		elif piece == "r":
			if st_pos == 0:
				self.black_left_rook_moved = True
			elif st_pos == 7:
				self.black_right_rook_moved = True

		is_en_passant = False
		if piece in 'Pp' and end_pos == old_en_passant_target:
			is_en_passant = True
			board_list = list(self.board)
			board_list[old_en_passant_pawn] = '.'
			self.board = ''.join(board_list)
			
			if piece == 'P': 
				if old_en_passant_pawn in self.position_black_pawns:
					self.position_black_pawns.remove(old_en_passant_pawn)
			else:
				if old_en_passant_pawn in self.position_white_pawns:
					self.position_white_pawns.remove(old_en_passant_pawn)
			
			if old_en_passant_pawn not in self.position_empty:
				self.position_empty.append(old_en_passant_pawn)

		if piece == 'P' and st_pos // 8 == 6 and end_pos // 8 == 4:
			self.en_passant_target = st_pos - 8 
			self.en_passant_pawn = end_pos      
		elif piece == 'p' and st_pos // 8 == 1 and end_pos // 8 == 3: 
			self.en_passant_target = st_pos + 8
			self.en_passant_pawn = end_pos

		board_list = list(self.board)
		board_list[end_pos] = piece
		board_list[st_pos] = '.'
		self.board = ''.join(board_list)

		def update_positions(positions, old, new):
			if old in positions:
				positions.remove(old)
			if new not in positions:
				positions.append(new)

		if not is_en_passant and captured_piece != '.':
			if captured_piece == "K":
				if end_pos in self.position_white_king:
					self.position_white_king.remove(end_pos)
			elif captured_piece == "Q":
				if end_pos in self.position_white_queen:
					self.position_white_queen.remove(end_pos)
			elif captured_piece == "R":
				if end_pos in self.position_white_rooks:
					self.position_white_rooks.remove(end_pos)
			elif captured_piece == "B":
				if end_pos in self.position_white_bishops:
					self.position_white_bishops.remove(end_pos)
			elif captured_piece == "N":
				if end_pos in self.position_white_knights:
					self.position_white_knights.remove(end_pos)
			elif captured_piece == "P":
				if end_pos in self.position_white_pawns:
					self.position_white_pawns.remove(end_pos)
			elif captured_piece == "k":
				if end_pos in self.position_black_king:
					self.position_black_king.remove(end_pos)
			elif captured_piece == "q":
				if end_pos in self.position_black_queen:
					self.position_black_queen.remove(end_pos)
			elif captured_piece == "r":
				if end_pos in self.position_black_rooks:
					self.position_black_rooks.remove(end_pos)
			elif captured_piece == "b":
				if end_pos in self.position_black_bishops:
					self.position_black_bishops.remove(end_pos)
			elif captured_piece == "n":
				if end_pos in self.position_black_knights:
					self.position_black_knights.remove(end_pos)
			elif captured_piece == "p":
				if end_pos in self.position_black_pawns:
					self.position_black_pawns.remove(end_pos)

		if piece == "K":
			update_positions(self.position_white_king, st_pos, end_pos)
		elif piece == "Q":
			update_positions(self.position_white_queen, st_pos, end_pos)
		elif piece == "R":
			update_positions(self.position_white_rooks, st_pos, end_pos)
		elif piece == "B":
			update_positions(self.position_white_bishops, st_pos, end_pos)
		elif piece == "N":
			update_positions(self.position_white_knights, st_pos, end_pos)
		elif piece == "P":
			update_positions(self.position_white_pawns, st_pos, end_pos)
		elif piece == "k":
			update_positions(self.position_black_king, st_pos, end_pos)
		elif piece == "q":
			update_positions(self.position_black_queen, st_pos, end_pos)
		elif piece == "r":
			update_positions(self.position_black_rooks, st_pos, end_pos)
		elif piece == "b":
			update_positions(self.position_black_bishops, st_pos, end_pos)
		elif piece == "n":
			update_positions(self.position_black_knights, st_pos, end_pos)
		elif piece == "p":
			update_positions(self.position_black_pawns, st_pos, end_pos)

		if st_pos not in self.position_empty:
			self.position_empty.append(st_pos)
		if end_pos in self.position_empty:
			self.position_empty.remove(end_pos)
		
		self.white_turn = not self.white_turn

	def make_promotion_move(self, st_pos: int, end_pos: int, promoted_piece: str):
		piece = self.board[st_pos]
		captured_piece = self.board[end_pos]

		board_list = list(self.board)
		board_list[end_pos] = promoted_piece
		board_list[st_pos] = '.'
		self.board = ''.join(board_list)

		def update_positions(positions, old, new):
			if old in positions:
				positions.remove(old)
			if new not in positions:
				positions.append(new)

		if captured_piece == "K":
			if end_pos in self.position_white_king:
				self.position_white_king.remove(end_pos)
		elif captured_piece == "Q":
			if end_pos in self.position_white_queen:
				self.position_white_queen.remove(end_pos)
		elif captured_piece == "R":
			if end_pos in self.position_white_rooks:
				self.position_white_rooks.remove(end_pos)
		elif captured_piece == "B":
			if end_pos in self.position_white_bishops:
				self.position_white_bishops.remove(end_pos)
		elif captured_piece == "N":
			if end_pos in self.position_white_knights:
				self.position_white_knights.remove(end_pos)
		elif captured_piece == "P":
			if end_pos in self.position_white_pawns:
				self.position_white_pawns.remove(end_pos)
		elif captured_piece == "k":
			if end_pos in self.position_black_king:
				self.position_black_king.remove(end_pos)
		elif captured_piece == "q":
			if end_pos in self.position_black_queen:
				self.position_black_queen.remove(end_pos)
		elif captured_piece == "r":
			if end_pos in self.position_black_rooks:
				self.position_black_rooks.remove(end_pos)
		elif captured_piece == "b":
			if end_pos in self.position_black_bishops:
				self.position_black_bishops.remove(end_pos)
		elif captured_piece == "n":
			if end_pos in self.position_black_knights:
				self.position_black_knights.remove(end_pos)
		elif captured_piece == "p":
			if end_pos in self.position_black_pawns:
				self.position_black_pawns.remove(end_pos)

		if piece == "P":
			if st_pos in self.position_white_pawns:
				self.position_white_pawns.remove(st_pos)
		elif piece == "p":
			if st_pos in self.position_black_pawns:
				self.position_black_pawns.remove(st_pos)

		if promoted_piece == "Q":
			if end_pos not in self.position_white_queen:
				self.position_white_queen.append(end_pos)
		elif promoted_piece == "R":
			if end_pos not in self.position_white_rooks:
				self.position_white_rooks.append(end_pos)
		elif promoted_piece == "B":
			if end_pos not in self.position_white_bishops:
				self.position_white_bishops.append(end_pos)
		elif promoted_piece == "N":
			if end_pos not in self.position_white_knights:
				self.position_white_knights.append(end_pos)
		elif promoted_piece == "q":
			if end_pos not in self.position_black_queen:
				self.position_black_queen.append(end_pos)
		elif promoted_piece == "r":
			if end_pos not in self.position_black_rooks:
				self.position_black_rooks.append(end_pos)
		elif promoted_piece == "b":
			if end_pos not in self.position_black_bishops:
				self.position_black_bishops.append(end_pos)
		elif promoted_piece == "n":
			if end_pos not in self.position_black_knights:
				self.position_black_knights.append(end_pos)

		if st_pos not in self.position_empty:
			self.position_empty.append(st_pos)
		if end_pos in self.position_empty:
			self.position_empty.remove(end_pos)
		
		self.white_turn = not self.white_turn

	def make_castling_move(self, king_start: int, king_end: int, rook_start: int, rook_end: int):
		board_list = list(self.board)
		
		if self.white_turn:
			board_list[king_end] = 'K'
			board_list[king_start] = '.'
			
			board_list[rook_end] = 'R'
			board_list[rook_start] = '.'
			
			self.position_white_king = [king_end]
			if rook_start in self.position_white_rooks:
				self.position_white_rooks.remove(rook_start)
			self.position_white_rooks.append(rook_end)
			
			self.white_king_moved = True
			if rook_start == 56:
				self.white_left_rook_moved = True
			elif rook_start == 63:
				self.white_right_rook_moved = True
		else:
			board_list[king_end] = 'k'
			board_list[king_start] = '.'
			
			board_list[rook_end] = 'r'
			board_list[rook_start] = '.'
			
			self.position_black_king = [king_end]
			if rook_start in self.position_black_rooks:
				self.position_black_rooks.remove(rook_start)
			self.position_black_rooks.append(rook_end)
			
			self.black_king_moved = True
			if rook_start == 0:
				self.black_left_rook_moved = True
			elif rook_start == 7:
				self.black_right_rook_moved = True
		
		if king_start not in self.position_empty:
			self.position_empty.append(king_start)
		if rook_start not in self.position_empty:
			self.position_empty.append(rook_start)
		if king_end in self.position_empty:
			self.position_empty.remove(king_end)
		if rook_end in self.position_empty:
			self.position_empty.remove(rook_end)
		
		self.board = ''.join(board_list)
		self.white_turn = not self.white_turn