from board import BoardRepresentation
from .white_king_capturable import Check_White
from .black_king_capturable import Check_Black

class BishopMove:
    @staticmethod

    def get_moves(board: BoardRepresentation, position: int) -> list:
        r = position // 8
        c = position % 8
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                if board.board[nr*8 + nc] == '.':
                    moves.append(nr*8 + nc)
                elif board.white_turn and board.board[nr*8 + nc] in 'rnbqkp':
                    moves.append(nr*8 + nc)
                    break
                elif not board.white_turn and board.board[nr*8 + nc] in 'RNBQKP':
                    moves.append(nr*8 + nc)
                    break
                else:
                    break
                nr += dr
                nc += dc

        valid_moves = []
        for move in moves:
            clone_board = list(board.board)
            clone_board[r*8 + c] = '.'
            clone_board[move] = 'B' if board.white_turn else 'b'
            clone_board_str = ''.join(clone_board)
            if board.white_turn:
                if not Check_White.white_king_capturable(clone_board_str):
                    valid_moves.append(move)
            else:
                if not Check_Black.black_king_capturable(clone_board_str):
                    valid_moves.append(move)

        return valid_moves