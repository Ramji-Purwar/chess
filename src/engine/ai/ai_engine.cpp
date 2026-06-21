#include "ai_engine.h"
#include "../board.h"
#include <algorithm>
#include <iostream>

namespace ai {

AIEngine::AIEngine(const std::string& aiColor)
    : color(aiColor), pv_eval(false), order_pv(false), node_count(0), alpha(-INF), beta(INF) {
    prev_move = AIMove();
    std::fill(pv_len, pv_len + MAX_DEPTH, 0);
    std::fill(&history_table[0][0], &history_table[0][0] + sizeof(history_table) / sizeof(int), 0);
}

void AIEngine::order_moves(std::vector<AIMove>& moves, int ply) {
    std::vector<std::pair<AIMove, int>> scored_moves;
    scored_moves.reserve(moves.size());

    for (const auto& move : moves) {
        int score = 0;

        if (prev_move == move) {
            score += PREV_MOVE_BONUS;
            prev_move = AIMove(); // Clear once matched
        } else if (order_pv) {
            if (pv_table[0][ply] == move) {
                order_pv = false;
                score += PV_BONUS;
            }
        } else {
            bool quiet = true;
            std::string captured = board.boardState[move.end];
            if (captured != "..") {
                char attackerType = board.boardState[move.start][1];
                char victimType = captured[1];
                score += MVV_LVA_BONUS + getMvvLvaScore(attackerType, victimType);
                quiet = false;
            }

            if (move.special[0] == 'P') {
                score += PROMOTION_BONUS + getPhaseValue(move.special[1]);
                quiet = false;
            }

            if (quiet) {
                int pNum = getPieceNumber(move.start_piece);
                score += history_table[pNum][move.end];
            }
        }

        scored_moves.push_back({move, score});
    }

    std::sort(scored_moves.begin(), scored_moves.end(), [](const auto& a, const auto& b) {
        return a.second > b.second;
    });

    moves.clear();
    for (const auto& sm : scored_moves) {
        moves.push_back(sm.first);
    }
}

bool AIEngine::check_draw() const {
    auto it = board.repetitions.find(board.board_hash);
    if (it != board.repetitions.end()) {
        return it->second >= 3;
    }
    return false;
}

int AIEngine::quiescence(int alphaVal, int betaVal, int ply) {
    int stand_pat = board.evaluate();
    if (stand_pat >= betaVal) {
        return betaVal;
    }
    if (stand_pat < alphaVal - 975) {
        return alphaVal;
    }
    if (stand_pat > alphaVal) {
        alphaVal = stand_pat;
    }

    node_count++;

    // Only search captures/promotions in quiescence
    std::vector<AIMove> legal_moves = board.get_legal_moves(true);
    order_moves(legal_moves, ply);

    for (const auto& move : legal_moves) {
        board.move(move);
        int evaluation = -quiescence(-betaVal, -alphaVal, ply + 1);
        board.unmove();

        if (evaluation > alphaVal) {
            alphaVal = evaluation;
            if (evaluation >= betaVal) {
                return betaVal;
            }
        }
    }

    return alphaVal;
}

int AIEngine::negamax(int depth, int alphaVal, int betaVal, int ply, bool null_move) {
    if (ply > 0 && check_draw()) {
        return 0;
    }

    if (ply < MAX_DEPTH) {
        pv_table[ply][ply] = AIMove();
        pv_len[ply] = 0;
    }

    std::vector<AIMove> legal_moves = board.get_legal_moves();
    if (legal_moves.empty()) {
        if (board.is_checked) {
            return -MATE_EVAL + ply;
        }
        return 0;
    }

    if (board.is_checked) {
        depth += 1;
    }

    node_count++;

    if (depth <= 0 || ply >= MAX_DEPTH - 1) {
        return quiescence(alphaVal, betaVal, ply);
    }

    // Null move pruning
    if (null_move && depth - NULL_DEPTH_REDUCTION >= 0 && ply > 0) {
        board.white_turn = !board.white_turn;
        int evaluation = -negamax(depth - NULL_DEPTH_REDUCTION, -betaVal, -betaVal + 1, ply + 1, false);
        board.white_turn = !board.white_turn;

        if (evaluation >= betaVal) {
            return betaVal;
        }
    }

    order_moves(legal_moves, ply);

    if (pv_eval) {
        pv_eval = false;
        for (const auto& move : legal_moves) {
            if (ply < MAX_DEPTH && move == pv_table[0][ply]) {
                pv_eval = true;
                order_pv = true;
                break;
            }
        }
    }

    for (const auto& move : legal_moves) {
        board.move(move);
        int evaluation = -negamax(depth - 1, -betaVal, -alphaVal, ply + 1, true);
        board.unmove();

        if (evaluation > alphaVal) {
            alphaVal = evaluation;
            if (ply < MAX_DEPTH) {
                pv_table[ply][ply] = move;
            }

            if (board.boardState[move.end] == "..") { // quiet move
                int pNum = getPieceNumber(move.start_piece);
                history_table[pNum][move.end] += depth;
            }

            if (ply < MAX_DEPTH - 1) {
                int pv_line_start = ply + 1;
                int pv_line_end = std::min(MAX_DEPTH, ply + 1 + pv_len[ply + 1]);

                for (int i = pv_line_start; i < pv_line_end; ++i) {
                    pv_table[ply][i] = pv_table[ply + 1][i];
                }
                pv_len[ply] = 1 + pv_len[ply + 1];
            }

            if (evaluation >= betaVal) {
                return betaVal;
            }
        }
    }

    return alphaVal;
}

AIMove AIEngine::get_best_move_depth(int depth, AIMove best_move) {
    prev_move = best_move;
    node_count = 0;
    
    // Clear PV
    std::fill(pv_len, pv_len + MAX_DEPTH, 0);
    for (int i = 0; i < MAX_DEPTH; ++i) {
        for (int j = 0; j < MAX_DEPTH; ++j) {
            pv_table[i][j] = AIMove();
        }
    }

    // Clear History heuristic
    std::fill(&history_table[0][0], &history_table[0][0] + sizeof(history_table) / sizeof(int), 0);
    
    pv_eval = true;
    int cur_ply = 0;

    int cur_evaluation = negamax(depth, alpha, beta, cur_ply, false);

    if (beta <= cur_evaluation || cur_evaluation <= alpha) {
        alpha = -INF;
        beta = INF;
        
        // Re-clear PV
        std::fill(pv_len, pv_len + MAX_DEPTH, 0);
        for (int i = 0; i < MAX_DEPTH; ++i) {
            for (int j = 0; j < MAX_DEPTH; ++j) {
                pv_table[i][j] = AIMove();
            }
        }

        cur_evaluation = negamax(depth, alpha, beta, cur_ply, false);
    }

    alpha = cur_evaluation - ASPIRATION;
    beta = cur_evaluation + ASPIRATION;

    return pv_table[0][0];
}

AIMove AIEngine::get_best_move(const Board& guiBoard, int depthLimit, const std::vector<std::string>& positionHistory) {
    board.update_board(guiBoard);
    
    if (positionHistory.empty()) {
        board.repetitions[board.board_hash]++;
    } else {
        board.repetitions.clear();
        for (const auto& sig : positionHistory) {
            uint64_t hash = board.get_hash_from_signature(sig);
            board.repetitions[hash]++;
        }
    }
    
    alpha = -INF;
    beta = INF;

    AIMove best_move;
    for (int depth = 1; depth <= depthLimit; ++depth) {
        best_move = get_best_move_depth(depth, best_move);
    }
    return best_move;
}

} // namespace ai
