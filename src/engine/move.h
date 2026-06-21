#ifndef MOVE_H
#define MOVE_H

#include "piece.h"

struct Move {
    int from;
    int to;
    PieceType promotion;

    Move()
        : from(-1), to(-1), promotion(PieceType::None) {}

    Move(int from, int to, PieceType promotion = PieceType::None)
        : from(from), to(to), promotion(promotion) {}
};

#endif // MOVE_H
