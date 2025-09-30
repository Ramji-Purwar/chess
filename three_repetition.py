import os
from collections import Counter

class ThreeFoldRepetition:
    @staticmethod
    def check_repetition() -> bool:
        try:
            if not os.path.exists("game.txt"):
                return False
            
            with open("game.txt", "r") as f:
                positions = f.readlines()
            
            position_counts = Counter()
            for position in positions:
                cleaned_position = position.strip()
                if cleaned_position:
                    position_counts[cleaned_position] += 1

            for position, count in position_counts.items():
                if count >= 3:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking repetition: {e}")
            return False
    
    @staticmethod
    def get_repetition_info() -> dict:
        try:
            if not os.path.exists("game.txt"):
                return {"repeated_positions": [], "max_repetitions": 0, "total_positions": 0}
            
            with open("game.txt", "r") as f:
                positions = f.readlines()
            
            position_counts = Counter()
            for position in positions:
                cleaned_position = position.strip()
                if cleaned_position:
                    position_counts[cleaned_position] += 1
            
                    repeated_positions = []
                    max_repetitions = 0
            
            for position, count in position_counts.items():
                if count >= 2:
                    repeated_positions.append({"position": position, "count": count})
                    max_repetitions = max(max_repetitions, count)
            
            return {
                "repeated_positions": repeated_positions,
                "max_repetitions": max_repetitions,
                "total_positions": len([p for p in positions if p.strip()]),
                "has_threefold_repetition": max_repetitions >= 3
            }
            
        except Exception as e:
            print(f"Error getting repetition info: {e}")
            return {"repeated_positions": [], "max_repetitions": 0, "total_positions": 0}