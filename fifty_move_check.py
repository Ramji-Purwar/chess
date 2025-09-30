import os

class FiftyMoveRule:
    @staticmethod
    def count_pieces(board_line):
        piece_count = 0
        for char in board_line.strip():
            if char != '.':
                piece_count += 1
        return piece_count

    @staticmethod
    def check_50_move_rule():
        try:
            if not os.path.exists("game.txt"):
                return False
            
            with open('game.txt', 'r') as file:
                lines = file.readlines()
            
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) < 50:
                return False
            
            last_lines = lines[-50:]
            
            piece_counts = []
            for line in last_lines:
                if len(line) == 64:
                    piece_counts.append(FiftyMoveRule.count_pieces(line))
            
            if len(piece_counts) < 50:
                return False
            
            first_count = piece_counts[0]
            for count in piece_counts:
                if count != first_count:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking 50-move rule: {e}")
            return False


def main():
    if FiftyMoveRule.check_50_move_rule():
        print("50-move rule applies - Game is a draw!")

if __name__ == "__main__":
    main()