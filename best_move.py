"""
Best Move Engine for Chess
Finds the best move using minimax algorithm with alpha-beta pruning
"""

from board import BoardRepresentation
from valid_move import MoveValidator
from eval import evaluate_position
import copy


class BestMoveEngine:
    def __init__(self, depth=3):
        """
        Initialize the best move engine
        
        Args:
            depth: Search depth for minimax algorithm
        """
        self.depth = depth
        self.nodes_searched = 0
    
    def get_best_move(self, board: BoardRepresentation, is_white_turn: bool):
        """
        Get the best move for the current position
        
        Args:
            board: Current board state
            is_white_turn: True if it's white's turn, False for black
            
        Returns:
            tuple: (from_pos, to_pos, score) or (None, None, None) if no moves
        """
        self.nodes_searched = 0
        
        # Get all possible moves
        all_moves = self._get_all_moves(board, is_white_turn)
        
        if not all_moves:
            return None, None, None
        
        best_move = None
        best_score = float('-inf') if is_white_turn else float('inf')
        
        # Evaluate each move
        for from_pos, to_pos in all_moves:
            # Make the move
            temp_board = copy.deepcopy(board)
            temp_board.make_move(from_pos, to_pos)
            
            # Evaluate position after move
            score = self._minimax(temp_board, self.depth - 1, not is_white_turn, 
                                 float('-inf'), float('inf'))
            
            # Update best move
            if is_white_turn and score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)
            elif not is_white_turn and score < best_score:
                best_score = score
                best_move = (from_pos, to_pos)
        
        if best_move:
            return best_move[0], best_move[1], best_score
        else:
            return None, None, None
    
    def _minimax(self, board: BoardRepresentation, depth: int, is_white_turn: bool, 
                alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning
        
        Args:
            board: Current board state
            depth: Remaining search depth
            is_white_turn: True if it's white's turn
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            
        Returns:
            float: Evaluation score
        """
        self.nodes_searched += 1
        
        # Base case: if depth is 0, evaluate position
        if depth == 0:
            board_string = self._board_to_string(board)
            return evaluate_position(board_string, is_white_turn)
        
        # Get all possible moves
        all_moves = self._get_all_moves(board, is_white_turn)
        
        # If no moves, return evaluation
        if not all_moves:
            board_string = self._board_to_string(board)
            return evaluate_position(board_string, is_white_turn)
        
        if is_white_turn:
            max_eval = float('-inf')
            for from_pos, to_pos in all_moves:
                # Make the move
                temp_board = copy.deepcopy(board)
                temp_board.make_move(from_pos, to_pos)
                
                # Recursive call
                eval_score = self._minimax(temp_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            for from_pos, to_pos in all_moves:
                # Make the move
                temp_board = copy.deepcopy(board)
                temp_board.make_move(from_pos, to_pos)
                
                # Recursive call
                eval_score = self._minimax(temp_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _get_all_moves(self, board: BoardRepresentation, is_white_turn: bool) -> list:
        """
        Get all valid moves for the current player
        
        Args:
            board: Current board state
            is_white_turn: True if it's white's turn
            
        Returns:
            list: List of (from_pos, to_pos) tuples
        """
        all_moves = []
        
        # Iterate through all squares
        for pos in range(64):
            piece = board.board[pos]  # Access piece using board string
            if piece and piece != '.':
                # Check if piece belongs to current player
                if (is_white_turn and piece.isupper()) or (not is_white_turn and piece.islower()):
                    # Get valid moves for this piece
                    valid_moves = MoveValidator.get_valid_moves(board, pos, piece)
                    for move_pos in valid_moves:
                        all_moves.append((pos, move_pos))
        
        return all_moves
    
    def _board_to_string(self, board: BoardRepresentation) -> str:
        """
        Convert board to 64-character string for evaluation
        
        Args:
            board: Board representation
            
        Returns:
            str: 64-character string (a8-h1 order)
        """
        return board.board  # The board is already a string


# Simple function for backward compatibility
def get_best_move(board: BoardRepresentation, is_white_turn: bool, depth: int = 3):
    """
    Simple function to get best move
    
    Args:
        board: Current board state
        is_white_turn: True if it's white's turn
        depth: Search depth
        
    Returns:
        tuple: (from_pos, to_pos, score)
    """
    engine = BestMoveEngine(depth)
    return engine.get_best_move(board, is_white_turn)


# For testing
if __name__ == "__main__":
    # Test the engine with a starting position
    board = BoardRepresentation()
    engine = BestMoveEngine(depth=2)
    
    from_pos, to_pos, score = engine.get_best_move(board, True)
    
    if from_pos is not None:
        print(f"Best move: from {from_pos} to {to_pos}")
        print(f"Evaluation: {score}")
        print(f"Nodes searched: {engine.nodes_searched}")
    else:
        print("No valid moves found")
