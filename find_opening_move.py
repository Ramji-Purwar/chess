import json
import os
import random
from typing import Dict, List, Optional, Tuple


class OpeningMoveFinder:
    """
    A class to find opening moves based on the current game state.
    Reads moves from game_.txt and matches them against opening book JSON files.
    """
    
    def __init__(self, opening_folder: str = "opening", game_file: str = "game_.txt"):
        """
        Initialize the opening move finder.
        
        Args:
            opening_folder: Path to folder containing opening JSON files
            game_file: Path to file containing current game moves in algebraic notation
        """
        self.opening_folder = opening_folder
        self.game_file = game_file
        self.opening_books = {}
        self.load_opening_books()
    
    def load_opening_books(self) -> None:
        """Load all opening books from JSON files in the opening folder."""
        if not os.path.exists(self.opening_folder):
            print(f"Warning: Opening folder '{self.opening_folder}' not found.")
            return
        
        for filename in os.listdir(self.opening_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(self.opening_folder, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        opening_data = json.load(f)
                        opening_name = opening_data.get('opening_name', filename[:-5])
                        self.opening_books[opening_name] = opening_data
                        print(f"Loaded opening: {opening_name}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def get_current_moves(self) -> List[str]:
        """
        Read the current game moves from game_.txt.
        
        Returns:
            List of moves in algebraic notation
        """
        try:
            if not os.path.exists(self.game_file):
                return []
            
            with open(self.game_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                
                # Split moves by spaces and filter out empty strings
                moves = [move.strip() for move in content.split() if move.strip()]
                return moves
        except Exception as e:
            print(f"Error reading game file: {e}")
            return []
    
    def moves_to_sequence_string(self, moves: List[str]) -> str:
        """
        Convert a list of moves to a sequence string for matching against opening books.
        
        Args:
            moves: List of moves in algebraic notation
            
        Returns:
            String representation of the move sequence
        """
        # Remove check (+) and checkmate (#) symbols for matching
        clean_moves = []
        for move in moves:
            clean_move = move.replace('+', '').replace('#', '')
            clean_moves.append(clean_move)
        
        return ' '.join(clean_moves)
    
    def find_matching_openings(self, move_sequence: str) -> List[Tuple[str, Dict]]:
        """
        Find all openings that match the current move sequence.
        
        Args:
            move_sequence: String of moves separated by spaces
            
        Returns:
            List of tuples (opening_name, opening_data) for matching openings
        """
        matching_openings = []
        
        for opening_name, opening_data in self.opening_books.items():
            book = opening_data.get('book', {})
            
            # Check if the current sequence exists in this opening book
            if move_sequence in book or (move_sequence == "" and "start" in book):
                matching_openings.append((opening_name, opening_data))
        
        return matching_openings
    
    def get_best_moves_for_sequence(self, move_sequence: str, opening_data: Dict) -> List[str]:
        """
        Get the best moves for a given sequence from an opening book.
        
        Args:
            move_sequence: String of moves separated by spaces
            opening_data: The opening book data
            
        Returns:
            List of best moves for the current position
        """
        book = opening_data.get('book', {})
        
        # Handle starting position
        if move_sequence == "":
            start_data = book.get('start', {})
            return start_data.get('best_moves', [])
        
        # Look for the exact sequence
        sequence_data = book.get(move_sequence, {})
        return sequence_data.get('best_moves', [])
    
    def find_opening_move(self) -> Dict:
        """
        Find the best opening move based on the current game state.
        
        Returns:
            Dictionary containing:
            - current_moves: List of moves played so far
            - move_sequence: String representation of move sequence
            - matching_openings: List of matching opening names
            - suggested_moves: List of suggested moves with their sources
            - opening_info: Detailed information about matching openings
        """
        # Get current moves from the game file
        current_moves = self.get_current_moves()
        move_sequence = self.moves_to_sequence_string(current_moves)
        
        # Find matching openings
        matching_openings = self.find_matching_openings(move_sequence)
        
        # Collect suggested moves from all matching openings
        suggested_moves = {}  # move -> list of opening names that suggest it
        opening_info = {}
        
        for opening_name, opening_data in matching_openings:
            best_moves = self.get_best_moves_for_sequence(move_sequence, opening_data)
            opening_info[opening_name] = {
                'description': opening_data.get('description', ''),
                'eco_code': opening_data.get('eco_code', ''),
                'main_line': opening_data.get('main_line', ''),
                'best_moves': best_moves
            }
            
            # Add moves to suggested moves dictionary
            for move in best_moves:
                if move not in suggested_moves:
                    suggested_moves[move] = []
                suggested_moves[move].append(opening_name)
        
        # Convert suggested_moves to a list format for easier use
        suggested_moves_list = [
            {
                'move': move,
                'supported_by': openings,
                'confidence': len(openings)  # More openings = higher confidence
            }
            for move, openings in suggested_moves.items()
        ]
        
        # Sort by confidence (number of openings that suggest this move)
        suggested_moves_list.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'current_moves': current_moves,
            'move_sequence': move_sequence,
            'matching_openings': [name for name, _ in matching_openings],
            'suggested_moves': suggested_moves_list,
            'opening_info': opening_info
        }
    
    def get_all_best_moves(self) -> List[str]:
        """
        Get all the best opening moves for the current position.
        
        Returns:
            List of all recommended moves
        """
        result = self.find_opening_move()
        suggested_moves = result['suggested_moves']
        
        if suggested_moves:
            # Return all moves with the highest confidence level
            max_confidence = suggested_moves[0]['confidence']
            best_moves = [move['move'] for move in suggested_moves 
                         if move['confidence'] == max_confidence]
            return best_moves
        return []
    
    def get_all_possible_moves(self) -> List[Dict]:
        """
        Get all possible opening moves with their details.
        
        Returns:
            List of dictionaries containing move details
        """
        result = self.find_opening_move()
        return result['suggested_moves']
    
    def get_random_best_move(self) -> Optional[str]:
        """
        Get a randomly selected move from all the best moves.
        At game start, randomly chooses between e4 and d4.
        
        Returns:
            A randomly selected best move
        """
        current_moves = self.get_current_moves()
        
        # Special handling for game start - randomly choose between e4 and d4
        if len(current_moves) == 0:
            return random.choice(['e4', 'd4'])
        
        # For other positions, get all best moves and choose randomly
        best_moves = self.get_all_best_moves()
        
        if best_moves:
            return random.choice(best_moves)
        return None
    
    def get_best_opening_move(self) -> Optional[str]:
        """
        Get a single best opening move recommendation.
        At game start, randomly chooses between e4 and d4.
        Otherwise, randomly chooses from all best moves.
        
        Returns:
            The best move as a string, or None if no moves are found
        """
        return self.get_random_best_move()
    
    def print_opening_analysis(self) -> None:
        """Print a detailed analysis of the current opening position."""
        result = self.find_opening_move()
        
        print("=== Opening Analysis ===")
        print(f"Current moves: {' '.join(result['current_moves']) if result['current_moves'] else 'Game start'}")
        print(f"Move count: {len(result['current_moves'])}")
        print()
        
        if result['matching_openings']:
            print(f"Matching openings ({len(result['matching_openings'])}):")
            for opening_name in result['matching_openings']:
                info = result['opening_info'][opening_name]
                print(f"  • {opening_name} ({info['eco_code']})")
                print(f"    {info['description']}")
                print(f"    Main line: {info['main_line']}")
                if info['best_moves']:
                    print(f"    Suggests: {', '.join(info['best_moves'])}")
                print()
        else:
            print("No matching openings found for current position.")
            print()
        
        if result['suggested_moves']:
            print("Recommended moves:")
            # Group moves by confidence level
            confidence_groups = {}
            for move_info in result['suggested_moves']:
                confidence = move_info['confidence']
                if confidence not in confidence_groups:
                    confidence_groups[confidence] = []
                confidence_groups[confidence].append(move_info)
            
            # Display moves grouped by confidence (highest first)
            for confidence in sorted(confidence_groups.keys(), reverse=True):
                moves_in_group = confidence_groups[confidence]
                print(f"  Best moves (confidence {confidence}):")
                for move_info in moves_in_group:
                    move = move_info['move']
                    sources = ', '.join(move_info['supported_by'])
                    print(f"    • {move} (supported by: {sources})")
                print()
        else:
            print("No opening moves recommended for current position.")
        
        print("=" * 25)


def main():
    """Example usage of the OpeningMoveFinder."""
    finder = OpeningMoveFinder()
    
    # Print current analysis
    finder.print_opening_analysis()
    
    # Get all best moves
    all_best_moves = finder.get_all_best_moves()
    if all_best_moves:
        print(f"\nAll best moves: {', '.join(all_best_moves)}")
    
    # Get a randomly selected best move
    best_move = finder.get_best_opening_move()
    if best_move:
        print(f"Randomly selected move: {best_move}")
    else:
        print("No opening move found.")
    
    # Demonstrate multiple random selections at game start
    current_moves = finder.get_current_moves()
    if len(current_moves) == 0:
        print(f"\nRandom opening move selections (game start):")
        for i in range(5):
            move = finder.get_best_opening_move()
            print(f"  Selection {i+1}: {move}")


if __name__ == "__main__":
    main()
