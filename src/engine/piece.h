#ifndef PIECE_H
#define PIECE_H

enum class PieceType {
    None,
    Pawn,
    Knight,
    Bishop,
    Rook,
    Queen,
    King
};

enum class PieceColor {
    White,
    Black
};

class Piece {
private:
    PieceType type;
    PieceColor color;

public:
    Piece(PieceType type, PieceColor color);

    PieceType getType() const;
    PieceColor getColor() const;
};

#endif // PIECE_H
