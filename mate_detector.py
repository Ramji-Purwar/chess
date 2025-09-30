from board import BoardRepresentation
from check_detector import CheckDetector
from valid_move import MoveValidator
from three_repetition import ThreeFoldRepetition
import copy

class MateDetector:
    @staticmethod
    def is_checkmate(board: BoardRepresentation) -> bool:
        if not CheckDetector().checked(board, board.white_turn):
            return False
        
        return not MateDetector._has_legal_moves(board)
    
    @staticmethod
    def is_stalemate(board: BoardRepresentation) -> bool:
        if CheckDetector().checked(board, board.white_turn):
            return False
        
        return not MateDetector._has_legal_moves(board)
    
    @staticmethod
    def _has_legal_moves(board: BoardRepresentation) -> bool:
        if board.white_turn:
            all_positions = (board.position_white_king + 
                           board.position_white_queen + 
                           board.position_white_rooks + 
                           board.position_white_bishops + 
                           board.position_white_knights + 
                           board.position_white_pawns)
        else:
            all_positions = (board.position_black_king + 
                           board.position_black_queen + 
                           board.position_black_rooks + 
                           board.position_black_bishops + 
                           board.position_black_knights + 
                           board.position_black_pawns)
        
        for pos in all_positions:
            piece = board.board[pos]
            if piece != '.':
                possible_moves = MoveValidator.get_valid_moves(board, pos, piece)
                
                for move_pos in possible_moves:
                    if MateDetector._is_legal_move(board, pos, move_pos):
                        return True
        
        return False
    
    @staticmethod
    def _is_legal_move(board: BoardRepresentation, start_pos: int, end_pos: int) -> bool:
        test_board = copy.deepcopy(board)
        test_board.make_move(start_pos, end_pos)
        test_board.white_turn = not test_board.white_turn
        
        return not CheckDetector().checked(test_board, test_board.white_turn)
    
    @staticmethod
    def get_game_status(board: BoardRepresentation) -> str:
        if ThreeFoldRepetition.check_repetition():
            return 'repetition_draw'
        elif MateDetector.is_checkmate(board):
            return 'checkmate'
        elif MateDetector.is_stalemate(board):
            return 'stalemate'
        elif CheckDetector().checked(board, board.white_turn):
            return 'check'
        else:
            return 'normal'