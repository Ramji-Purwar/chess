from board import BoardRepresentation
from .white_king_capturable import Check_White
from .black_king_capturable import Check_Black

class PawnMoves:
    @staticmethod

    @staticmethod
    def white_pawn_moves(board: BoardRepresentation, r : int, c : int) -> list:
        moves = []
        if(r == 6 and board.board[(r-1)*8 + c] == '.' and board.board[(r-2)*8 + c] == '.'):
            moves.append((r-2)*8 + c)
        if(r > 0 and board.board[(r-1)*8 + c] == '.'):
            moves.append((r-1)*8 + c)
        if(r > 0 and c > 0 and board.board[(r-1)*8 + (c-1)] in 'rnbqkp'):
            moves.append((r-1)*8 + (c-1))
        if(r > 0 and c < 7 and board.board[(r-1)*8 + (c+1)] in 'rnbqkp'):
            moves.append((r-1)*8 + (c+1))
        
        valid_moves = []
        for move in moves:
            clone_board = list(board.board)
            clone_board[r*8 + c] = '.'
            # Check if this move leads to promotion (reaching row 0)
            move_row = move // 8
            if move_row == 0:
                # For promotion moves, temporarily place a queen for validation
                clone_board[move] = 'Q'
            else:
                clone_board[move] = 'P'
            clone_board_str = ''.join(clone_board)
            if not Check_White.white_king_capturable(clone_board_str):
                valid_moves.append(move)

        return valid_moves

    @staticmethod
    def black_pawn_moves(board: BoardRepresentation, r : int, c : int) -> list:
        moves = []
        if(r == 1 and board.board[(r+1)*8 + c] == '.' and board.board[(r+2)*8 + c] == '.'):
            moves.append((r+2)*8 + c)
        if(r < 7 and board.board[(r+1)*8 + c] == '.'):
            moves.append((r+1)*8 + c)
        if(r < 7 and c > 0 and board.board[(r+1)*8 + (c-1)] in 'RNBQKP'):
            moves.append((r+1)*8 + (c-1))
        if(r < 7 and c < 7 and board.board[(r+1)*8 + (c+1)] in 'RNBQKP'):
            moves.append((r+1)*8 + (c+1))

        valid_moves = []
        for move in moves:
            clone_board = list(board.board)
            clone_board[r*8 + c] = '.'
            # Check if this move leads to promotion (reaching row 7)
            move_row = move // 8
            if move_row == 7:
                # For promotion moves, temporarily place a queen for validation
                clone_board[move] = 'q'
            else:
                clone_board[move] = 'p'
            clone_board_str = ''.join(clone_board)
            if not Check_Black.black_king_capturable(clone_board_str):
                valid_moves.append(move)
            
        return valid_moves

    @staticmethod
    def is_promotion_move(start_pos: int, end_pos: int, piece: str) -> bool:
        """Check if a move is a promotion move"""
        end_row = end_pos // 8
        if piece == 'P':  # White pawn
            return end_row == 0  # Reached rank 8 (row 0)
        elif piece == 'p':  # Black pawn
            return end_row == 7  # Reached rank 1 (row 7)
        return False

    @staticmethod
    def get_moves(board: BoardRepresentation, position: int) -> list:
        r = position // 8
        c = position % 8
        moves = []
        if(board.white_turn):
            moves = PawnMoves.white_pawn_moves(board, r, c)
        else:
            moves = PawnMoves.black_pawn_moves(board, r, c)
        return moves