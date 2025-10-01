from board import BoardRepresentation

class CheckDetector:
    def checked(self, board: BoardRepresentation, white_turn: bool) -> bool:
        if white_turn:
            return self.is_white_king_in_check(board.board)
        else:
            return self.is_black_king_in_check(board.board)
    
    def is_white_king_in_check(self, board_string: str) -> bool:
        """Check if white king is under attack by any black piece"""
        king_pos = board_string.index('K')
        king_row = king_pos // 8
        king_col = king_pos % 8
        
        if self.is_attacked_by_black_pawn(board_string, king_row, king_col):
            return True
        
        if self.is_attacked_horizontally_vertically(board_string, king_row, king_col, 'rq'):
            return True
        
        if self.is_attacked_diagonally(board_string, king_row, king_col, 'bq'):
            return True
        
        if self.is_attacked_by_knight(board_string, king_row, king_col, 'n'):
            return True

        if self.is_attacked_by_king(board_string, king_row, king_col, 'k'):
            return True
        
        return False
    
    def is_black_king_in_check(self, board_string: str) -> bool:
        king_pos = board_string.index('k')
        king_row = king_pos // 8
        king_col = king_pos % 8
        
        if self.is_attacked_by_white_pawn(board_string, king_row, king_col):
            return True
        
        if self.is_attacked_horizontally_vertically(board_string, king_row, king_col, 'RQ'):
            return True

        if self.is_attacked_diagonally(board_string, king_row, king_col, 'BQ'):
            return True

        if self.is_attacked_by_knight(board_string, king_row, king_col, 'N'):
            return True
        
        if self.is_attacked_by_king(board_string, king_row, king_col, 'K'):
            return True
        
        return False
    
    def is_attacked_by_white_pawn(self, board_string: str, row: int, col: int) -> bool:
        for dc in [-1, 1]: 
            attack_row = row + 1  
            attack_col = col + dc
            if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                if board_string[attack_row * 8 + attack_col] == 'P':
                    return True
        return False
    
    def is_attacked_by_black_pawn(self, board_string: str, row: int, col: int) -> bool:
        for dc in [-1, 1]:  
            attack_row = row - 1  
            attack_col = col + dc
            if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                if board_string[attack_row * 8 + attack_col] == 'p':
                    return True
        return False
    
    def is_attacked_horizontally_vertically(self, board_string: str, row: int, col: int, attackers: str) -> bool:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board_string[r * 8 + c]
                if piece != '.':
                    if piece in attackers:
                        return True
                    break
                r += dr
                c += dc
        return False
    
    def is_attacked_diagonally(self, board_string: str, row: int, col: int, attackers: str) -> bool:
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board_string[r * 8 + c]
                if piece != '.':
                    if piece in attackers:
                        return True
                    break
                r += dr
                c += dc
        return False
    
    def is_attacked_by_knight(self, board_string: str, row: int, col: int, attacker: str) -> bool:
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