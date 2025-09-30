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
        
        if r == 3 and board.en_passant_target is not None:
            current_pos = r * 8 + c
            if (c > 0 and board.en_passant_target == current_pos - 8 - 1) or \
               (c < 7 and board.en_passant_target == current_pos - 8 + 1):
                moves.append(board.en_passant_target)
        
        valid_moves = []
        for move in moves:
            clone_board = list(board.board)
            clone_board[r*8 + c] = '.'
            move_row = move // 8
            if move_row == 0:
                clone_board[move] = 'Q'
            else:
                clone_board[move] = 'P'
                
            if move == board.en_passant_target and board.en_passant_pawn is not None:
                clone_board[board.en_passant_pawn] = '.'
                
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

        if r == 4 and board.en_passant_target is not None:
            current_pos = r * 8 + c
            if (c > 0 and board.en_passant_target == current_pos + 8 - 1) or \
               (c < 7 and board.en_passant_target == current_pos + 8 + 1):
                moves.append(board.en_passant_target)

        valid_moves = []
        for move in moves:
            clone_board = list(board.board)
            clone_board[r*8 + c] = '.'
            move_row = move // 8
            if move_row == 7:
                clone_board[move] = 'q'
            else:
                clone_board[move] = 'p'
                
            if move == board.en_passant_target and board.en_passant_pawn is not None:
                clone_board[board.en_passant_pawn] = '.'
                
            clone_board_str = ''.join(clone_board)
            if not Check_Black.black_king_capturable(clone_board_str):
                valid_moves.append(move)
            
        return valid_moves

    @staticmethod
    def is_promotion_move(start_pos: int, end_pos: int, piece: str) -> bool:
        """Check if a move is a promotion move"""
        end_row = end_pos // 8
        if piece == 'P':
            return end_row == 0
        elif piece == 'p':
            return end_row == 7
        return False

    @staticmethod
    def is_en_passant_move(board: BoardRepresentation, start_pos: int, end_pos: int, piece: str) -> bool:
        """Check if a move is an en passant capture"""
        return (piece in 'Pp' and 
                end_pos == board.en_passant_target and 
                board.en_passant_target is not None)

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