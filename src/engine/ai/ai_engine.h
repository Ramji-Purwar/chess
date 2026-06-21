#ifndef AI_ENGINE_H
#define AI_ENGINE_H

#include <string>
#include <vector>
#include "ai_board.h"
#include "ai_common.h"

// Forward declaration of the GUI board class
class Board;

namespace ai {

class AIEngine {
private:
    std::string color; // "w" or "b"
    AIBoard board;
    AIMove prev_move;
    
    // Search flags & state
    bool pv_eval;
    bool order_pv;
    int node_count;

    // Principal Variation table
    int pv_len[MAX_DEPTH];
    AIMove pv_table[MAX_DEPTH][MAX_DEPTH];

    // History heuristic table
    int history_table[13][110];

    // Search bounds
    int alpha;
    int beta;

private:
    // Sort moves in place for ordering
    void order_moves(std::vector<AIMove>& moves, int ply);
    
    // Check if the current position is a 3-fold draw
    bool check_draw() const;

    // Negamax with alpha-beta pruning
    int negamax(int depth, int alpha, int beta, int ply, bool null_move);

    // Quiescence search
    int quiescence(int alpha, int beta, int ply);

    // Run search for a single depth
    AIMove get_best_move_depth(int depth, AIMove best_move);

public:
    AIEngine(const std::string& aiColor);

    // Iterative deepening search up to depthLimit
    AIMove get_best_move(const Board& guiBoard, int depthLimit = 5, const std::vector<std::string>& positionHistory = {});
};

} // namespace ai

#endif // AI_ENGINE_H
