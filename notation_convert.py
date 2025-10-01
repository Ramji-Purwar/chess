class AlgebraicNotationConverter:
    def __init__(self):
        self.piece_symbols = {
            'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': '',
            'k': 'K', 'q': 'Q', 'r': 'R', 'b': 'B', 'n': 'N', 'p': ''
        }
        
        self.files = 'abcdefgh'
        self.ranks = '87654321'
        
    def index_to_algebraic(self, index):
        if not (0 <= index <= 63):
            return None
        
        file_index = index % 8
        rank_index = index // 8
        
        return f"{self.files[file_index]}{self.ranks[rank_index]}"
    
    def algebraic_to_index(self, algebraic):
        if len(algebraic) != 2:
            return None
            
        file_char = algebraic[0].lower()
        rank_char = algebraic[1]
        
        if file_char not in self.files or rank_char not in self.ranks:
            return None
            
        file_index = self.files.index(file_char)
        rank_index = self.ranks.index(rank_char)
        
        return rank_index * 8 + file_index
    
    def get_piece_at(self, board, index):
        if 0 <= index <= 63:
            return board[index]
        return '.'
    
    def is_white_piece(self, piece):
        return piece.isupper() and piece != '.'
    
    def is_black_piece(self, piece):
        return piece.islower() and piece != '.'
    
    def find_differences(self, old_board, new_board):
        differences = []
        for i in range(64):
            if old_board[i] != new_board[i]:
                differences.append({
                    'index': i,
                    'position': self.index_to_algebraic(i),
                    'old_piece': old_board[i],
                    'new_piece': new_board[i]
                })
        return differences
    
    def detect_castling(self, differences, is_white_turn):
        if len(differences) != 4:
            return None
            
        king_moves = []
        rook_moves = []
        
        for diff in differences:
            old_piece = diff['old_piece']
            new_piece = diff['new_piece']
            
            if is_white_turn and old_piece == 'K' and new_piece == '.':
                king_moves.append(('from', diff['index']))
            elif is_white_turn and old_piece == '.' and new_piece == 'K':
                king_moves.append(('to', diff['index']))
            elif not is_white_turn and old_piece == 'k' and new_piece == '.':
                king_moves.append(('from', diff['index']))
            elif not is_white_turn and old_piece == '.' and new_piece == 'k':
                king_moves.append(('to', diff['index']))
                
            elif is_white_turn and old_piece == 'R' and new_piece == '.':
                rook_moves.append(('from', diff['index']))
            elif is_white_turn and old_piece == '.' and new_piece == 'R':
                rook_moves.append(('to', diff['index']))
            elif not is_white_turn and old_piece == 'r' and new_piece == '.':
                rook_moves.append(('from', diff['index']))
            elif not is_white_turn and old_piece == '.' and new_piece == 'r':
                rook_moves.append(('to', diff['index']))
        
        if len(king_moves) == 2 and len(rook_moves) == 2:
            king_from = next((move[1] for move in king_moves if move[0] == 'from'), None)
            king_to = next((move[1] for move in king_moves if move[0] == 'to'), None)
            
            if king_from is not None and king_to is not None:
                if abs(king_to - king_from) == 2:
                    if king_to > king_from:
                        return "O-O"  
                    else:
                        return "O-O-O"

        return None
    
    def detect_en_passant(self, differences, is_white_turn):
        if len(differences) != 3:
            return None
            
        pawn_moves = []
        captured_pawn = None
        
        for diff in differences:
            old_piece = diff['old_piece']
            new_piece = diff['new_piece']
            
            if is_white_turn and old_piece == 'P' and new_piece == '.':
                pawn_moves.append(('from', diff['index']))
            elif is_white_turn and old_piece == '.' and new_piece == 'P':
                pawn_moves.append(('to', diff['index']))
            elif not is_white_turn and old_piece == 'p' and new_piece == '.':
                pawn_moves.append(('from', diff['index']))
            elif not is_white_turn and old_piece == '.' and new_piece == 'p':
                pawn_moves.append(('to', diff['index']))
            
            elif (is_white_turn and old_piece == 'p' and new_piece == '.') or \
                 (not is_white_turn and old_piece == 'P' and new_piece == '.'):
                captured_pawn = diff['index']
        
        if len(pawn_moves) == 2 and captured_pawn is not None:
            from_square = next((move[1] for move in pawn_moves if move[0] == 'from'), None)
            to_square = next((move[1] for move in pawn_moves if move[0] == 'to'), None)
            
            if from_square is not None and to_square is not None:
                from_file = from_square % 8
                to_file = to_square % 8
                if abs(from_file - to_file) == 1:
                    return {
                        'from': from_square,
                        'to': to_square,
                        'captured': captured_pawn,
                        'type': 'en_passant'
                    }
        
        return None
    
    def detect_promotion(self, differences, is_white_turn):
        if len(differences) != 2:
            return None
            
        pawn_disappears = None
        piece_appears = None
        
        for diff in differences:
            old_piece = diff['old_piece']
            new_piece = diff['new_piece']
            
            if is_white_turn and old_piece == 'P' and new_piece == '.':
                pawn_disappears = diff['index']
            elif not is_white_turn and old_piece == 'p' and new_piece == '.':
                pawn_disappears = diff['index']
            
            elif is_white_turn and old_piece in ['.', 'p', 'r', 'n', 'b', 'q'] and new_piece in ['Q', 'R', 'B', 'N']:
                piece_appears = {'index': diff['index'], 'piece': new_piece, 'captured': old_piece}
            elif not is_white_turn and old_piece in ['.', 'P', 'R', 'N', 'B', 'Q'] and new_piece in ['q', 'r', 'b', 'n']:
                piece_appears = {'index': diff['index'], 'piece': new_piece, 'captured': old_piece}
        
        if pawn_disappears is not None and piece_appears is not None:
            pawn_rank = pawn_disappears // 8
            promotion_rank = piece_appears['index'] // 8
            
            if (is_white_turn and pawn_rank == 1 and promotion_rank == 0) or \
               (not is_white_turn and pawn_rank == 6 and promotion_rank == 7):
                return {
                    'from': pawn_disappears,
                    'to': piece_appears['index'],
                    'promoted_to': piece_appears['piece'],
                    'captured': piece_appears['captured'] if piece_appears['captured'] != '.' else None,
                    'type': 'promotion'
                }
        
        return None
    
    def find_ambiguous_pieces(self, board, piece_type, target_square, is_white_turn):
        ambiguous_pieces = []
        
        for i in range(64):
            piece = board[i]
            if piece == '.' or (is_white_turn and not self.is_white_piece(piece)) or \
               (not is_white_turn and not self.is_black_piece(piece)):
                continue
                
            piece_lower = piece.lower()
            if piece_lower == piece_type.lower():
                if self.can_piece_move_to(piece_lower, i, target_square, board):
                    ambiguous_pieces.append(i)
        
        return ambiguous_pieces
    
    def can_piece_move_to(self, piece_type, from_square, to_square, board):
        from_file = from_square % 8
        from_rank = from_square // 8
        to_file = to_square % 8
        to_rank = to_square // 8
        
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)
        
        if piece_type == 'p': 
            return file_diff <= 1 and rank_diff == 1
        elif piece_type == 'r':  
            return file_diff == 0 or rank_diff == 0
        elif piece_type == 'n':  
            return (file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2)
        elif piece_type == 'b':  
            return file_diff == rank_diff
        elif piece_type == 'q':  
            return file_diff == rank_diff or file_diff == 0 or rank_diff == 0
        elif piece_type == 'k':  
            return file_diff <= 1 and rank_diff <= 1
        
        return False
    
    def get_disambiguation(self, from_square, ambiguous_pieces):
        if len(ambiguous_pieces) <= 1:
            return ''
        
        from_file = from_square % 8
        from_rank = from_square // 8
        
        same_file_pieces = [p for p in ambiguous_pieces if p % 8 == from_file and p != from_square]
        if not same_file_pieces:
            return self.files[from_file]
        
        same_rank_pieces = [p for p in ambiguous_pieces if p // 8 == from_rank and p != from_square]
        if not same_rank_pieces:
            return self.ranks[from_rank]
        
        return f"{self.files[from_file]}{self.ranks[from_rank]}"
    
    def is_check(self, board, is_white_turn_after_move):
        try:
            from check_detector import CheckDetector
            
            detector = CheckDetector()
            if is_white_turn_after_move:
                return detector.is_black_king_in_check(board)
            else:
                return detector.is_white_king_in_check(board)
        except ImportError:
            return False
    
    def is_checkmate(self, board, is_white_turn_after_move):
        try:
            from mate_detector import MateDetector
            from board import BoardRepresentation
            
            board_rep = BoardRepresentation()
            board_rep.board = board
            board_rep.white_turn = not is_white_turn_after_move
            
            detector = MateDetector()
            return detector.is_checkmate(board_rep)
        except ImportError:
            return False
    
    def convert_move_to_algebraic(self, old_board, new_board, is_white_turn):
        differences = self.find_differences(old_board, new_board)
        
        if not differences:
            return ""
        
        castling = self.detect_castling(differences, is_white_turn)
        if castling:
            return castling
        
        en_passant = self.detect_en_passant(differences, is_white_turn)
        if en_passant:
            from_pos = self.index_to_algebraic(en_passant['from'])
            to_pos = self.index_to_algebraic(en_passant['to'])
            return f"{from_pos[0]}x{to_pos}"
        
        promotion = self.detect_promotion(differences, is_white_turn)
        if promotion:
            from_pos = self.index_to_algebraic(promotion['from'])
            to_pos = self.index_to_algebraic(promotion['to'])
            promoted_piece = promotion['promoted_to'].upper()
            capture_notation = 'x' if promotion['captured'] else ''
            if promotion['captured']:
                return f"{from_pos[0]}{capture_notation}{to_pos}={promoted_piece}"
            else:
                return f"{to_pos}={promoted_piece}"
        
        if len(differences) == 2:
            from_square = None
            to_square = None
            moving_piece = None
            captured_piece = None
            
            for diff in differences:
                if diff['old_piece'] != '.' and diff['new_piece'] == '.':
                    from_square = diff['index']
                    moving_piece = diff['old_piece']
                elif diff['old_piece'] != diff['new_piece'] and diff['new_piece'] != '.':
                    to_square = diff['index']
                    captured_piece = diff['old_piece'] if diff['old_piece'] != '.' else None
            
            if from_square is not None and to_square is not None and moving_piece is not None:
                piece_symbol = self.piece_symbols[moving_piece]
                from_pos = self.index_to_algebraic(from_square)
                to_pos = self.index_to_algebraic(to_square)
                
                ambiguous_pieces = self.find_ambiguous_pieces(old_board, moving_piece, to_square, is_white_turn)
                disambiguation = self.get_disambiguation(from_square, ambiguous_pieces)
                
                capture_notation = 'x' if captured_piece else ''
                
                if moving_piece.lower() == 'p' and captured_piece:
                    return f"{from_pos[0]}x{to_pos}"
                elif moving_piece.lower() == 'p' and not captured_piece:
                    return to_pos
                else:
                    return f"{piece_symbol}{disambiguation}{capture_notation}{to_pos}"
        
        return "UNKNOWN_MOVE"
    
    def convert_move_to_coordinate(self, old_board, new_board):
        differences = self.find_differences(old_board, new_board)
        
        if not differences:
            return ""
        
        castling = self.detect_castling(differences, True)
        if castling:
            if castling == "O-O": 
                for diff in differences:
                    if diff['old_piece'] in ['K', 'k'] and diff['new_piece'] == '.':
                        from_square = diff['index']
                        from_pos = self.index_to_algebraic(from_square)
                        if from_pos == 'e1':  
                            return "e1g1"
                        elif from_pos == 'e8':
                            return "e8g8"
            elif castling == "O-O-O":
                for diff in differences:
                    if diff['old_piece'] in ['K', 'k'] and diff['new_piece'] == '.':
                        from_square = diff['index']
                        from_pos = self.index_to_algebraic(from_square)
                        if from_pos == 'e1': 
                            return "e1c1"
                        elif from_pos == 'e8':
                            return "e8c8"
        
        if len(differences) >= 2:
            from_square = None
            to_square = None
            
            for diff in differences:
                if diff['old_piece'] != '.' and diff['new_piece'] == '.':
                    from_square = diff['index']
                elif diff['old_piece'] != diff['new_piece'] and diff['new_piece'] != '.':
                    to_square = diff['index']
            
            if from_square is not None and to_square is not None:
                from_pos = self.index_to_algebraic(from_square)
                to_pos = self.index_to_algebraic(to_square)
                return f"{from_pos}{to_pos}"
        
        return ""

    def convert_game_to_coordinate_notation(self, input_file="game.txt", output_file="game_sequence.txt"):
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            board_states = [line.strip() for line in lines if line.strip()]
            
            if len(board_states) < 2:
                return []
            
            for i, board in enumerate(board_states):
                if len(board) != 64:
                    print(f"Error: Board state {i+1} has {len(board)} characters, expected 64")
                    return []
            
            coordinate_moves = []
            
            for i in range(1, len(board_states)):
                old_board = board_states[i-1]
                new_board = board_states[i]
                
                move_coordinate = self.convert_move_to_coordinate(old_board, new_board)
                
                if move_coordinate:
                    coordinate_moves.append(move_coordinate)
            
            move_sequence = "-".join(coordinate_moves)
            
            with open(output_file, 'w') as f:
                f.write(move_sequence)
            
            return coordinate_moves
            
        except FileNotFoundError:
            print(f"Error: {input_file} not found")
            return []
        except Exception as e:
            print(f"Error converting to coordinate notation: {e}")
            return []

    def get_current_move_sequence(self, board_states_list):
        if len(board_states_list) < 2:
            return ""
        
        coordinate_moves = []
        
        for i in range(1, len(board_states_list)):
            old_board = board_states_list[i-1]
            new_board = board_states_list[i]
            
            move_coordinate = self.convert_move_to_coordinate(old_board, new_board)
            
            if move_coordinate:
                coordinate_moves.append(move_coordinate)
        
        return "-".join(coordinate_moves)

    def convert_game_to_algebraic(self, input_file="game.txt", output_file="game_.txt"):
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            board_states = [line.strip() for line in lines if line.strip()]
            
            if len(board_states) < 2:
                print("Need at least 2 board states to generate moves")
                return
            
            for i, board in enumerate(board_states):
                if len(board) != 64:
                    print(f"Error: Board state {i+1} has {len(board)} characters, expected 64")
                    return
            
            algebraic_moves = []
            is_white_turn = True  
            
            for i in range(1, len(board_states)):
                old_board = board_states[i-1]
                new_board = board_states[i]
                
                move_notation = self.convert_move_to_algebraic(old_board, new_board, is_white_turn)
                
                if move_notation and move_notation != "UNKNOWN_MOVE":
                    if self.is_checkmate(new_board, is_white_turn):
                        move_notation += "#"
                    elif self.is_check(new_board, is_white_turn):
                        move_notation += "+"
                    
                    algebraic_moves.append(move_notation)
                
                is_white_turn = not is_white_turn
            
            formatted_game = self.format_game_notation(algebraic_moves)
            
            with open(output_file, 'w') as f:
                f.write(formatted_game)
            
            print(f"Game converted to algebraic notation and saved to {output_file}")
            print(f"Generated {len(algebraic_moves)} moves")
            
        except FileNotFoundError:
            print(f"Error: {input_file} not found")
        except Exception as e:
            print(f"Error converting game: {e}")
    
    def format_game_notation(self, moves):
        if not moves:
            return ""
        
        formatted = []
        for i in range(0, len(moves), 2):
            move_number = (i // 2) + 1
            white_move = moves[i] if i < len(moves) else ""
            black_move = moves[i + 1] if i + 1 < len(moves) else ""
            
            if black_move:
                formatted.append(f"{move_number}. {white_move} {black_move}")
            else:
                formatted.append(f"{move_number}. {white_move}")
        
        return " ".join(formatted)


def main():
    converter = AlgebraicNotationConverter()
    converter.convert_game_to_algebraic()

def convert_game_file(input_file="game.txt", output_file="game_.txt"):
    converter = AlgebraicNotationConverter()
    converter.convert_game_to_algebraic(input_file, output_file)

if __name__ == "__main__":
    main()
