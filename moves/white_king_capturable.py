class Check_White:
    @staticmethod

    @staticmethod
    def capture_diagonally(board : str, R : int, C : int):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            r, c = R + dr, C + dc 
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r * 8 + c]
                if piece != '.':
                    if piece in 'bq':
                        return True
                    break
                r += dr
                c += dc
        
        return False


    @staticmethod
    def capture_horizontally(board : str, R : int, C : int):
        directions = [(0, -1), (0, 1)]
        
        for dr, dc in directions:
            r, c = R + dr, C + dc  
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r * 8 + c]
                if piece != '.': 
                    if piece in 'rq': 
                        return True
                    break
                r += dr
                c += dc

        return False

    @staticmethod
    def capture_vertically(board : str, R : int, C : int):
        directions = [(-1, 0), (1, 0)]
        
        for dr, dc in directions:
            r, c = R + dr, C + dc 
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r * 8 + c]
                if piece != '.': 
                    if piece in 'rq':
                        return True
                    break
                r += dr
                c += dc

        return False
    
    @staticmethod
    def capture_by_knight(board : str, R : int, C : int):
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        for dr, dc in knight_moves:
            r = R + dr
            c = C + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r * 8 + c] in 'n':
                    return True
        return False
    
    @staticmethod
    def capture_by_pawn(board: str, R: int, C: int):
        pawn_attack_positions = [
            (R - 1, C - 1),
            (R - 1, C + 1) 
        ]
        
        for r, c in pawn_attack_positions:
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r * 8 + c] == 'p': 
                    return True
        return False

    @staticmethod
    def white_king_capturable(board):
        king_pos = board.index('K')
        r = king_pos // 8
        c = king_pos % 8
        if Check_White.capture_diagonally(board, r, c):
            return True
        if Check_White.capture_horizontally(board, r, c):
            return True
        if Check_White.capture_vertically(board, r, c):
            return True
        if Check_White.capture_by_knight(board, r, c):
            return True
        if Check_White.capture_by_pawn(board, r, c):
            return True
        
        return False