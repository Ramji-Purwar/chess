import pygame
import os
import threading
import time
from board import BoardRepresentation
from valid_move import MoveValidator
from check_detector import CheckDetector
from mate_detector import MateDetector
from moves.pawn import PawnMoves
from best_move import BestMoveEngine
from notation_convert import AlgebraicNotationConverter

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
		self.promotion_pending = False
		self.promotion_from = None
		self.promotion_to = None
		self.promotion_pieces = ['Q', 'R', 'B', 'N']  # Queen, Rook, Bishop, Knight
		
		# Game mode selection
		self.game_mode = None  # None means selecting mode, 'hvh', 'hvc_white', 'hvc_black'
		self.show_mode_selection = True
		self.computer_is_white = False
		self.computer_is_black = False
		self.ai_engine = BestMoveEngine(depth=3)
		self.computer_thinking = False
		self.computer_move_thread = None
		
		# Notation converter for storing algebraic notation
		self.notation_converter = AlgebraicNotationConverter()
		self.move_count = 0  # Track number of moves for incremental conversion
		
		self.load_images()
		
		# Clear game.txt and save initial board state
		self.clear_game_file()
		self.clear_algebraic_file()  # Also clear algebraic notation file
		self.save_board_state()

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


	def draw_mode_selection(self):
		"""Draw game mode selection screen"""
		self.screen.fill((50, 50, 50))
		
		# Title
		font_large = pygame.font.Font(None, 48)
		title_text = "Choose Game Mode"
		title_surface = font_large.render(title_text, True, (255, 255, 255))
		title_rect = title_surface.get_rect()
		title_rect.centerx = self.width // 2
		title_rect.y = 80
		self.screen.blit(title_surface, title_rect)
		
		# Mode options
		font = pygame.font.Font(None, 32)
		options = [
			("1. Human vs Human", "hvh"),
			("2. Human (White) vs Computer", "hvc_white"),
			("3. Human (Black) vs Computer", "hvc_black")
		]
		
		option_y = 180
		for i, (text, mode) in enumerate(options):
			text_surface = font.render(text, True, (255, 255, 255))
			text_rect = text_surface.get_rect()
			text_rect.centerx = self.width // 2
			text_rect.y = option_y + i * 60
			self.screen.blit(text_surface, text_rect)
		
		# Instructions
		font_small = pygame.font.Font(None, 24)
		instruction_text = "Press 1, 2, or 3 to select"
		instruction_surface = font_small.render(instruction_text, True, (200, 200, 200))
		instruction_rect = instruction_surface.get_rect()
		instruction_rect.centerx = self.width // 2
		instruction_rect.y = 380
		self.screen.blit(instruction_surface, instruction_rect)

	def set_game_mode(self, mode):
		"""Set the game mode and configure computer players"""
		self.game_mode = mode
		self.show_mode_selection = False
		
		if mode == "hvh":
			self.computer_is_white = False
			self.computer_is_black = False
		elif mode == "hvc_white":
			self.computer_is_white = False
			self.computer_is_black = True
		elif mode == "hvc_black":
			self.computer_is_white = True
			self.computer_is_black = False
		
		# If computer plays white, make the first move
		if self.computer_is_white and self.board_state.white_turn:
			self.trigger_computer_move()

	def trigger_computer_move(self):
		"""Start computer move calculation in a separate thread"""
		if self.computer_thinking or self.game_over or self.promotion_pending:
			return
		
		# Check if it's the computer's turn
		is_computer_turn = (self.board_state.white_turn and self.computer_is_white) or \
						   (not self.board_state.white_turn and self.computer_is_black)
		
		if not is_computer_turn:
			return
		
		self.computer_thinking = True
		self.computer_move_thread = threading.Thread(target=self.calculate_computer_move)
		self.computer_move_thread.daemon = True
		self.computer_move_thread.start()

	def calculate_computer_move(self):
		"""Calculate and execute computer move (runs in separate thread)"""
		try:
			# Add a small delay for visual feedback
			time.sleep(0.5)
			
			# Get the best move from AI engine
			from_pos, to_pos, score = self.ai_engine.get_best_move(
				self.board_state, self.board_state.white_turn
			)
			
			if from_pos is not None and to_pos is not None:
				# Execute the move on the main thread
				self.execute_computer_move(from_pos, to_pos)
			
		except Exception as e:
			print(f"Computer move calculation error: {e}")
		finally:
			self.computer_thinking = False

	def execute_computer_move(self, from_pos, to_pos):
		"""Execute the computer's move on the board"""
		piece = self.board_state.board[from_pos]
		
		# Check if this is a promotion move (for computer pawns)
		if PawnMoves.is_promotion_move(from_pos, to_pos, piece):
			# Computer always promotes to queen for simplicity
			promoted_piece = 'Q' if piece.isupper() else 'q'
			self.board_state.make_promotion_move(from_pos, to_pos, promoted_piece)
		
		# Check if this is a castling move
		elif piece == 'K' and from_pos == 60:  # White king from e1
			if to_pos == 62:  # Kingside castling to g1
				self.board_state.make_castling_move(60, 62, 63, 61)
			elif to_pos == 58:  # Queenside castling to c1
				self.board_state.make_castling_move(60, 58, 56, 59)
			else:
				self.board_state.make_move(from_pos, to_pos)
		elif piece == 'k' and from_pos == 4:  # Black king from e8
			if to_pos == 6:  # Kingside castling to g8
				self.board_state.make_castling_move(4, 6, 7, 5)
			elif to_pos == 2:  # Queenside castling to c8
				self.board_state.make_castling_move(4, 2, 0, 3)
			else:
				self.board_state.make_move(from_pos, to_pos)
		else:
			# Regular move
			self.board_state.make_move(from_pos, to_pos)
		
		# Save board state after computer move
		self.save_board_state()
		
		# Check for game-ending conditions
		self.game_status = self.mate_detector.get_game_status(self.board_state)
		if self.game_status in ['checkmate', 'stalemate', 'repetition_draw', 'fifty_move_draw']:
			self.game_over = True
			if self.game_status == 'repetition_draw':
				print("3-fold repetition detected! Game is a draw.")

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
		
		if not self.game_over:
			self.game_status = self.mate_detector.get_game_status(self.board_state)
		
		if self.game_status == 'checkmate':
			winner = "Black" if self.board_state.white_turn else "White"
			# Check if winner is human or computer
			if (winner == "White" and self.computer_is_white) or (winner == "Black" and self.computer_is_black):
				turn_text = f"Checkmate! Computer ({winner}) Wins!"
			else:
				turn_text = f"Checkmate! {winner} Wins!"
			text_color = (255, 0, 0)
			bg_color = (255, 255, 255)
			if not self.game_over:  # Only set game_over and clear if not already done
				self.game_over = True
				self.clear_game_file()  # Clear game.txt when game ends
				self.clear_algebraic_file()  # Clear game_.txt when game ends
		elif self.game_status == 'stalemate':
			turn_text = "Stalemate! Draw!"
			text_color = (128, 128, 128)
			bg_color = (255, 255, 255)
			if not self.game_over:  # Only set game_over and clear if not already done
				self.game_over = True
				self.clear_game_file()  # Clear game.txt when game ends
				self.clear_algebraic_file()  # Clear game_.txt when game ends
		elif self.game_status == 'repetition_draw':
			turn_text = "Draw by 3-fold repetition!"
			text_color = (0, 0, 255)  # Blue for repetition draw
			bg_color = (255, 255, 255)
			if not self.game_over:  # Only set game_over and clear if not already done
				self.game_over = True
				self.clear_game_file()  # Clear game.txt when game ends
				self.clear_algebraic_file()  # Clear game_.txt when game ends
		elif self.game_status == 'fifty_move_draw':
			turn_text = "Draw by 50-move rule!"
			text_color = (128, 0, 128)  # Purple for 50-move draw
			bg_color = (255, 255, 255)
			if not self.game_over:  # Only set game_over and clear if not already done
				self.game_over = True
				self.clear_game_file()  # Clear game.txt when game ends
				self.clear_algebraic_file()  # Clear game_.txt when game ends
		elif self.game_status == 'check':
			current_player = "White" if self.board_state.white_turn else "Black"
			is_computer = (self.board_state.white_turn and self.computer_is_white) or \
						  (not self.board_state.white_turn and self.computer_is_black)
			
			if self.computer_thinking:
				turn_text = f"Check! Computer ({current_player}) Thinking..."
			elif is_computer:
				turn_text = f"Check! Computer's ({current_player}) Turn"
			else:
				turn_text = f"Check! {current_player}'s Turn"
			text_color = (255, 0, 0)
			bg_color = (255, 255, 255)
		else:
			current_player = "White" if self.board_state.white_turn else "Black"
			is_computer = (self.board_state.white_turn and self.computer_is_white) or \
						  (not self.board_state.white_turn and self.computer_is_black)
			
			if self.computer_thinking:
				turn_text = f"Computer ({current_player}) Thinking..."
				text_color = (0, 128, 255)  # Blue for thinking
			elif is_computer:
				turn_text = f"Computer's ({current_player}) Turn"
				text_color = (255, 255, 255) if self.board_state.white_turn else (0, 0, 0)
			else:
				turn_text = f"{current_player}'s Turn"
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

	def draw_promotion_dialog(self):
		"""Draw promotion piece selection dialog"""
		if not self.promotion_pending:
			return
			
		# Draw semi-transparent overlay
		overlay = pygame.Surface((self.width, self.height))
		overlay.set_alpha(128)
		overlay.fill((0, 0, 0))
		self.screen.blit(overlay, (0, 0))
		
		# Dialog dimensions
		dialog_width = 280
		dialog_height = 120
		dialog_x = (self.width - dialog_width) // 2
		dialog_y = (self.height - dialog_height) // 2
		
		# Draw dialog background
		dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
		pygame.draw.rect(self.screen, (240, 240, 240), dialog_rect)
		pygame.draw.rect(self.screen, (0, 0, 0), dialog_rect, 2)
		
		# Draw title
		font = pygame.font.Font(None, 24)
		title_text = "Choose promotion piece:"
		title_surface = font.render(title_text, True, (0, 0, 0))
		title_rect = title_surface.get_rect()
		title_rect.centerx = dialog_x + dialog_width // 2
		title_rect.y = dialog_y + 10
		self.screen.blit(title_surface, title_rect)
		
		# Draw piece options
		piece_size = 50
		piece_spacing = 60
		start_x = dialog_x + (dialog_width - (4 * piece_spacing - 10)) // 2
		start_y = dialog_y + 50
		
		# Determine piece color based on the piece that's being promoted (not current turn)
		promoting_piece = self.board_state.board[self.promotion_from]
		is_white = promoting_piece.isupper()
		piece_color = "white" if is_white else "black"
		
		for i, piece_type in enumerate(self.promotion_pieces):
			piece_x = start_x + i * piece_spacing
			piece_y = start_y
			
			# Draw piece background
			piece_rect = pygame.Rect(piece_x, piece_y, piece_size, piece_size)
			pygame.draw.rect(self.screen, (200, 200, 200), piece_rect)
			pygame.draw.rect(self.screen, (0, 0, 0), piece_rect, 1)
			
			# Draw piece image
			piece_name = f"{piece_color}_{self.get_piece_name(piece_type)}"
			img_key = f"{piece_name}_light"
			if img_key in self.images:
				img = pygame.transform.scale(self.images[img_key], (piece_size - 4, piece_size - 4))
				self.screen.blit(img, (piece_x + 2, piece_y + 2))

	def get_piece_name(self, piece_type):
		"""Convert piece letter to piece name"""
		piece_names = {
			'Q': 'queen',
			'R': 'rook', 
			'B': 'bishop',
			'N': 'knight'
		}
		return piece_names.get(piece_type, 'queen')

	def handle_promotion_click(self, mouse_x, mouse_y):
		"""Handle clicks on promotion dialog"""
		if not self.promotion_pending:
			return False
			
		dialog_width = 280
		dialog_height = 120
		dialog_x = (self.width - dialog_width) // 2
		dialog_y = (self.height - dialog_height) // 2
		
		piece_size = 50
		piece_spacing = 60
		start_x = dialog_x + (dialog_width - (4 * piece_spacing - 10)) // 2
		start_y = dialog_y + 50
		
		for i, piece_type in enumerate(self.promotion_pieces):
			piece_x = start_x + i * piece_spacing
			piece_y = start_y
			
			if (piece_x <= mouse_x <= piece_x + piece_size and 
				piece_y <= mouse_y <= piece_y + piece_size):
				
				# Execute promotion
				promoting_piece = self.board_state.board[self.promotion_from]
				is_white = promoting_piece.isupper()
				promoted_piece = piece_type if is_white else piece_type.lower()
				self.board_state.make_promotion_move(self.promotion_from, self.promotion_to, promoted_piece)
				
				# Save board state after promotion
				self.save_board_state()
				
				# Check for game-ending conditions immediately after promotion
				self.game_status = self.mate_detector.get_game_status(self.board_state)
				if self.game_status in ['checkmate', 'stalemate', 'repetition_draw']:
					self.game_over = True
					if self.game_status == 'repetition_draw':
						print("3-fold repetition detected! Game is a draw.")
					# Don't clear file here - let draw_turn_indicator handle it
				
				# Reset promotion state
				self.promotion_pending = False
				self.promotion_from = None
				self.promotion_to = None
				self.selected_piece = None
				self.valid_moves = []
				
				# Trigger computer move after promotion if game isn't over
				if not self.game_over:
					self.trigger_computer_move()
				
				return True
		
		return False

	def save_board_state(self):
		"""Append the current board state to game.txt"""
		try:
			with open("game.txt", "a") as f:
				f.write(f"{self.board_state.board}\n")
			
			# Update algebraic notation after saving board state
			self.update_algebraic_notation()
		except Exception as e:
			print(f"Error saving board state: {e}")

	def update_algebraic_notation(self):
		"""Update the algebraic notation file with the latest move"""
		try:
			# Read all board states from game.txt
			with open("game.txt", "r") as f:
				board_states = [line.strip() for line in f.readlines() if line.strip()]
			
			# If we have at least 2 board states, we can convert the latest move
			if len(board_states) >= 2:
				# Only convert the latest move (incremental approach)
				old_board = board_states[-2]
				new_board = board_states[-1]
				
				# Determine whose turn it was (starts with white=True for first move)
				is_white_turn = (len(board_states) % 2 == 0)
				
				# Convert the latest move to algebraic notation
				move_notation = self.notation_converter.convert_move_to_algebraic(
					old_board, new_board, is_white_turn
				)
				
				if move_notation and move_notation != "UNKNOWN_MOVE":
					# Add check/checkmate notation
					if self.notation_converter.is_checkmate(new_board, is_white_turn):
						move_notation += "#"
					elif self.notation_converter.is_check(new_board, is_white_turn):
						move_notation += "+"
					
					# Append to algebraic notation file
					self.append_algebraic_move(move_notation, is_white_turn)
		except Exception as e:
			print(f"Error updating algebraic notation: {e}")

	def append_algebraic_move(self, move_notation, is_white_turn):
		"""Append a move to the algebraic notation file"""
		try:
			# Read existing content
			try:
				with open("game_.txt", "r") as f:
					existing_content = f.read().strip()
			except FileNotFoundError:
				existing_content = ""
			
			# Simple format: just append moves separated by spaces
			if existing_content:
				new_content = f"{existing_content} {move_notation}"
			else:
				new_content = move_notation
			
			# Write updated content
			with open("game_.txt", "w") as f:
				f.write(new_content)
				
		except Exception as e:
			print(f"Error appending algebraic move: {e}")

	def clear_algebraic_file(self):
		"""Clear the game_.txt file"""
		try:
			with open("game_.txt", "w") as f:
				f.write("")  # Clear the file
			self.move_count = 0  # Reset move counter
		except Exception as e:
			print(f"Error clearing algebraic file: {e}")

	def clear_game_file(self):
		"""Clear the game.txt file when game is complete"""
		try:
			with open("game.txt", "w") as f:
				f.write("")  # Clear the file
		except Exception as e:
			print(f"Error clearing game file: {e}")

	def restart_game(self):
		"""Restart the game to initial state"""
		self.board_state = BoardRepresentation()
		self.selected_piece = None
		self.valid_moves = []
		self.game_over = False
		self.game_status = 'normal'
		self.promotion_pending = False
		self.promotion_from = None
		self.promotion_to = None
		self.computer_thinking = False
		self.show_mode_selection = True
		self.game_mode = None
		self.computer_is_white = False
		self.computer_is_black = False
		self.clear_game_file()  # Clear game.txt when restarting
		self.clear_algebraic_file()  # Clear game_.txt when restarting
		self.save_board_state()  # Save the initial position

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
			elif event.type == pygame.KEYDOWN:
				# Handle game mode selection
				if self.show_mode_selection:
					if event.key == pygame.K_1:
						self.set_game_mode("hvh")
					elif event.key == pygame.K_2:
						self.set_game_mode("hvc_white")
					elif event.key == pygame.K_3:
						self.set_game_mode("hvc_black")
				elif event.key == pygame.K_r and self.game_over:  # Press 'R' to restart when game is over
					self.restart_game()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:  # Left click
					# Skip mouse handling if in mode selection
					if self.show_mode_selection:
						return
					
					mouse_x, mouse_y = event.pos
					
					# Check if clicking on promotion dialog
					if self.promotion_pending:
						self.handle_promotion_click(mouse_x, mouse_y)
						return
					
					# Skip mouse handling if computer is thinking
					if self.computer_thinking:
						return
					
					# Only handle board clicks if game is not over
					if not self.game_over:
						col = mouse_x // self.square_size
						row = mouse_y // self.square_size
						
						pos = row * 8 + col
						piece = self.board_state.board[pos]

						# Check if it's a human player's turn
						is_human_turn = (self.board_state.white_turn and not self.computer_is_white) or \
									   (not self.board_state.white_turn and not self.computer_is_black)
						
						if not is_human_turn:
							return  # It's computer's turn, ignore clicks

						# Only allow selecting pieces that belong to the current player
						if piece != '.' and self.is_current_player_piece(piece):
							self.selected_piece = pos
							self.valid_moves = MoveValidator.get_valid_moves(self.board_state, pos, piece)

						elif self.selected_piece is not None:
							if pos in self.valid_moves:
								print(f"Moving piece from {self.selected_piece} to {pos}")
								
								piece = self.board_state.board[self.selected_piece]
								
								# Check if this is a promotion move
								if PawnMoves.is_promotion_move(self.selected_piece, pos, piece):
									self.promotion_pending = True
									self.promotion_from = self.selected_piece
									self.promotion_to = pos
									return  # Don't make the move yet, wait for promotion choice
								
								# Check if this is an en passant move
								is_en_passant = PawnMoves.is_en_passant_move(self.board_state, self.selected_piece, pos, piece)
								
								# Check if this is a castling move
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
								
								# Save board state after castling
								if is_castling:
									self.save_board_state()
									
									# Check for game-ending conditions immediately after castling
									self.game_status = self.mate_detector.get_game_status(self.board_state)
									if self.game_status in ['checkmate', 'stalemate', 'repetition_draw']:
										self.game_over = True
										if self.game_status == 'repetition_draw':
											print("3-fold repetition detected! Game is a draw.")
										# Don't clear file here - let draw_turn_indicator handle it
								
								if not is_castling:
									if is_en_passant:
										print(f"En passant capture from {self.selected_piece} to {pos}")
									self.board_state.make_move(self.selected_piece, pos)
								
								# Save board state after move
								self.save_board_state()
								
								# Check for game-ending conditions immediately after move
								self.game_status = self.mate_detector.get_game_status(self.board_state)
								if self.game_status in ['checkmate', 'stalemate', 'repetition_draw']:
									self.game_over = True
									if self.game_status == 'repetition_draw':
										print("3-fold repetition detected! Game is a draw.")
									# Don't clear file here - let draw_turn_indicator handle it
								
								# Clear selection after human move
								self.selected_piece = None
								self.valid_moves = []
								
								# Trigger computer move after human move
								if not self.game_over:
									self.trigger_computer_move()
								
							else:
								self.selected_piece = None
								self.valid_moves = []


	def run(self):
		while self.running:
			self.handle_events()
			self.screen.fill((0, 0, 0))
			
			if self.show_mode_selection:
				self.draw_mode_selection()
			else:
				self.draw_board()
				self.draw_promotion_dialog()  # Draw promotion dialog on top
			
			pygame.display.flip()
			self.clock.tick(60)
		
		pygame.quit()