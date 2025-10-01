from board import BoardRepresentation
from valid_move import MoveValidator
from eval import evaluate_position
import copy


class BestMoveEngine:
    def __init__(self, depth=3):
        self.depth = depth
        self.nodes_searched = 0
    
    def get_best_move(self, board: BoardRepresentation, is_white_turn: bool):
        self.nodes_searched = 0
        
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


def get_best_move(board: BoardRepresentation, is_white_turn: bool, depth: int = 3):
    engine = BestMoveEngine(depth)
    return engine.get_best_move(board, is_white_turn)


if __name__ == "__main__":
    board = BoardRepresentation()
    engine = BestMoveEngine(depth=2)
    
    from_pos, to_pos, score = engine.get_best_move(board, True)
    
    if from_pos is not None:
        print(f"Best move: from {from_pos} to {to_pos}")
        print(f"Evaluation: {score}")
        print(f"Nodes searched: {engine.nodes_searched}")
    else:
        print("No valid moves found")   
