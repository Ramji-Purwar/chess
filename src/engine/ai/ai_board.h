#ifndef AI_BOARD_H
#define AI_BOARD_H

#include <string>
#include <vector>
#include <array>
#include <map>
#include <tuple>
#include "ai_common.h"

// Forward declaration of the GUI board class
class Board;

namespace ai {

struct SafeBoardState {
    std::array<std::string, 110> data;

    const std::string& operator[](long long idx) const {
        if (idx < 0 || idx >= 110) {
            static const std::string border = "xx";
            return border;
        }
        return data[static_cast<std::size_t>(idx)];
    }

    std::string& operator[](long long idx) {
        if (idx < 0 || idx >= 110) {
            static std::string dummy = "xx";
            return dummy;
        }
        return data[static_cast<std::size_t>(idx)];
    }

    const std::string& operator[](std::size_t idx) const {
        if (idx >= 110) {
            static const std::string border = "xx";
            return border;
        }
        return data[idx];
    }

    std::string& operator[](std::size_t idx) {
        if (idx >= 110) {
            static std::string dummy = "xx";
            return dummy;
        }
        return data[idx];
    }

    const std::string& operator[](int idx) const {
        if (idx < 0 || idx >= 110) {
            static const std::string border = "xx";
            return border;
        }
        return data[static_cast<std::size_t>(idx)];
    }

    std::string& operator[](int idx) {
        if (idx < 0 || idx >= 110) {
            static std::string dummy = "xx";
            return dummy;
        }
        return data[static_cast<std::size_t>(idx)];
    }

    auto begin() { return data.begin(); }
    auto end() { return data.end(); }
    auto begin() const { return data.begin(); }
    auto end() const { return data.end(); }
    void fill(const std::string& val) { data.fill(val); }
    std::size_t size() const { return 110; }
};

class AIBoard {
public:
    SafeBoardState boardState;
    int phase;
    
    // Evaluation values
    int mid_value_w;
    int mid_value_b;
    int end_value_w;
    int end_value_b;

    int white_king_position;
    int black_king_position;
    int castle_rights;
    bool is_checked;
    bool white_turn;
    bool initialized;
    uint64_t board_hash;

    // repetition map
    std::map<uint64_t, int> repetitions;

    // move history: stores (move, captured_piece, old_castle_rights, old_board_hash)
    std::vector<std::tuple<AIMove, std::string, int, uint64_t>> moves;

public:
    AIBoard();
    
    // Synchronize this AI board with the GUI Board state
    void update_board(const ::Board& guiBoard);
    
    // Make and undo moves
    void move(const AIMove& move);
    void unmove();

    // Check queries
    bool has_check(int square, int ignore_square = -1) const;

    // Move generation
    std::vector<AIMove> get_legal_moves(bool loud_moves_only = false);

    // Position evaluation
    int evaluate() const;

    // Game state query
    bool is_over();

    // Hash conversion
    uint64_t get_hash_from_signature(const std::string& signature) const;
};

} // namespace ai

#endif // AI_BOARD_H
