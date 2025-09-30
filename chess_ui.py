import pygame
import os
from board import BoardRepresentation
from valid_move import MoveValidator
from check_detector import CheckDetector
from mate_detector import MateDetector

class ChessUI:
	def __init__(self):
		pygame.init()
		self.width = 480
		self.height = 480
		self.square_size = 60
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Chess")
		self.clock = pygame.time.Clock()
		self.images = {}
		self.board_state = BoardRepresentation()
		self.check_detector = CheckDetector()
		self.mate_detector = MateDetector()
		self.square_colors = [(255, 206, 158), (209, 139, 71)]
		self.running = True
		self.selected_piece = None
		self.valid_moves = []
		self.game_over = False
		self.game_status = 'normal'
		self.load_images()

	def load_images(self):
		colors = ["dark", "light"]
		pieces = [
			"white_king", "white_queen", "white_rook", "white_bishop", "white_knight", "white_pawn",
			"black_king", "black_queen", "black_rook", "black_bishop", "black_knight", "black_pawn"
		]
		
		for piece in pieces:
			for color in colors:
				img_path = os.path.join("images", f"{piece}_{color}.png")
				try:
					image = pygame.image.load(img_path)
					image = pygame.transform.scale(image, (self.square_size, self.square_size))
					self.images[f"{piece}_{color}"] = image
				except Exception as e:
					print(f"Could not load {img_path}: {e}")


	def draw_board(self):
		# Check if current player's king is in check
		is_in_check = self.check_detector.checked(self.board_state, self.board_state.white_turn)
		king_pos = None
		if is_in_check:
			# Find the king position based on whose turn it is
			king_piece = 'K' if self.board_state.white_turn else 'k'
			king_pos = self.board_state.board.index(king_piece)
		
		for row in range(8):
			for col in range(8):
				idx = row * 8 + col
				piece = self.board_state.board[idx]
				color_index = (row + col) % 2
				color = self.square_colors[color_index]
				
				rect = pygame.Rect(col * self.square_size, row * self.square_size, 
								 self.square_size, self.square_size)
				pygame.draw.rect(self.screen, color, rect)
				
				# Highlight selected piece
				if self.selected_piece == idx:
					pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
				
				if piece != ".":
					img_key = self.get_image_key(piece)
					if img_key:
						img_full_key = f"{img_key}_{'light' if color_index == 0 else 'dark'}"
						if img_full_key in self.images:
							self.screen.blit(self.images[img_full_key], 
										   (col * self.square_size, row * self.square_size))
				
				# Draw valid move highlight ABOVE the piece image
				if idx in self.valid_moves:
					# Red highlight for capture moves (opponent pieces), green for empty squares
					highlight_color = (255, 0, 0) if piece != "." else (0, 255, 0)
					pygame.draw.rect(self.screen, highlight_color, rect, 3)
				
				# Draw king in check highlight ABOVE the piece image
				if king_pos is not None and idx == king_pos:
					pygame.draw.rect(self.screen, (255, 0, 0), rect, 5)
		
		# Display whose turn it is
		self.draw_turn_indicator()

	def draw_turn_indicator(self):
		"""Draw a text indicator showing whose turn it is and game status"""
		font = pygame.font.Font(None, 36)
		
		# Check game status
		self.game_status = self.mate_detector.get_game_status(self.board_state)
		
		if self.game_status == 'checkmate':
			winner = "Black" if self.board_state.white_turn else "White"
			turn_text = f"Checkmate! {winner} Wins!"
			text_color = (255, 0, 0)
			bg_color = (255, 255, 255)
			self.game_over = True
		elif self.game_status == 'stalemate':
			turn_text = "Stalemate! Draw!"
			text_color = (128, 128, 128)
			bg_color = (255, 255, 255)
			self.game_over = True
		elif self.game_status == 'check':
			player = "White" if self.board_state.white_turn else "Black"
			turn_text = f"Check! {player}'s Turn"
			text_color = (255, 0, 0)
			bg_color = (255, 255, 255)
		else:
			turn_text = "White's Turn" if self.board_state.white_turn else "Black's Turn"
			text_color = (255, 255, 255) if self.board_state.white_turn else (0, 0, 0)
			bg_color = (0, 0, 0) if self.board_state.white_turn else (255, 255, 255)
		
		text_surface = font.render(turn_text, True, text_color, bg_color)
		text_rect = text_surface.get_rect()
		text_rect.centerx = self.width // 2
		text_rect.y = 10
		
		self.screen.blit(text_surface, text_rect)
		
		# If game is over, show restart instruction
		if self.game_over:
			font_small = pygame.font.Font(None, 24)
			restart_text = "Press 'R' to restart"
			restart_surface = font_small.render(restart_text, True, (100, 100, 100), (255, 255, 255))
			restart_rect = restart_surface.get_rect()
			restart_rect.centerx = self.width // 2
			restart_rect.y = text_rect.bottom + 5
			self.screen.blit(restart_surface, restart_rect)

	def restart_game(self):
		"""Restart the game to initial state"""
		self.board_state = BoardRepresentation()
		self.selected_piece = None
		self.valid_moves = []
		self.game_over = False
		self.game_status = 'normal'

	def get_image_key(self, piece):
		piece_map = self.board_state.piece_map
		return piece_map.get(piece)

	def is_current_player_piece(self, piece):
		"""Check if the piece belongs to the current player"""
		if piece == '.':
			return False
		is_white_piece = piece.isupper()
		return (self.board_state.white_turn and is_white_piece) or (not self.board_state.white_turn and not is_white_piece)

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1 and not self.game_over:  # Only handle clicks if game is not over
					mouse_x, mouse_y = event.pos
					col = mouse_x // self.square_size
					row = mouse_y // self.square_size
					
					pos = row * 8 + col
					piece = self.board_state.board[pos]

					# Only allow selecting pieces that belong to the current player
					if piece != '.' and self.is_current_player_piece(piece):
						self.selected_piece = pos
						self.valid_moves = MoveValidator.get_valid_moves(self.board_state, pos, piece)

					elif self.selected_piece is not None:
						if pos in self.valid_moves:
							print(f"Moving piece from {self.selected_piece} to {pos}")
							
							# Check if this is a castling move
							piece = self.board_state.board[self.selected_piece]
							is_castling = False
							
							if piece == 'K' and self.selected_piece == 60:  # White king from e1
								if pos == 62:  # Kingside castling to g1
									self.board_state.make_castling_move(60, 62, 63, 61)
									is_castling = True
								elif pos == 58:  # Queenside castling to c1
									self.board_state.make_castling_move(60, 58, 56, 59)
									is_castling = True
							elif piece == 'k' and self.selected_piece == 4:  # Black king from e8
								if pos == 6:  # Kingside castling to g8
									self.board_state.make_castling_move(4, 6, 7, 5)
									is_castling = True
								elif pos == 2:  # Queenside castling to c8
									self.board_state.make_castling_move(4, 2, 0, 3)
									is_castling = True
							
							if not is_castling:
								self.board_state.make_move(self.selected_piece, pos)
								
						self.selected_piece = None
						self.valid_moves = []
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r and self.game_over:  # Press 'R' to restart when game is over
					self.restart_game()


	def run(self):
		while self.running:
			self.handle_events()
			self.screen.fill((0, 0, 0))
			self.draw_board()
			pygame.display.flip()
			self.clock.tick(60)
		
		pygame.quit()