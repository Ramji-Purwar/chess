#ifndef MOVE_GENERATOR_H
#define MOVE_GENERATOR_H

#include <vector>
#include "board.h"
#include "move.h"
#include "piece.h"

class MoveGenerator {
public:
    std::vector<Move> generateLegalMoves(const Board& board, int square);
    std::vector<Move> generateAllLegalMoves(const Board& board, PieceColor color);
    bool isInCheck(const Board& board, PieceColor color);

private:
    void generatePawnMoves(const Board& board, int square, PieceColor color, std::vector<Move>& moves);
    void generateKnightMoves(const Board& board, int square, PieceColor color, std::vector<Move>& moves);
    void generateBishopMoves(const Board& board, int square, PieceColor color, std::vector<Move>& moves);
    void generateRookMoves(const Board& board, int square, PieceColor color, std::vector<Move>& moves);
    void generateQueenMoves(const Board& board, int square, PieceColor color, std::vector<Move>& moves);
    void generateKingMoves(const Board& board, int square, PieceColor color, std::vector<Move>& moves);

    void generateSlidingMoves(const Board& board, int square, PieceColor color,
                              const int directions[][2], int numDirections, std::vector<Move>& moves);

    bool isSquareAttacked(const Board& board, int square, PieceColor byColor);
    bool isValidSquare(int row, int col);
    bool isLegalAfterMove(const Board& board, const Move& move, PieceColor color);
};

#endif