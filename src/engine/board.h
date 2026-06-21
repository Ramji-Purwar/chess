#ifndef BOARD_H
#define BOARD_H

#include <vector>
#include <string>
#include "piece.h"
#include "move.h"

class Board {
private:
    std::vector<Piece*> squares;
    bool whiteToMove;

    bool whiteCastleKingside;
    bool whiteCastleQueenside;
    bool blackCastleKingside;
    bool blackCastleQueenside;

    // Board index for the en passant target square, or -1 when unavailable.
    int enPassantTarget;

    void cleanup();

public:
    Board();
    Board(const Board& other);
    Board& operator=(const Board& other);
    ~Board();

    void initialize();
    void makeMove(const Move& move);

    Piece* getPiece(int square) const;
    void setPiece(int square, Piece* piece);

    bool isWhiteToMove() const;
    void switchTurn();

    bool canCastleKingside(PieceColor color) const;
    bool canCastleQueenside(PieceColor color) const;
    int getEnPassantTarget() const;
    int findKing(PieceColor color) const;
    std::string getPositionSignature() const;
};

#endif // BOARD_H