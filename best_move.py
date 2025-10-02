from board import BoardRepresentation
from valid_move import MoveValidator
from eval import evaluate_position
from find_opening_move import OpeningMoveFinder
from notation_convert import AlgebraicNotationConverter
import copy
import os


class BestMoveEngine:
    def __init__(self, depth=3, use_opening_book=True):
        self.depth = depth
        self.nodes_searched = 0
        self.use_opening_book = use_opening_book
        self.opening_finder = OpeningMoveFinder() if use_opening_book else None
        self.notation_converter = AlgebraicNotationConverter()
    
    def get_best_move(self, board: BoardRepresentation, is_white_turn: bool):
        """
        Get the best move for the current position.
        If use_opening_book is True and we're in the opening phase, 
        it will try to use opening book moves first.
        """
        self.nodes_searched = 0
        
        # Try opening book first if enabled
        if self.use_opening_book and self._is_opening_phase():
            opening_move = self._get_opening_move(board, is_white_turn)
            if opening_move:
                from_pos, to_pos = opening_move
                return from_pos, to_pos, "opening"
        
        # Fall back to minimax search
        return self._get_minimax_move(board, is_white_turn)
    
    def _is_opening_phase(self) -> bool:
        """
        Determine if we're still in the opening phase of the game.
        Uses move count from game_.txt to decide.
        """
        try:
            if not os.path.exists("game_.txt"):
                return True
            
            with open("game_.txt", "r") as f:
                content = f.read().strip()
                if not content:
                    return True
                
                moves = content.split()
                # Consider opening phase for first 10-12 moves (20-24 half-moves)
                return len(moves) <= 20
        except:
            return True  # Default to opening phase if can't read file
    
    def _get_opening_move(self, board: BoardRepresentation, is_white_turn: bool):
        """
        Get a move from the opening book if available.
        Returns (from_pos, to_pos) or None.
        """
        try:
            if not self.opening_finder:
                return None
            
            # Get the best opening move in algebraic notation
            algebraic_move = self.opening_finder.get_best_opening_move()
            if not algebraic_move:
                return None
            
            # Convert algebraic move to board positions
            move_positions = self._algebraic_to_positions(algebraic_move, board, is_white_turn)
            if move_positions:
                from_pos, to_pos = move_positions
                
                # Validate that this move is actually legal on the current board
                if self._is_move_valid(board, from_pos, to_pos, is_white_turn):
                    print(f"Using opening book move: {algebraic_move}")
                    return (from_pos, to_pos)
            
        except Exception as e:
            print(f"Error getting opening move: {e}")
        
        return None
    
    def _algebraic_to_positions(self, algebraic_move: str, board: BoardRepresentation, is_white_turn: bool):
        """
        Convert algebraic notation to board positions.
        This is a simplified version - for full implementation, you'd need 
        more sophisticated parsing.
        """
        try:
            # Handle castling
            if algebraic_move == "O-O":  # Kingside castling
                if is_white_turn:
                    return (60, 62)  # White king e1 to g1
                else:
                    return (4, 6)    # Black king e8 to g8
            elif algebraic_move == "O-O-O":  # Queenside castling
                if is_white_turn:
                    return (60, 58)  # White king e1 to c1
                else:
                    return (4, 2)    # Black king e8 to c8
            
            # Remove check/checkmate symbols
            clean_move = algebraic_move.replace('+', '').replace('#', '')
            
            # Simple pawn moves (e4, e5, etc.)
            if len(clean_move) == 2 and clean_move[0].islower():
                to_pos = self.notation_converter.algebraic_to_index(clean_move)
                if to_pos is None:
                    return None
                
                # Find the pawn that can move to this square
                from_pos = self._find_pawn_move(board, to_pos, is_white_turn)
                if from_pos is not None:
                    return (from_pos, to_pos)
            
            # Piece moves (Nf3, Bc4, etc.)
            elif len(clean_move) >= 3:
                piece_type = clean_move[0].upper()
                target_square = clean_move[-2:]
                to_pos = self.notation_converter.algebraic_to_index(target_square)
                
                if to_pos is None:
                    return None
                
                # Find the piece that can move to this square
                from_pos = self._find_piece_move(board, piece_type, to_pos, is_white_turn, clean_move)
                if from_pos is not None:
                    return (from_pos, to_pos)
            
        except Exception as e:
            print(f"Error converting algebraic move {algebraic_move}: {e}")
        
        return None
    
    def _find_pawn_move(self, board: BoardRepresentation, to_pos: int, is_white_turn: bool):
        """Find which pawn can move to the target position."""
        target_file = to_pos % 8
        target_rank = to_pos // 8
        
        piece_char = 'P' if is_white_turn else 'p'
        
        # Check one square forward
        if is_white_turn and target_rank > 0:
            from_pos = to_pos + 8
            if 0 <= from_pos < 64 and board.board[from_pos] == piece_char:
                return from_pos
        elif not is_white_turn and target_rank < 7:
            from_pos = to_pos - 8
            if 0 <= from_pos < 64 and board.board[from_pos] == piece_char:
                return from_pos
        
        # Check two squares forward (initial pawn move)
        if is_white_turn and target_rank == 4:  # Moving to rank 5 (4th index)
            from_pos = to_pos + 16
            if 0 <= from_pos < 64 and board.board[from_pos] == piece_char:
                return from_pos
        elif not is_white_turn and target_rank == 3:  # Moving to rank 4 (3rd index)
            from_pos = to_pos - 16
            if 0 <= from_pos < 64 and board.board[from_pos] == piece_char:
                return from_pos
        
        return None
    
    def _find_piece_move(self, board: BoardRepresentation, piece_type: str, to_pos: int, is_white_turn: bool, full_move: str):
        """Find which piece can move to the target position."""
        piece_char = piece_type if is_white_turn else piece_type.lower()
        
        # Search all squares for the piece
        for from_pos in range(64):
            if board.board[from_pos] == piece_char:
                # Check if this piece can legally move to the target
                if self._is_move_valid(board, from_pos, to_pos, is_white_turn):
                    return from_pos
        
        return None
    
    def _is_move_valid(self, board: BoardRepresentation, from_pos: int, to_pos: int, is_white_turn: bool):
        """Check if a move is valid using the existing move validator."""
        try:
            piece = board.board[from_pos]
            if not piece or piece == '.':
                return False
            
            # Check piece color matches turn
            if (is_white_turn and piece.islower()) or (not is_white_turn and piece.isupper()):
                return False
            
            valid_moves = MoveValidator.get_valid_moves(board, from_pos, piece)
            return to_pos in valid_moves
        except:
            return False
    
    def _get_minimax_move(self, board: BoardRepresentation, is_white_turn: bool):
        """Get the best move using minimax search."""
        all_moves = self._get_all_moves(board, is_white_turn)
        
        if not all_moves:
            return None, None, None
        
        best_move = None
        best_score = float('-inf') if is_white_turn else float('inf')
        
        for from_pos, to_pos in all_moves:
            temp_board = copy.deepcopy(board)
            temp_board.make_move(from_pos, to_pos)
            
            score = self._minimax(temp_board, self.depth - 1, not is_white_turn, 
                                 float('-inf'), float('inf'))
            
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
        self.nodes_searched += 1
        
        if depth == 0:
            board_string = self._board_to_string(board)
            return evaluate_position(board_string, is_white_turn)
        
        all_moves = self._get_all_moves(board, is_white_turn)
        
        if not all_moves:
            board_string = self._board_to_string(board)
            return evaluate_position(board_string, is_white_turn)
        
        if is_white_turn:
            max_eval = float('-inf')
            for from_pos, to_pos in all_moves:
                temp_board = copy.deepcopy(board)
                temp_board.make_move(from_pos, to_pos)
                eval_score = self._minimax(temp_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            for from_pos, to_pos in all_moves:

                temp_board = copy.deepcopy(board)
                temp_board.make_move(from_pos, to_pos)

                eval_score = self._minimax(temp_board, depth - 1, True, alpha, beta)
                eval_score = self._minimax(temp_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _get_all_moves(self, board: BoardRepresentation, is_white_turn: bool) -> list:
        all_moves = []
        
        for pos in range(64):
            piece = board.board[pos]
            if piece and piece != '.':
                if (is_white_turn and piece.isupper()) or (not is_white_turn and piece.islower()):
                    valid_moves = MoveValidator.get_valid_moves(board, pos, piece)
                    for move_pos in valid_moves:
                        all_moves.append((pos, move_pos))
        
        return all_moves
    
    def _board_to_string(self, board: BoardRepresentation) -> str:
        return board.board


def get_best_move(board: BoardRepresentation, is_white_turn: bool, depth: int = 3, use_opening_book: bool = True):
    """
    Get the best move for the given position.
    
    Args:
        board: Current board representation
        is_white_turn: Whether it's white's turn
        depth: Search depth for minimax (default: 3)
        use_opening_book: Whether to use opening book moves (default: True)
    
    Returns:
        Tuple of (from_pos, to_pos, score/evaluation)
    """
    engine = BestMoveEngine(depth, use_opening_book)
    return engine.get_best_move(board, is_white_turn)


if __name__ == "__main__":
    board = BoardRepresentation()
    
    print("=== Testing Integrated Best Move Engine ===")
    
    # Test with opening book enabled
    print("\n1. Testing with opening book enabled:")
    engine_with_opening = BestMoveEngine(depth=2, use_opening_book=True)
    from_pos, to_pos, score = engine_with_opening.get_best_move(board, True)
    
    if from_pos is not None:
        print(f"Best move: from {from_pos} to {to_pos}")
        print(f"Evaluation: {score}")
        if score == "opening":
            print("Move selected from opening book!")
        else:
            print(f"Nodes searched: {engine_with_opening.nodes_searched}")
    else:
        print("No valid moves found")
    
    # Test with opening book disabled
    print("\n2. Testing with opening book disabled:")
    engine_without_opening = BestMoveEngine(depth=2, use_opening_book=False)
    from_pos, to_pos, score = engine_without_opening.get_best_move(board, True)
    
    if from_pos is not None:
        print(f"Best move: from {from_pos} to {to_pos}")
        print(f"Evaluation: {score}")
        print(f"Nodes searched: {engine_without_opening.nodes_searched}")
    else:
        print("No valid moves found")
    
    # Test the standalone function
    print("\n3. Testing standalone function:")
    from_pos, to_pos, score = get_best_move(board, True, depth=2, use_opening_book=True)
    if from_pos is not None:
        print(f"Best move: from {from_pos} to {to_pos}")
        print(f"Evaluation: {score}")
    else:
        print("No valid moves found")   
