from board import BoardRepresentation

class CheckDetector:
    def checked(self, board: BoardRepresentation, white_turn: bool) -> bool:
        if white_turn:
            # If it's white's turn, check if white king is under attack
            return self.is_white_king_in_check(board.board)
        else:
            # If it's black's turn, check if black king is under attack
            return self.is_black_king_in_check(board.board)
    
    def is_white_king_in_check(self, board_string: str) -> bool:
        """Check if white king is under attack by any black piece"""
        king_pos = board_string.index('K')
        king_row = king_pos // 8
        king_col = king_pos % 8
        
        # Check for pawn attacks
        if self.is_attacked_by_black_pawn(board_string, king_row, king_col):
            return True
        
        # Check for rook/queen attacks (horizontal/vertical)
        if self.is_attacked_horizontally_vertically(board_string, king_row, king_col, 'rq'):
            return True
        
        # Check for bishop/queen attacks (diagonal)
        if self.is_attacked_diagonally(board_string, king_row, king_col, 'bq'):
            return True
        
        # Check for knight attacks
        if self.is_attacked_by_knight(board_string, king_row, king_col, 'n'):
            return True
        
        # Check for king attacks
        if self.is_attacked_by_king(board_string, king_row, king_col, 'k'):
            return True
        
        return False
    
    def is_black_king_in_check(self, board_string: str) -> bool:
        """Check if black king is under attack by any white piece"""
        king_pos = board_string.index('k')
        king_row = king_pos // 8
        king_col = king_pos % 8
        
        # Check for pawn attacks
        if self.is_attacked_by_white_pawn(board_string, king_row, king_col):
            return True
        
        # Check for rook/queen attacks (horizontal/vertical)
        if self.is_attacked_horizontally_vertically(board_string, king_row, king_col, 'RQ'):
            return True
        
        # Check for bishop/queen attacks (diagonal)
        if self.is_attacked_diagonally(board_string, king_row, king_col, 'BQ'):
            return True
        
        # Check for knight attacks
        if self.is_attacked_by_knight(board_string, king_row, king_col, 'N'):
            return True
        
        # Check for king attacks
        if self.is_attacked_by_king(board_string, king_row, king_col, 'K'):
            return True
        
        return False
    
    def is_attacked_by_white_pawn(self, board_string: str, row: int, col: int) -> bool:
        """Check if position is attacked by white pawn"""
        # White pawns attack diagonally upward (decreasing row)
        for dc in [-1, 1]:  # Left and right diagonal
            attack_row = row + 1  # White pawns attack from below
            attack_col = col + dc
            if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                if board_string[attack_row * 8 + attack_col] == 'P':
                    return True
        return False
    
    def is_attacked_by_black_pawn(self, board_string: str, row: int, col: int) -> bool:
        """Check if position is attacked by black pawn"""
        # Black pawns attack diagonally downward (increasing row)
        for dc in [-1, 1]:  # Left and right diagonal
            attack_row = row - 1  # Black pawns attack from above
            attack_col = col + dc
            if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                if board_string[attack_row * 8 + attack_col] == 'p':
                    return True
        return False
    
    def is_attacked_horizontally_vertically(self, board_string: str, row: int, col: int, attackers: str) -> bool:
        """Check if position is attacked by rook or queen horizontally/vertically"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board_string[r * 8 + c]
                if piece != '.':
                    if piece in attackers:
                        return True
                    break  # Blocked by any piece
                r += dr
                c += dc
        return False
    
    def is_attacked_diagonally(self, board_string: str, row: int, col: int, attackers: str) -> bool:
        """Check if position is attacked by bishop or queen diagonally"""
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # All diagonal directions
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board_string[r * 8 + c]
                if piece != '.':
                    if piece in attackers:
                        return True
                    break  # Blocked by any piece
                r += dr
                c += dc
        return False
    
    def is_attacked_by_knight(self, board_string: str, row: int, col: int, attacker: str) -> bool:
        """Check if position is attacked by knight"""
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board_string[r * 8 + c] == attacker:
                    return True
        return False
    
    def is_attacked_by_king(self, board_string: str, row: int, col: int, attacker: str) -> bool:
        """Check if position is attacked by enemy king"""
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board_string[r * 8 + c] == attacker:
                    return True
        return False