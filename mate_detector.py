from board import BoardRepresentation
from check_detector import CheckDetector
from valid_move import MoveValidator
import copy

class MateDetector:
    @staticmethod
    def is_checkmate(board: BoardRepresentation) -> bool:
        """
        Check if the current player is in checkmate.
        Returns True if the current player is in checkmate, False otherwise.
        """
        # First check if the king is in check
        if not CheckDetector().checked(board, board.white_turn):
            return False
        
        # If in check, see if there are any legal moves that get out of check
        return not MateDetector._has_legal_moves(board)
    
    @staticmethod
    def is_stalemate(board: BoardRepresentation) -> bool:
        """
        Check if the current player is in stalemate.
        Returns True if the current player is in stalemate, False otherwise.
        """
        # First check if the king is NOT in check
        if CheckDetector().checked(board, board.white_turn):
            return False
        
        # If not in check, see if there are any legal moves available
        return not MateDetector._has_legal_moves(board)
    
    @staticmethod
    def _has_legal_moves(board: BoardRepresentation) -> bool:
        """
        Check if the current player has any legal moves available.
        Returns True if there are legal moves, False if no legal moves.
        """
        # Get all piece positions for the current player
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
        
        # Check each piece to see if it has any legal moves
        for pos in all_positions:
            piece = board.board[pos]
            if piece != '.':
                possible_moves = MoveValidator.get_valid_moves(board, pos, piece)
                
                # Test each possible move to see if it's legal (doesn't leave king in check)
                for move_pos in possible_moves:
                    if MateDetector._is_legal_move(board, pos, move_pos):
                        return True
        
        return False
    
    @staticmethod
    def _is_legal_move(board: BoardRepresentation, start_pos: int, end_pos: int) -> bool:
        """
        Check if a move is legal (doesn't leave the king in check).
        """
        # Create a copy of the board to test the move
        test_board = copy.deepcopy(board)
        
        # Make the move on the test board
        test_board.make_move(start_pos, end_pos)
        
        # Switch turn back to check if the original player's king is still in check
        test_board.white_turn = not test_board.white_turn
        
        # Check if this move leaves the king in check
        return not CheckDetector().checked(test_board, test_board.white_turn)
    
    @staticmethod
    def get_game_status(board: BoardRepresentation) -> str:
        """
        Get the current game status.
        Returns: 'checkmate', 'stalemate', 'check', or 'normal'
        """
        if MateDetector.is_checkmate(board):
            return 'checkmate'
        elif MateDetector.is_stalemate(board):
            return 'stalemate'
        elif CheckDetector().checked(board, board.white_turn):
            return 'check'
        else:
            return 'normal'