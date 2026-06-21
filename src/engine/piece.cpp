#include "piece.h"

Piece::Piece(PieceType type, PieceColor color)
    : type(type), color(color) {}

PieceType Piece::getType() const {
    return type;
}

PieceColor Piece::getColor() const {
    return color;
}
