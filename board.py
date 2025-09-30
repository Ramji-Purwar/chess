class BoardRepresentation:
	def __init__(self):
		self.board = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
		self.white_turn = True

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

		board_list = list(self.board)
		board_list[end_pos] = piece
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