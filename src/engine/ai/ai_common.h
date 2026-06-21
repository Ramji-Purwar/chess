#ifndef AI_COMMON_H
#define AI_COMMON_H

#include <string>
#include <vector>
#include <array>
#include <cmath>
#include <map>
#include <random>

namespace ai {

// Constants
constexpr int INF = 1000000;
constexpr int MATE_EVAL = INF * 4 / 5;
constexpr int OPENING_PHASE = 6192;
constexpr int ENDGAME_PHASE = 518;
constexpr int MAX_DEPTH = 40;
constexpr int NULL_DEPTH_REDUCTION = 3;
constexpr int NODE_CHECK_INTERVAL = 1000;
constexpr int ASPIRATION = 40;

// Direction Offsets
constexpr int UP = 10;
constexpr int DOWN = -10;
constexpr int LEFT = -1;
constexpr int RIGHT = 1;

// Pawn constants
constexpr int WHITE_PAWN_STARTING_RANK = 1;
constexpr int BLACK_PAWN_STARTING_RANK = 6;
constexpr int WHITE_PROMOTION_RANK = 7;
constexpr int BLACK_PROMOTION_RANK = 0;

// Directions and Move Offsets
const std::array<int, 4> ROOK_DIRECTIONS = {UP, DOWN, LEFT, RIGHT};
const std::array<int, 4> BISHOP_DIRECTIONS = {UP + LEFT, UP + RIGHT, DOWN + LEFT, DOWN + RIGHT};
const std::array<int, 8> KING_MOVES = {UP, DOWN, LEFT, RIGHT, UP + LEFT, UP + RIGHT, DOWN + LEFT, DOWN + RIGHT};
const std::array<int, 8> KNIGHT_MOVES = {
    UP + UP + LEFT, UP + UP + RIGHT, UP + LEFT + LEFT, UP + RIGHT + RIGHT,
    DOWN + DOWN + LEFT, DOWN + DOWN + RIGHT, DOWN + LEFT + LEFT, DOWN + RIGHT + RIGHT
};

// Squares Mappings
const std::array<int, 110> TRUE_SQUARES = {
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, 0,  1,  2,  3,  4,  5,  6,  7,  -1,
    -1, 8,  9,  10, 11, 12, 13, 14, 15, -1,
    -1, 16, 17, 18, 19, 20, 21, 22, 23, -1,
    -1, 24, 25, 26, 27, 28, 29, 30, 31, -1,
    -1, 32, 33, 34, 35, 36, 37, 38, 39, -1,
    -1, 40, 41, 42, 43, 44, 45, 46, 47, -1,
    -1, 48, 49, 50, 51, 52, 53, 54, 55, -1,
    -1, 56, 57, 58, 59, 60, 61, 62, 63, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
};

const std::array<int, 64> FAKE_SQUARES = {
    11, 12, 13, 14, 15, 16, 17, 18,
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
    51, 52, 53, 54, 55, 56, 57, 58,
    61, 62, 63, 64, 65, 66, 67, 68,
    71, 72, 73, 74, 75, 76, 77, 78,
    81, 82, 83, 84, 85, 86, 87, 88
};

const std::vector<int> ALL_INVALID_SQUARES = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 19,
    20, 29,
    30, 39,
    40, 49,
    50, 59,
    60, 69,
    70, 79,
    80, 89,
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
    100, 101, 102, 103, 104, 105, 106, 107, 108, 109
};

// Coordinate Translation Helpers
inline int guiToPythonSq(int guiSq) {
    int row = guiSq / 8;
    int col = guiSq % 8;
    return (7 - row) * 8 + col;
}

inline int pythonToGuiSq(int pythonSq) {
    int row = pythonSq / 8;
    int col = pythonSq % 8;
    return (7 - row) * 8 + col;
}

inline int guiToMailboxSq(int guiSq) {
    int pythonSq = guiToPythonSq(guiSq);
    return FAKE_SQUARES[pythonSq];
}

inline int mailboxSqToGui(int mailboxSq) {
    int pythonSq = TRUE_SQUARES[mailboxSq];
    return pythonToGuiSq(pythonSq);
}

// Move Representation
struct AIMove {
    std::string start_piece; // e.g. "wp"
    int start;               // mailbox index
    int end;                 // mailbox index
    std::string special;     // "N" (normal), "D" (double push), "C" (castle), "P" + promotion (e.g. "Pq")

    AIMove() : start_piece(".."), start(-1), end(-1), special("N") {}
    AIMove(const std::string& piece, int s, int e, const std::string& sp)
        : start_piece(piece), start(s), end(e), special(sp) {}

    bool operator==(const AIMove& other) const {
        return start == other.start && end == other.end && special == other.special;
    }
    bool operator!=(const AIMove& other) const {
        return !(*this == other);
    }
};

// Castle rights helper
inline int getCastleRights(const std::string& piece) {
    if (piece == "wk") return 1;
    if (piece == "wq") return 2;
    if (piece == "bk") return 4;
    if (piece == "bq") return 8;
    return 0;
}

inline int getRemoveCastleRights(const std::string& piece) {
    if (piece == "wk") return 14;
    if (piece == "wq") return 13;
    if (piece == "bk") return 11;
    if (piece == "bq") return 7;
    return 15;
}

inline int getRooksPosition(const std::string& key) {
    if (key == "wk") return 18; // FAKE_SQUARES[7]
    if (key == "wq") return 11; // FAKE_SQUARES[0]
    if (key == "bk") return 88; // FAKE_SQUARES[63]
    if (key == "bq") return 81; // FAKE_SQUARES[56]
    return -1;
}

inline std::string getPositionRooks(int square) {
    if (square == 18) return "wk";
    if (square == 11) return "wq";
    if (square == 88) return "bk";
    if (square == 81) return "bq";
    return "";
}

inline bool getCastleRookPosition(int endSquare, int& rookStart, int& rookEnd) {
    if (endSquare == 13) { rookStart = 11; rookEnd = 14; return true; }
    if (endSquare == 17) { rookStart = 18; rookEnd = 16; return true; }
    if (endSquare == 83) { rookStart = 81; rookEnd = 84; return true; }
    if (endSquare == 87) { rookStart = 88; rookEnd = 86; return true; }
    return false;
}

// Phase values
inline int getPhaseValue(char pieceChar) {
    switch (pieceChar) {
        case 'r': return 477;
        case 'n': return 337;
        case 'b': return 365;
        case 'q': return 1025;
        default: return 0;
    }
}

inline int getPhaseValueMid(char pieceChar) {
    switch (pieceChar) {
        case 'k': return 12000;
        case 'p': return 82;
        case 'r': return 477;
        case 'n': return 337;
        case 'b': return 365;
        case 'q': return 1025;
        default: return 0;
    }
}

inline int getPhaseValueEnd(char pieceChar) {
    switch (pieceChar) {
        case 'k': return 12000;
        case 'p': return 94;
        case 'r': return 512;
        case 'n': return 281;
        case 'b': return 297;
        case 'q': return 936;
        default: return 0;
    }
}

// MVV-LVA Scoring Helper
inline int getMvvLvaScore(char attacker, char victim) {
    int vVal = 0;
    switch (victim) {
        case 'p': vVal = 100; break;
        case 'n': vVal = 200; break;
        case 'b': vVal = 300; break;
        case 'r': vVal = 400; break;
        case 'q': vVal = 500; break;
        case 'k': vVal = 600; break;
    }
    int aVal = 0;
    switch (attacker) {
        case 'p': aVal = 5; break;
        case 'n': aVal = 4; break;
        case 'b': aVal = 3; break;
        case 'r': aVal = 2; break;
        case 'q': aVal = 1; break;
        case 'k': aVal = 0; break;
    }
    return vVal + aVal;
}

// Piece numbers for history table
inline int getPieceNumber(const std::string& piece) {
    if (piece == "wp") return 0;
    if (piece == "wr") return 1;
    if (piece == "wn") return 2;
    if (piece == "wb") return 3;
    if (piece == "wq") return 4;
    if (piece == "wk") return 5;
    if (piece == "bp") return 6;
    if (piece == "br") return 7;
    if (piece == "bn") return 8;
    if (piece == "bb") return 9;
    if (piece == "bq") return 10;
    if (piece == "bk") return 11;
    return 12;
}

// PST tables
const std::array<int, 110> PAWN_TABLE_MID_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -35, -1, -20, -23, -15, 24, 38, -22, 0,
    0, -26, -4, -4, -10, 3, 3, 33, -12, 0,
    0, -27, -2, -5, 12, 17, 6, 10, -25, 0,
    0, -14, 13, 6, 21, 23, 12, 17, -23, 0,
    0, -6, 7, 26, 31, 65, 56, 25, -20, 0,
    0, 98, 134, 61, 95, 68, 126, 34, -11, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> PAWN_TABLE_MID_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 98, 134, 61, 95, 68, 126, 34, -11, 0,
    0, -6, 7, 26, 31, 65, 56, 25, -20, 0,
    0, -14, 13, 6, 21, 23, 12, 17, -23, 0,
    0, -27, -2, -5, 12, 17, 6, 10, -25, 0,
    0, -26, -4, -4, -10, 3, 3, 33, -12, 0,
    0, -35, -1, -20, -23, -15, 24, 38, -22, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> PAWN_TABLE_END_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 13, 8, 8, 10, 13, 0, 2, -7, 0,
    0, 4, 7, -6, 1, 0, -5, -1, -8, 0,
    0, 13, 9, -3, -7, -7, -8, 3, -1, 0,
    0, 32, 24, 13, 5, -2, 4, 17, 17, 0,
    0, 94, 100, 85, 67, 56, 53, 82, 84, 0,
    0, 178, 173, 158, 134, 147, 132, 165, 187, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> PAWN_TABLE_END_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 178, 173, 158, 134, 147, 132, 165, 187, 0,
    0, 94, 100, 85, 67, 56, 53, 82, 84, 0,
    0, 32, 24, 13, 5, -2, 4, 17, 17, 0,
    0, 13, 9, -3, -7, -7, -8, 3, -1, 0,
    0, 4, 7, -6, 1, 0, -5, -1, -8, 0,
    0, 13, 8, 8, 10, 13, 0, 2, -7, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KNIGHT_TABLE_MID_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -105, -21, -58, -33, -17, -28, -19, -23, 0,
    0, -29, -53, -12, -3, -1, 18, -14, -19, 0,
    0, -23, -9, 12, 10, 19, 17, 25, -16, 0,
    0, -13, 4, 16, 13, 28, 19, 21, -8, 0,
    0, -9, 17, 19, 53, 37, 69, 18, 22, 0,
    0, -47, 60, 37, 65, 84, 129, 73, 44, 0,
    0, -73, -41, 72, 36, 23, 62, 7, -17, 0,
    0, -167, -89, -34, -49, 61, -97, -15, -107, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KNIGHT_TABLE_MID_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -167, -89, -34, -49, 61, -97, -15, -107, 0,
    0, -73, -41, 72, 36, 23, 62, 7, -17, 0,
    0, -47, 60, 37, 65, 84, 129, 73, 44, 0,
    0, -9, 17, 19, 53, 37, 69, 18, 22, 0,
    0, -13, 4, 16, 13, 28, 19, 21, -8, 0,
    0, -23, -9, 12, 10, 19, 17, 25, -16, 0,
    0, -29, -53, -12, -3, -1, 18, -14, -19, 0,
    0, -105, -21, -58, -33, -17, -28, -19, -23, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KNIGHT_TABLE_END_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -29, -51, -23, -15, -22, -18, -50, -64, 0,
    0, -42, -20, -10, -5, -2, -20, -23, -44, 0,
    0, -23, -3, -1, 15, 10, -3, -20, -22, 0,
    0, -18, -6, 16, 25, 16, 17, 4, -18, 0,
    0, -17, 3, 22, 22, 22, 11, 8, -18, 0,
    0, -24, -20, 10, 9, -1, -9, -19, -41, 0,
    0, -25, -8, -25, -2, -9, -25, -24, -52, 0,
    0, -58, -38, -13, -28, -31, -27, -63, -99, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KNIGHT_TABLE_END_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -58, -38, -13, -28, -31, -27, -63, -99, 0,
    0, -25, -8, -25, -2, -9, -25, -24, -52, 0,
    0, -24, -20, 10, 9, -1, -9, -19, -41, 0,
    0, -17, 3, 22, 22, 22, 11, 8, -18, 0,
    0, -18, -6, 16, 25, 16, 17, 4, -18, 0,
    0, -23, -3, -1, 15, 10, -3, -20, -22, 0,
    0, -42, -20, -10, -5, -2, -20, -23, -44, 0,
    0, -29, -51, -23, -15, -22, -18, -50, -64, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> BISHOP_TABLE_MID_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -33, -3, -14, -21, -13, -12, -39, -21, 0,
    0, 4, 15, 16, 0, 7, 21, 33, 1, 0,
    0, 0, 15, 15, 15, 14, 27, 18, 10, 0,
    0, -6, 13, 13, 26, 34, 12, 10, 4, 0,
    0, -4, 5, 19, 50, 37, 37, 7, -2, 0,
    0, -16, 37, 43, 40, 35, 50, 37, -2, 0,
    0, -26, 16, -18, -13, 30, 59, 18, -47, 0,
    0, -29, 4, -82, -37, -25, -42, 7, -8, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> BISHOP_TABLE_MID_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -29, 4, -82, -37, -25, -42, 7, -8, 0,
    0, -26, 16, -18, -13, 30, 59, 18, -47, 0,
    0, -16, 37, 43, 40, 35, 50, 37, -2, 0,
    0, -4, 5, 19, 50, 37, 37, 7, -2, 0,
    0, -6, 13, 13, 26, 34, 12, 10, 4, 0,
    0, 0, 15, 15, 15, 14, 27, 18, 10, 0,
    0, 4, 15, 16, 0, 7, 21, 33, 1, 0,
    0, -33, -3, -14, -21, -13, -12, -39, -21, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> BISHOP_TABLE_END_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -23, -9, -23, -5, -9, -16, -5, -17, 0,
    0, -14, -18, -7, -1, 4, -9, -15, -27, 0,
    0, -12, -3, 8, 10, 13, 3, -7, -15, 0,
    0, -6, 3, 13, 19, 7, 10, -3, -9, 0,
    0, -3, 9, 12, 9, 14, 10, 3, 2, 0,
    0, 2, -8, 0, -1, -2, 6, 0, 4, 0,
    0, -8, -4, 7, -12, -3, -13, -4, -14, 0,
    0, -14, -21, -11, -8, -7, -9, -17, -24, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> BISHOP_TABLE_END_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -14, -21, -11, -8, -7, -9, -17, -24, 0,
    0, -8, -4, 7, -12, -3, -13, -4, -14, 0,
    0, 2, -8, 0, -1, -2, 6, 0, 4, 0,
    0, -3, 9, 12, 9, 14, 10, 3, 2, 0,
    0, -6, 3, 13, 19, 7, 10, -3, -9, 0,
    0, -12, -3, 8, 10, 13, 3, -7, -15, 0,
    0, -14, -18, -7, -1, 4, -9, -15, -27, 0,
    0, -23, -9, -23, -5, -9, -16, -5, -17, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> ROOK_TABLE_MID_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -19, -13, 1, 17, 16, 7, -37, -26, 0,
    0, -44, -16, -20, -9, -1, 11, -6, -71, 0,
    0, -45, -25, -16, -17, 3, 0, -5, -33, 0,
    0, -36, -26, -12, -1, 9, -7, 6, -23, 0,
    0, -24, -11, 7, 26, 24, 35, -8, -20, 0,
    0, -5, 19, 26, 36, 17, 45, 61, 16, 0,
    0, 27, 32, 58, 62, 80, 67, 26, 44, 0,
    0, 32, 42, 32, 51, 63, 9, 31, 43, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> ROOK_TABLE_MID_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 32, 42, 32, 51, 63, 9, 31, 43, 0,
    0, 27, 32, 58, 62, 80, 67, 26, 44, 0,
    0, -5, 19, 26, 36, 17, 45, 61, 16, 0,
    0, -24, -11, 7, 26, 24, 35, -8, -20, 0,
    0, -36, -26, -12, -1, 9, -7, 6, -23, 0,
    0, -45, -25, -16, -17, 3, 0, -5, -33, 0,
    0, -44, -16, -20, -9, -1, 11, -6, -71, 0,
    0, -19, -13, 1, 17, 16, 7, -37, -26, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> ROOK_TABLE_END_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -9, 2, 3, -1, -5, -13, 4, -20, 0,
    0, -6, -6, 0, 2, -9, -9, -11, -3, 0,
    0, -4, 0, -5, -1, -7, -12, -8, -16, 0,
    0, 3, 5, 8, 4, -5, -6, -8, -11, 0,
    0, 4, 3, 13, 1, 2, 1, -1, 2, 0,
    0, 7, 7, 7, 5, 4, -3, -5, -3, 0,
    0, 11, 13, 13, 11, -3, 3, 8, 3, 0,
    0, 13, 10, 18, 15, 12, 12, 8, 5, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> ROOK_TABLE_END_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 13, 10, 18, 15, 12, 12, 8, 5, 0,
    0, 11, 13, 13, 11, -3, 3, 8, 3, 0,
    0, 7, 7, 7, 5, 4, -3, -5, -3, 0,
    0, 4, 3, 13, 1, 2, 1, -1, 2, 0,
    0, 3, 5, 8, 4, -5, -6, -8, -11, 0,
    0, -4, 0, -5, -1, -7, -12, -8, -16, 0,
    0, -6, -6, 0, 2, -9, -9, -11, -3, 0,
    0, -9, 2, 3, -1, -5, -13, 4, -20, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> QUEEN_TABLE_MID_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -1, -18, -9, 10, -15, -25, -31, -50, 0,
    0, -35, -8, 11, 2, 8, 15, -3, 1, 0,
    0, -14, 2, -11, -2, -5, 2, 14, 5, 0,
    0, -9, -26, -9, -10, -2, -4, 3, -3, 0,
    0, -27, -27, -16, -16, -1, 17, -2, 1, 0,
    0, -13, -17, 7, 8, 29, 56, 47, 57, 0,
    0, -24, -39, -5, 1, -16, 57, 28, 54, 0,
    0, -28, 0, 29, 12, 59, 44, 43, 45, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> QUEEN_TABLE_MID_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -28, 0, 29, 12, 59, 44, 43, 45, 0,
    0, -24, -39, -5, 1, -16, 57, 28, 54, 0,
    0, -13, -17, 7, 8, 29, 56, 47, 57, 0,
    0, -27, -27, -16, -16, -1, 17, -2, 1, 0,
    0, -9, -26, -9, -10, -2, -4, 3, -3, 0,
    0, -14, 2, -11, -2, -5, 2, 14, 5, 0,
    0, -35, -8, 11, 2, 8, 15, -3, 1, 0,
    0, -1, -18, -9, 10, -15, -25, -31, -50, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> QUEEN_TABLE_END_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -33, -28, -22, -43, -5, -32, -20, -41, 0,
    0, -22, -23, -30, -16, -16, -23, -36, -32, 0,
    0, -16, -27, 15, 6, 9, 17, 10, 5, 0,
    0, -18, 28, 19, 47, 31, 34, 39, 23, 0,
    0, 3, 22, 24, 45, 57, 40, 57, 36, 0,
    0, -20, 6, 9, 49, 47, 35, 19, 9, 0,
    0, -17, 20, 32, 41, 58, 25, 30, 0, 0,
    0, -9, 22, 22, 27, 27, 19, 10, 20, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> QUEEN_TABLE_END_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -9, 22, 22, 27, 27, 19, 10, 20, 0,
    0, -17, 20, 32, 41, 58, 25, 30, 0, 0,
    0, -20, 6, 9, 49, 47, 35, 19, 9, 0,
    0, 3, 22, 24, 45, 57, 40, 57, 36, 0,
    0, -18, 28, 19, 47, 31, 34, 39, 23, 0,
    0, -16, -27, 15, 6, 9, 17, 10, 5, 0,
    0, -22, -23, -30, -16, -16, -23, -36, -32, 0,
    0, -33, -28, -22, -43, -5, -32, -20, -41, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KING_TABLE_MID_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -15, 36, 12, -54, 8, -28, 24, 14, 0,
    0, 1, 7, -8, -64, -43, -16, 9, 8, 0,
    0, -14, -14, -22, -46, -44, -30, -15, -27, 0,
    0, -49, -1, -27, -39, -46, -44, -33, -51, 0,
    0, -17, -20, -12, -27, -30, -25, -14, -36, 0,
    0, -9, 24, 2, -16, -20, 6, 22, -22, 0,
    0, 29, -1, -20, -7, -8, -4, -38, -29, 0,
    0, -65, 23, 16, -15, -56, -34, 2, 13, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KING_TABLE_MID_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -65, 23, 16, -15, -56, -34, 2, 13, 0,
    0, 29, -1, -20, -7, -8, -4, -38, -29, 0,
    0, -9, 24, 2, -16, -20, 6, 22, -22, 0,
    0, -17, -20, -12, -27, -30, -25, -14, -36, 0,
    0, -49, -1, -27, -39, -46, -44, -33, -51, 0,
    0, -14, -14, -22, -46, -44, -30, -15, -27, 0,
    0, 1, 7, -8, -64, -43, -16, 9, 8, 0,
    0, -15, 36, 12, -54, 8, -28, 24, 14, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KING_TABLE_END_WHITE = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -53, -34, -21, -11, -28, -14, -24, -43, 0,
    0, -27, -11, 4, 13, 14, 4, -5, -17, 0,
    0, -19, -3, 11, 21, 23, 16, 7, -9, 0,
    0, -18, -4, 21, 24, 27, 23, 9, -11, 0,
    0, -8, 22, 24, 27, 26, 33, 26, 3, 0,
    0, 10, 17, 23, 15, 20, 45, 44, 13, 0,
    0, -12, 17, 14, 17, 17, 38, 23, 11, 0,
    0, -74, -35, -18, -18, -11, 15, 4, -17, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> KING_TABLE_END_BLACK = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -74, -35, -18, -18, -11, 15, 4, -17, 0,
    0, -12, 17, 14, 17, 17, 38, 23, 11, 0,
    0, 10, 17, 23, 15, 20, 45, 44, 13, 0,
    0, -8, 22, 24, 27, 26, 33, 26, 3, 0,
    0, -18, -4, 21, 24, 27, 23, 9, -11, 0,
    0, -19, -3, 11, 21, 23, 16, 7, -9, 0,
    0, -27, -11, 4, 13, 14, 4, -5, -17, 0,
    0, -53, -34, -21, -11, -28, -14, -24, -43, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

const std::array<int, 110> EMPTY_TABLE = {0};

inline const std::array<int, 110>& getMidValues(const std::string& piece) {
    if (piece == "wp") return PAWN_TABLE_MID_WHITE;
    if (piece == "wr") return ROOK_TABLE_MID_WHITE;
    if (piece == "wn") return KNIGHT_TABLE_MID_WHITE;
    if (piece == "wb") return BISHOP_TABLE_MID_WHITE;
    if (piece == "wq") return QUEEN_TABLE_MID_WHITE;
    if (piece == "wk") return KING_TABLE_MID_WHITE;
    if (piece == "bp") return PAWN_TABLE_MID_BLACK;
    if (piece == "br") return ROOK_TABLE_MID_BLACK;
    if (piece == "bn") return KNIGHT_TABLE_MID_BLACK;
    if (piece == "bb") return BISHOP_TABLE_MID_BLACK;
    if (piece == "bq") return QUEEN_TABLE_MID_BLACK;
    if (piece == "bk") return KING_TABLE_MID_BLACK;
    return EMPTY_TABLE;
}

inline const std::array<int, 110>& getEndValues(const std::string& piece) {
    if (piece == "wp") return PAWN_TABLE_END_WHITE;
    if (piece == "wr") return ROOK_TABLE_END_WHITE;
    if (piece == "wn") return KNIGHT_TABLE_END_WHITE;
    if (piece == "wb") return BISHOP_TABLE_END_WHITE;
    if (piece == "wq") return QUEEN_TABLE_END_WHITE;
    if (piece == "wk") return KING_TABLE_END_WHITE;
    if (piece == "bp") return PAWN_TABLE_END_BLACK;
    if (piece == "br") return ROOK_TABLE_END_BLACK;
    if (piece == "bn") return KNIGHT_TABLE_END_BLACK;
    if (piece == "bb") return BISHOP_TABLE_END_BLACK;
    if (piece == "bq") return QUEEN_TABLE_END_BLACK;
    if (piece == "bk") return KING_TABLE_END_BLACK;
    return EMPTY_TABLE;
}

constexpr int PREV_MOVE_BONUS = INF;
constexpr int PV_BONUS = INF * 2 / 3;
constexpr int PROMOTION_BONUS = INF / 2;
constexpr int MVV_LVA_BONUS = INF / 3;
constexpr int FIRST_KILLER_MOVE_BONUS = INF / 4;
constexpr int SECOND_KILLER_MOVE_BONUS = INF / 5;

// Zobrist Hashing variables
struct Zobrist {
    uint64_t hash_castle[16];
    uint64_t hash_pieces[110][13]; // 110 squares, 13 piece types

    Zobrist() {
        std::mt19937_64 rng(123456789ULL);
        for (int i = 0; i < 16; ++i) {
            hash_castle[i] = rng();
        }
        for (int sq = 0; sq < 110; ++sq) {
            for (int p = 0; p < 13; ++p) {
                if (p == 12) {
                    hash_pieces[sq][p] = 0; // Empty square hash is 0
                } else {
                    hash_pieces[sq][p] = rng();
                }
            }
        }
    }
};

inline const Zobrist& getZobrist() {
    static Zobrist zobrist;
    return zobrist;
}

} // namespace ai

#endif // AI_COMMON_H
