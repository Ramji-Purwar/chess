#include "ai_board.h"
#include "../board.h"
#include <iostream>
#include <set>
#include <cmath>
#include <cctype>

namespace ai {

static std::string getAIPieceString(const Piece* piece) {
    if (!piece) return "..";
    std::string s = "";
    s += (piece->getColor() == PieceColor::White) ? 'w' : 'b';
    switch (piece->getType()) {
        case PieceType::Pawn: s += 'p'; break;
        case PieceType::Rook: s += 'r'; break;
        case PieceType::Knight: s += 'n'; break;
        case PieceType::Bishop: s += 'b'; break;
        case PieceType::Queen: s += 'q'; break;
        case PieceType::King: s += 'k'; break;
        default: s += '.'; break;
    }
    return s;
}

AIBoard::AIBoard()
    : phase(0),
      mid_value_w(0), mid_value_b(0),
      end_value_w(0), end_value_b(0),
      white_king_position(-1), black_king_position(-1),
      castle_rights(0), is_checked(false),
      white_turn(true), initialized(false), board_hash(0) {
    boardState.fill("xx");
}

void AIBoard::update_board(const ::Board& guiBoard) {
    boardState.fill("xx");
    
    // Set up standard invalid borders and playable center
    for (int row = 1; row <= 8; ++row) {
        boardState[row * 10] = "xx";
        for (int col = 1; col <= 8; ++col) {
            boardState[row * 10 + col] = "..";
        }
        boardState[row * 10 + 9] = "xx";
    }

    white_turn = guiBoard.isWhiteToMove();
    phase = 0;
    mid_value_w = 0; mid_value_b = 0;
    end_value_w = 0; end_value_b = 0;
    board_hash = 0;
    repetitions.clear();
    moves.clear();

    for (int rank_index = 0; rank_index < 8; ++rank_index) {
        for (int file_index = 0; file_index < 8; ++file_index) {
            int guiSq = (7 - rank_index) * 8 + file_index;
            int square = FAKE_SQUARES[rank_index * 8 + file_index];

            Piece* p = guiBoard.getPiece(guiSq);
            std::string piece = getAIPieceString(p);
            boardState[square] = piece;

            int pNum = getPieceNumber(piece);
            board_hash ^= getZobrist().hash_pieces[square][pNum];

            if (piece != "..") {
                phase += getPhaseValue(piece[1]);
                int midVal = getMidValues(piece)[square] + getPhaseValueMid(piece[1]);
                int endVal = getEndValues(piece)[square] + getPhaseValueEnd(piece[1]);

                if (piece[0] == 'w') {
                    mid_value_w += midVal;
                    end_value_w += endVal;
                } else if (piece[0] == 'b') {
                    mid_value_b += midVal;
                    end_value_b += endVal;
                }

                if (piece == "wk") {
                    white_king_position = square;
                } else if (piece == "bk") {
                    black_king_position = square;
                }
            }
        }
    }

    castle_rights = 0;
    if (guiBoard.canCastleKingside(PieceColor::White)) castle_rights |= 1;  // wk
    if (guiBoard.canCastleQueenside(PieceColor::White)) castle_rights |= 2; // wq
    if (guiBoard.canCastleKingside(PieceColor::Black)) castle_rights |= 4;  // bk
    if (guiBoard.canCastleQueenside(PieceColor::Black)) castle_rights |= 8; // bq

    board_hash ^= getZobrist().hash_castle[castle_rights];
    repetitions[board_hash]++;
    initialized = true;
}

void AIBoard::move(const AIMove& move) {
    std::string start_piece = move.start_piece;
    int start = move.start;
    int end = move.end;
    std::string special = move.special;

    // Save history
    moves.push_back(std::make_tuple(move, boardState[end], castle_rights, board_hash));

    // XOR old castle rights
    board_hash ^= getZobrist().hash_castle[castle_rights];

    // XOR out old pieces from hash
    board_hash ^= getZobrist().hash_pieces[start][getPieceNumber(boardState[start])];
    board_hash ^= getZobrist().hash_pieces[end][getPieceNumber(boardState[end])];

    // Remove old values from evaluation
    char startType = boardState[start][1];
    char endType = boardState[end][1];
    char startColor = boardState[start][0];
    char endColor = boardState[end][0];

    phase -= getPhaseValue(startType) + getPhaseValue(endType);

    int startMid = getMidValues(boardState[start])[start] + getPhaseValueMid(startType);
    int startEnd = getEndValues(boardState[start])[start] + getPhaseValueEnd(startType);
    int endMid = getMidValues(boardState[end])[end] + getPhaseValueMid(endType);
    int endEnd = getEndValues(boardState[end])[end] + getPhaseValueEnd(endType);

    if (startColor == 'w') {
        mid_value_w -= startMid;
        end_value_w -= startEnd;
    } else if (startColor == 'b') {
        mid_value_b -= startMid;
        end_value_b -= startEnd;
    }

    if (endColor == 'w') {
        mid_value_w -= endMid;
        end_value_w -= endEnd;
    } else if (endColor == 'b') {
        mid_value_b -= endMid;
        end_value_b -= endEnd;
    }

    // Update pieces on board
    boardState[start] = "..";
    boardState[end] = start_piece;

    // Handle king movement / castle mask updates
    if (startType == 'k') {
        castle_rights &= (getRemoveCastleRights(startColor + "k") & getRemoveCastleRights(startColor + "q"));
        if (startColor == 'w') {
            white_king_position = end;
        } else {
            black_king_position = end;
        }

        if (special == "C") {
            int rookStart = 0, rookEnd = 0;
            if (getCastleRookPosition(end, rookStart, rookEnd)) {
                std::string rookPiece = boardState[rookStart];
                char rookType = rookPiece[1];
                
                mid_value_w -= (startColor == 'w') ? (getMidValues(rookPiece)[rookStart] + getPhaseValueMid(rookType)) : 0;
                mid_value_b -= (startColor == 'b') ? (getMidValues(rookPiece)[rookStart] + getPhaseValueMid(rookType)) : 0;
                end_value_w -= (startColor == 'w') ? (getEndValues(rookPiece)[rookStart] + getPhaseValueEnd(rookType)) : 0;
                end_value_b -= (startColor == 'b') ? (getEndValues(rookPiece)[rookStart] + getPhaseValueEnd(rookType)) : 0;

                boardState[rookEnd] = rookPiece;
                boardState[rookStart] = "..";

                mid_value_w += (startColor == 'w') ? (getMidValues(rookPiece)[rookEnd] + getPhaseValueMid(rookType)) : 0;
                mid_value_b += (startColor == 'b') ? (getMidValues(rookPiece)[rookEnd] + getPhaseValueMid(rookType)) : 0;
                end_value_w += (startColor == 'w') ? (getEndValues(rookPiece)[rookEnd] + getPhaseValueEnd(rookType)) : 0;
                end_value_b += (startColor == 'b') ? (getEndValues(rookPiece)[rookEnd] + getPhaseValueEnd(rookType)) : 0;
            }
        }
    } else if (startType == 'r') {
        std::string rookKey = getPositionRooks(start);
        if (!rookKey.empty()) {
            castle_rights &= getRemoveCastleRights(rookKey);
        }
    }

    // Handle promotions
    if (special[0] == 'P') {
        std::string promotedPiece = "";
        promotedPiece += startColor;
        promotedPiece += special[1];
        boardState[end] = promotedPiece;
    }

    // Add new values to evaluation
    char finalStartType = boardState[start][1];
    char finalEndType = boardState[end][1];
    char finalStartColor = boardState[start][0];
    char finalEndColor = boardState[end][0];

    phase += getPhaseValue(finalStartType) + getPhaseValue(finalEndType);

    int newStartMid = getMidValues(boardState[start])[start] + getPhaseValueMid(finalStartType);
    int newStartEnd = getEndValues(boardState[start])[start] + getPhaseValueEnd(finalStartType);
    int newEndMid = getMidValues(boardState[end])[end] + getPhaseValueMid(finalEndType);
    int newEndEnd = getEndValues(boardState[end])[end] + getPhaseValueEnd(finalEndType);

    if (finalStartColor == 'w') {
        mid_value_w += newStartMid;
        end_value_w += newStartEnd;
    } else if (finalStartColor == 'b') {
        mid_value_b += newStartMid;
        end_value_b += newStartEnd;
    }

    if (finalEndColor == 'w') {
        mid_value_w += newEndMid;
        end_value_w += newEndEnd;
    } else if (finalEndColor == 'b') {
        mid_value_b += newEndMid;
        end_value_b += newEndEnd;
    }

    // XOR new pieces and castle rights into hash
    board_hash ^= getZobrist().hash_pieces[start][getPieceNumber(boardState[start])];
    board_hash ^= getZobrist().hash_pieces[end][getPieceNumber(boardState[end])];
    board_hash ^= getZobrist().hash_castle[castle_rights];

    white_turn = !white_turn;
    repetitions[board_hash]++;
}

void AIBoard::unmove() {
    auto lastMoveData = moves.back();
    moves.pop_back();

    AIMove move = std::get<0>(lastMoveData);
    std::string end_piece = std::get<1>(lastMoveData);
    int old_castle_rights = std::get<2>(lastMoveData);
    uint64_t old_board_hash = std::get<3>(lastMoveData);

    repetitions[board_hash]--;
    if (repetitions[board_hash] == 0) {
        repetitions.erase(board_hash);
    }

    white_turn = !white_turn;

    std::string start_piece = move.start_piece;
    int start = move.start;
    int end = move.end;
    std::string special = move.special;

    // Remove current board values from evaluation
    char currentStartType = boardState[start][1];
    char currentEndType = boardState[end][1];
    char currentStartColor = boardState[start][0];
    char currentEndColor = boardState[end][0];

    phase -= getPhaseValue(currentStartType) + getPhaseValue(currentEndType);

    int startMid = getMidValues(boardState[start])[start] + getPhaseValueMid(currentStartType);
    int startEnd = getEndValues(boardState[start])[start] + getPhaseValueEnd(currentStartType);
    int endMid = getMidValues(boardState[end])[end] + getPhaseValueMid(currentEndType);
    int endEnd = getEndValues(boardState[end])[end] + getPhaseValueEnd(currentEndType);

    if (currentStartColor == 'w') {
        mid_value_w -= startMid;
        end_value_w -= startEnd;
    } else if (currentStartColor == 'b') {
        mid_value_b -= startMid;
        end_value_b -= startEnd;
    }

    if (currentEndColor == 'w') {
        mid_value_w -= endMid;
        end_value_w -= endEnd;
    } else if (currentEndColor == 'b') {
        mid_value_b -= endMid;
        end_value_b -= endEnd;
    }

    // Restore state
    boardState[start] = start_piece;
    boardState[end] = end_piece;
    castle_rights = old_castle_rights;
    board_hash = old_board_hash;

    char startColor = start_piece[0];
    char startType = start_piece[1];

    if (startType == 'k') {
        if (startColor == 'w') {
            white_king_position = start;
        } else {
            black_king_position = start;
        }

        if (special == "C") {
            int rookStart = 0, rookEnd = 0;
            if (getCastleRookPosition(end, rookStart, rookEnd)) {
                std::string rookPiece = boardState[rookEnd];
                char rookType = rookPiece[1];

                mid_value_w -= (startColor == 'w') ? (getMidValues(rookPiece)[rookEnd] + getPhaseValueMid(rookType)) : 0;
                mid_value_b -= (startColor == 'b') ? (getMidValues(rookPiece)[rookEnd] + getPhaseValueMid(rookType)) : 0;
                end_value_w -= (startColor == 'w') ? (getEndValues(rookPiece)[rookEnd] + getPhaseValueEnd(rookType)) : 0;
                end_value_b -= (startColor == 'b') ? (getEndValues(rookPiece)[rookEnd] + getPhaseValueEnd(rookType)) : 0;

                boardState[rookStart] = rookPiece;
                boardState[rookEnd] = "..";

                mid_value_w += (startColor == 'w') ? (getMidValues(rookPiece)[rookStart] + getPhaseValueMid(rookType)) : 0;
                mid_value_b += (startColor == 'b') ? (getMidValues(rookPiece)[rookStart] + getPhaseValueMid(rookType)) : 0;
                end_value_w += (startColor == 'w') ? (getEndValues(rookPiece)[rookStart] + getPhaseValueEnd(rookType)) : 0;
                end_value_b += (startColor == 'b') ? (getEndValues(rookPiece)[rookStart] + getPhaseValueEnd(rookType)) : 0;
            }
        }
    }

    // Re-add restored board values to evaluation
    char restoredStartType = boardState[start][1];
    char restoredEndType = boardState[end][1];
    char restoredStartColor = boardState[start][0];
    char restoredEndColor = boardState[end][0];

    phase += getPhaseValue(restoredStartType) + getPhaseValue(restoredEndType);

    int newStartMid = getMidValues(boardState[start])[start] + getPhaseValueMid(restoredStartType);
    int newStartEnd = getEndValues(boardState[start])[start] + getPhaseValueEnd(restoredStartType);
    int newEndMid = getMidValues(boardState[end])[end] + getPhaseValueMid(restoredEndType);
    int newEndEnd = getEndValues(boardState[end])[end] + getPhaseValueEnd(restoredEndType);

    if (restoredStartColor == 'w') {
        mid_value_w += newStartMid;
        end_value_w += newStartEnd;
    } else if (restoredStartColor == 'b') {
        mid_value_b += newStartMid;
        end_value_b += newStartEnd;
    }

    if (restoredEndColor == 'w') {
        mid_value_w += newEndMid;
        end_value_w += newEndEnd;
    } else if (restoredEndColor == 'b') {
        mid_value_b += newEndMid;
        end_value_b += newEndEnd;
    }
}

bool AIBoard::has_check(int square, int ignore_square) const {
    std::string friendlyColor = white_turn ? "w" : "b";
    std::string enemyColor = white_turn ? "b" : "w";
    int pawn_step = white_turn ? UP : DOWN;

    if (boardState[square + pawn_step + LEFT] == (enemyColor + "p") ||
        boardState[square + pawn_step + RIGHT] == (enemyColor + "p")) {
        return true;
    }

    struct DirRule {
        int dir;
        std::string pieces;
    };
    static const DirRule ALL_DIRECTIONS_RULES[] = {
        {UP, "rq"}, {DOWN, "rq"}, {LEFT, "rq"}, {RIGHT, "rq"},
        {UP + LEFT, "bq"}, {UP + RIGHT, "bq"}, {DOWN + LEFT, "bq"}, {DOWN + RIGHT, "bq"}
    };

    for (const auto& rule : ALL_DIRECTIONS_RULES) {
        int new_square = square;
        while (true) {
            new_square += rule.dir;
            if (new_square == ignore_square) {
                continue;
            }

            char pieceCol = boardState[new_square][0];
            if (pieceCol == friendlyColor[0] || pieceCol == 'x') {
                break;
            }

            char pieceType = boardState[new_square][1];
            if (rule.pieces.find(pieceType) != std::string::npos) {
                return true;
            } else if (boardState[new_square] != "..") {
                break;
            }
        }
    }

    for (int offset : KNIGHT_MOVES) {
        if (boardState[square + offset] == (enemyColor + "n")) {
            return true;
        }
    }

    for (int offset : KING_MOVES) {
        if (boardState[square + offset] == (enemyColor + "k")) {
            return true;
        }
    }

    return false;
}

std::vector<AIMove> AIBoard::get_legal_moves(bool loud_moves_only) {
    int pawn_step = white_turn ? UP : DOWN;
    std::string friendlyColor = white_turn ? "w" : "b";
    std::string enemyColor = white_turn ? "b" : "w";
    int starting_rank = white_turn ? WHITE_PAWN_STARTING_RANK : BLACK_PAWN_STARTING_RANK;
    int promotion_rank = white_turn ? WHITE_PROMOTION_RANK : BLACK_PROMOTION_RANK;

    int king_pos = white_turn ? white_king_position : black_king_position;
    
    std::vector<AIMove> all_moves;
    std::map<int, int> pins; // pinned square -> pin direction
    std::vector<std::pair<int, int>> checks; // attacking square, direction

    // process_pins()
    auto process_pins = [&]() {
        if (boardState[king_pos + pawn_step + LEFT] == (enemyColor + "p")) {
            checks.push_back({king_pos + pawn_step + LEFT, pawn_step + LEFT});
        }
        if (boardState[king_pos + pawn_step + RIGHT] == (enemyColor + "p")) {
            checks.push_back({king_pos + pawn_step + RIGHT, pawn_step + RIGHT});
        }

        struct DirRule {
            int dir;
            std::string pieces;
        };
        static const DirRule ALL_DIRECTIONS_RULES[] = {
            {UP, "rq"}, {DOWN, "rq"}, {LEFT, "rq"}, {RIGHT, "rq"},
            {UP + LEFT, "bq"}, {UP + RIGHT, "bq"}, {DOWN + LEFT, "bq"}, {DOWN + RIGHT, "bq"}
        };

        for (const auto& rule : ALL_DIRECTIONS_RULES) {
            int pin = -1;
            int new_square = king_pos;

            while (true) {
                new_square += rule.dir;
                if (boardState[new_square] == "xx") {
                    break;
                }

                char pieceCol = boardState[new_square][0];
                if (pieceCol == friendlyColor[0]) {
                    if (pin != -1) {
                        break;
                    }
                    pin = new_square;
                } else if (pieceCol == enemyColor[0]) {
                    char pieceType = boardState[new_square][1];
                    if (rule.pieces.find(pieceType) != std::string::npos) {
                        if (pin == -1) {
                            checks.push_back({new_square, rule.dir});
                        } else {
                            pins[pin] = rule.dir;
                        }
                    }
                    break;
                }
            }
        }

        for (int offset : KNIGHT_MOVES) {
            if (boardState[king_pos + offset] == (enemyColor + "n")) {
                checks.push_back({king_pos + offset, 0});
            }
        }
    };

    process_pins();

    // get_king_moves()
    auto get_king_moves = [&](int square, std::vector<AIMove>& moves_out) {
        bool valid_castle = (boardState[square] == (friendlyColor + "k")) && 
                            (square == (white_turn ? 15 : 85));

        if (checks.empty() && valid_castle) {
            // Kingside castling
            if (boardState[square + 1] == ".." && boardState[square + 2] == ".." &&
                (castle_rights & (white_turn ? 1 : 4)) &&
                boardState[square + 3] == (friendlyColor + "r")) {
                if (!has_check(square + 1, square) && !has_check(square + 2, square)) {
                    moves_out.push_back(AIMove(boardState[square], square, square + 2, "C"));
                }
            }
            // Queenside castling
            if (boardState[square - 1] == ".." && boardState[square - 2] == ".." && boardState[square - 3] == ".." &&
                (castle_rights & (white_turn ? 2 : 8)) &&
                boardState[square - 4] == (friendlyColor + "r")) {
                if (!has_check(square - 1, square) && !has_check(square - 2, square)) {
                    moves_out.push_back(AIMove(boardState[square], square, square - 2, "C"));
                }
            }
        }

        for (int offset : KING_MOVES) {
            int target = square + offset;
            char targetCol = boardState[target][0];
            if (targetCol != friendlyColor[0] && targetCol != 'x') {
                if (!has_check(target, square)) {
                    moves_out.push_back(AIMove(boardState[square], square, target, "N"));
                }
            }
        }
    };

    if (checks.size() > 1) {
        is_checked = true;
        get_king_moves(king_pos, all_moves);
        return all_moves;
    }

    is_checked = !checks.empty();

    // Pawn movement
    auto get_pawn_moves = [&](int square, bool is_pinned, int king_pin, std::vector<AIMove>& moves_out) {
        // Single push
        if (boardState[square + pawn_step] == ".." && (!is_pinned || king_pin == pawn_step || king_pin == -pawn_step)) {
            if (TRUE_SQUARES[square + pawn_step] / 8 == promotion_rank) {
                for (char p : std::string("qrbn")) {
                    std::string spec = "P";
                    spec += p;
                    moves_out.push_back(AIMove(boardState[square], square, square + pawn_step, spec));
                }
            } else {
                moves_out.push_back(AIMove(boardState[square], square, square + pawn_step, "N"));
            }
            
            // Double push
            if (TRUE_SQUARES[square] / 8 == starting_rank && boardState[square + 2 * pawn_step] == "..") {
                moves_out.push_back(AIMove(boardState[square], square, square + 2 * pawn_step, "D"));
            }
        }

        // Capture Left
        int targetLeft = square + pawn_step + LEFT;
        if (boardState[targetLeft][0] == enemyColor[0] && (!is_pinned || king_pin == pawn_step + LEFT)) {
            if (TRUE_SQUARES[targetLeft] / 8 == promotion_rank) {
                for (char p : std::string("qrbn")) {
                    std::string spec = "P";
                    spec += p;
                    moves_out.push_back(AIMove(boardState[square], square, targetLeft, spec));
                }
            } else {
                moves_out.push_back(AIMove(boardState[square], square, targetLeft, "N"));
            }
        }

        // Capture Right
        int targetRight = square + pawn_step + RIGHT;
        if (boardState[targetRight][0] == enemyColor[0] && (!is_pinned || king_pin == pawn_step + RIGHT)) {
            if (TRUE_SQUARES[targetRight] / 8 == promotion_rank) {
                for (char p : std::string("qrbn")) {
                    std::string spec = "P";
                    spec += p;
                    moves_out.push_back(AIMove(boardState[square], square, targetRight, spec));
                }
            } else {
                moves_out.push_back(AIMove(boardState[square], square, targetRight, "N"));
            }
        }
    };

    auto get_rook_moves = [&](int square, bool is_pinned, int king_pin, std::vector<AIMove>& moves_out) {
        for (int direction : ROOK_DIRECTIONS) {
            if (is_pinned && king_pin != direction && king_pin != -direction) {
                continue;
            }

            int new_square = square;
            while (true) {
                new_square += direction;
                char pieceCol = boardState[new_square][0];
                if (pieceCol == friendlyColor[0] || pieceCol == 'x') {
                    break;
                }

                moves_out.push_back(AIMove(boardState[square], square, new_square, "N"));

                if (pieceCol == enemyColor[0]) {
                    break;
                }
            }
        }
    };

    auto get_knight_moves = [&](int square, bool is_pinned, std::vector<AIMove>& moves_out) {
        if (!is_pinned) {
            for (int offset : KNIGHT_MOVES) {
                int target = square + offset;
                char targetCol = boardState[target][0];
                if (targetCol != friendlyColor[0] && targetCol != 'x') {
                    moves_out.push_back(AIMove(boardState[square], square, target, "N"));
                }
            }
        }
    };

    auto get_bishop_moves = [&](int square, bool is_pinned, int king_pin, std::vector<AIMove>& moves_out) {
        for (int direction : BISHOP_DIRECTIONS) {
            if (is_pinned && king_pin != direction && king_pin != -direction) {
                continue;
            }

            int new_square = square;
            while (true) {
                new_square += direction;
                char pieceCol = boardState[new_square][0];
                if (pieceCol == friendlyColor[0] || pieceCol == 'x') {
                    break;
                }

                moves_out.push_back(AIMove(boardState[square], square, new_square, "N"));

                if (pieceCol == enemyColor[0]) {
                    break;
                }
            }
        }
    };

    auto get_queen_moves = [&](int square, bool is_pinned, int king_pin, std::vector<AIMove>& moves_out) {
        get_rook_moves(square, is_pinned, king_pin, moves_out);
        get_bishop_moves(square, is_pinned, king_pin, moves_out);
    };

    // Filter target squares for non-king pieces if in check
    std::set<int> check_squares;
    bool has_check_filter = false;
    if (is_checked) {
        has_check_filter = true;
        int checkAttacker = checks[0].first;
        int checkDir = checks[0].second;
        check_squares.insert(checkAttacker);
        
        if (boardState[checkAttacker][1] != 'n' && checkDir != 0) {
            int check_square = king_pos;
            while (true) {
                check_square += checkDir;
                if (boardState[check_square] == boardState[checkAttacker]) {
                    break;
                }
                check_squares.insert(check_square);
            }
        }
    }

    // Generate for all pieces
    for (int cur_square = 0; cur_square < 110; ++cur_square) {
        std::string cur_piece = boardState[cur_square];
        if (cur_piece == "xx" || cur_piece[0] != friendlyColor[0]) {
            continue;
        }

        bool is_pinned = (pins.find(cur_square) != pins.end());
        int king_pin = is_pinned ? pins[cur_square] : 0;

        std::vector<AIMove> cur_piece_moves;
        char pieceType = cur_piece[1];

        if (pieceType == 'p') get_pawn_moves(cur_square, is_pinned, king_pin, cur_piece_moves);
        else if (pieceType == 'r') get_rook_moves(cur_square, is_pinned, king_pin, cur_piece_moves);
        else if (pieceType == 'n') get_knight_moves(cur_square, is_pinned, cur_piece_moves);
        else if (pieceType == 'b') get_bishop_moves(cur_square, is_pinned, king_pin, cur_piece_moves);
        else if (pieceType == 'q') get_queen_moves(cur_square, is_pinned, king_pin, cur_piece_moves);
        else if (pieceType == 'k') {
            get_king_moves(cur_square, cur_piece_moves);
        }

        if (has_check_filter && pieceType != 'k') {
            for (const auto& m : cur_piece_moves) {
                if (check_squares.find(m.end) != check_squares.end()) {
                    all_moves.push_back(m);
                }
            }
        } else {
            all_moves.insert(all_moves.end(), cur_piece_moves.begin(), cur_piece_moves.end());
        }
    }

    if (loud_moves_only) {
        std::vector<AIMove> loud_moves;
        for (const auto& m : all_moves) {
            if (boardState[m.end][0] == enemyColor[0] || m.special[0] == 'P') {
                loud_moves.push_back(m);
            }
        }
        return loud_moves;
    }

    return all_moves;
}

int AIBoard::evaluate() const {
    int evaluation = (((mid_value_w - mid_value_b) * phase) +
                      ((end_value_w - end_value_b) * (OPENING_PHASE - phase))) / OPENING_PHASE;

    if (phase <= ENDGAME_PHASE * 2) {
        evaluation = (end_value_w - end_value_b) / 2;

        int whiteKingSq = TRUE_SQUARES[white_king_position];
        int blackKingSq = TRUE_SQUARES[black_king_position];

        int rw = whiteKingSq / 8;
        int fw = whiteKingSq % 8;
        int rb = blackKingSq / 8;
        int fb = blackKingSq % 8;

        int mop_up = static_cast<int>(1.6 * (14 - (std::abs(rw - rb) + std::abs(fw - fb))));
        if (evaluation > 0) {
            int d01 = 3 - rb;
            int d02 = rb - 4;
            int d11 = 3 - fb;
            int d12 = fb - 4;
            mop_up += static_cast<int>(4.7 * ((d01 > d02 ? d01 : d02) + (d11 > d12 ? d11 : d12)));
            evaluation += mop_up;
        } else if (evaluation < 0) {
            int d01 = 3 - rw;
            int d02 = rw - 4;
            int d11 = 3 - fw;
            int d12 = fw - 4;
            mop_up += static_cast<int>(4.7 * ((d01 > d02 ? d01 : d02) + (d11 > d12 ? d11 : d12)));
            evaluation -= mop_up;
        }
    }

    return white_turn ? evaluation : -evaluation;
}

bool AIBoard::is_over() {
    return get_legal_moves().empty();
}

uint64_t AIBoard::get_hash_from_signature(const std::string& signature) const {
    uint64_t hash = 0;
    if (signature.length() < 65) return 0;

    for (int guiSq = 0; guiSq < 64; ++guiSq) {
        char c = signature[guiSq];
        std::string piece = "..";
        if (c != '.') {
            piece = "";
            piece += std::isupper(static_cast<unsigned char>(c)) ? 'w' : 'b';
            piece += std::tolower(static_cast<unsigned char>(c));
        }
        int rank_index = 7 - (guiSq / 8);
        int file_index = guiSq % 8;
        int square = FAKE_SQUARES[rank_index * 8 + file_index];
        int pNum = getPieceNumber(piece);
        hash ^= getZobrist().hash_pieces[square][pNum];
    }

    int castle = 0;
    for (size_t idx = 65; idx < signature.length(); ++idx) {
        char c = signature[idx];
        if (c == '_') break;
        if (c == 'K') castle |= 1;
        if (c == 'Q') castle |= 2;
        if (c == 'k') castle |= 4;
        if (c == 'q') castle |= 8;
    }
    hash ^= getZobrist().hash_castle[castle];

    return hash;
}

} // namespace ai
