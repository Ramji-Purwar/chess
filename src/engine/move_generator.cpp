#include "move_generator.h"
#include <cmath>

bool MoveGenerator::isValidSquare(int row, int col) {
    return row >= 0 && row < 8 && col >= 0 && col < 8;
}

void MoveGenerator::generateSlidingMoves(const Board& board, int square, PieceColor color,
                                         const int directions[][2], int numDirections,
                                         std::vector<Move>& moves) {
    int startRow = square / 8;
    int startCol = square % 8;

    for (int d = 0; d < numDirections; ++d) {
        int dr = directions[d][0];
        int dc = directions[d][1];
        int r = startRow + dr;
        int c = startCol + dc;

        while (isValidSquare(r, c)) {
            int target = r * 8 + c;
            Piece* piece = board.getPiece(target);

            if (piece == nullptr) {
                moves.push_back(Move(square, target));
            } else if (piece->getColor() != color) {
                moves.push_back(Move(square, target));
                break;
            } else {
                break;
            }

            r += dr;
            c += dc;
        }
    }
}

void MoveGenerator::generatePawnMoves(const Board& board, int square, PieceColor color,
                                      std::vector<Move>& moves) {
    int row = square / 8;
    int col = square % 8;

    int direction   = (color == PieceColor::White) ? -1 : 1;
    int startRow    = (color == PieceColor::White) ? 6 : 1;
    int promoteRow  = (color == PieceColor::White) ? 0 : 7;

    int newRow = row + direction;
    if (isValidSquare(newRow, col)) {
        int target = newRow * 8 + col;
        if (board.getPiece(target) == nullptr) {
            if (newRow == promoteRow) {
                moves.push_back(Move(square, target, PieceType::Queen));
                moves.push_back(Move(square, target, PieceType::Rook));
                moves.push_back(Move(square, target, PieceType::Bishop));
                moves.push_back(Move(square, target, PieceType::Knight));
            } else {
                moves.push_back(Move(square, target));
            }

            if (row == startRow) {
                int doubleRow = row + 2 * direction;
                int doubleTarget = doubleRow * 8 + col;
                if (board.getPiece(doubleTarget) == nullptr) {
                    moves.push_back(Move(square, doubleTarget));
                }
            }
        }
    }

    int captureCols[2] = { col - 1, col + 1 };
    for (int i = 0; i < 2; ++i) {
        int captureCol = captureCols[i];
        if (!isValidSquare(newRow, captureCol)) continue;

        int target = newRow * 8 + captureCol;
        Piece* targetPiece = board.getPiece(target);

        bool isEnPassant = (target == board.getEnPassantTarget());
        bool isCapture   = (targetPiece != nullptr && targetPiece->getColor() != color);

        if (isCapture || isEnPassant) {
            if (newRow == promoteRow) {
                moves.push_back(Move(square, target, PieceType::Queen));
                moves.push_back(Move(square, target, PieceType::Rook));
                moves.push_back(Move(square, target, PieceType::Bishop));
                moves.push_back(Move(square, target, PieceType::Knight));
            } else {
                moves.push_back(Move(square, target));
            }
        }
    }
}

void MoveGenerator::generateKnightMoves(const Board& board, int square, PieceColor color,
                                         std::vector<Move>& moves) {
    int row = square / 8;
    int col = square % 8;

    static const int offsets[8][2] = {
        {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
        { 1, -2}, { 1, 2}, { 2, -1}, { 2, 1}
    };

    for (int i = 0; i < 8; ++i) {
        int r = row + offsets[i][0];
        int c = col + offsets[i][1];
        if (!isValidSquare(r, c)) continue;

        int target = r * 8 + c;
        Piece* piece = board.getPiece(target);
        if (piece == nullptr || piece->getColor() != color) {
            moves.push_back(Move(square, target));
        }
    }
}

void MoveGenerator::generateBishopMoves(const Board& board, int square, PieceColor color,
                                         std::vector<Move>& moves) {
    static const int directions[4][2] = {
        {-1, -1}, {-1, 1}, {1, -1}, {1, 1}
    };
    generateSlidingMoves(board, square, color, directions, 4, moves);
}

void MoveGenerator::generateRookMoves(const Board& board, int square, PieceColor color,
                                       std::vector<Move>& moves) {
    static const int directions[4][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1}
    };
    generateSlidingMoves(board, square, color, directions, 4, moves);
}

void MoveGenerator::generateQueenMoves(const Board& board, int square, PieceColor color,
                                        std::vector<Move>& moves) {
    static const int directions[8][2] = {
        {-1, -1}, {-1, 0}, {-1, 1},
        { 0, -1},          { 0, 1},
        { 1, -1}, { 1, 0}, { 1, 1}
    };
    generateSlidingMoves(board, square, color, directions, 8, moves);
}

void MoveGenerator::generateKingMoves(const Board& board, int square, PieceColor color,
                                       std::vector<Move>& moves) {
    int row = square / 8;
    int col = square % 8;

    static const int offsets[8][2] = {
        {-1, -1}, {-1, 0}, {-1, 1},
        { 0, -1},          { 0, 1},
        { 1, -1}, { 1, 0}, { 1, 1}
    };

    for (int i = 0; i < 8; ++i) {
        int r = row + offsets[i][0];
        int c = col + offsets[i][1];
        if (!isValidSquare(r, c)) continue;

        int target = r * 8 + c;
        Piece* piece = board.getPiece(target);
        if (piece == nullptr || piece->getColor() != color) {
            moves.push_back(Move(square, target));
        }
    }

    PieceColor opponent = (color == PieceColor::White) ? PieceColor::Black : PieceColor::White;
    int backRank = (color == PieceColor::White) ? 7 : 0;
    int kingSquare = backRank * 8 + 4;

    if (square != kingSquare) return;
    if (isSquareAttacked(board, kingSquare, opponent)) return;

    if (board.canCastleKingside(color)) {
        int f = backRank * 8 + 5;
        int g = backRank * 8 + 6;

        if (board.getPiece(f) == nullptr && board.getPiece(g) == nullptr) {
            if (!isSquareAttacked(board, f, opponent) &&
                !isSquareAttacked(board, g, opponent)) {
                moves.push_back(Move(kingSquare, g));
            }
        }
    }

    if (board.canCastleQueenside(color)) {
        int d = backRank * 8 + 3;
        int c = backRank * 8 + 2;
        int b = backRank * 8 + 1;

        if (board.getPiece(d) == nullptr &&
            board.getPiece(c) == nullptr &&
            board.getPiece(b) == nullptr) {
            if (!isSquareAttacked(board, d, opponent) &&
                !isSquareAttacked(board, c, opponent)) {
                moves.push_back(Move(kingSquare, c));
            }
        }
    }
}

bool MoveGenerator::isSquareAttacked(const Board& board, int square, PieceColor byColor) {
    int row = square / 8;
    int col = square % 8;

    // Work backward from the target square to where an attacking pawn would sit.
    if (byColor == PieceColor::White) {
        int pawnRow = row + 1;
        for (int dc = -1; dc <= 1; dc += 2) {
            int pawnCol = col + dc;
            if (isValidSquare(pawnRow, pawnCol)) {
                Piece* piece = board.getPiece(pawnRow * 8 + pawnCol);
                if (piece != nullptr && piece->getColor() == PieceColor::White &&
                    piece->getType() == PieceType::Pawn) {
                    return true;
                }
            }
        }
    } else {
        int pawnRow = row - 1;
        for (int dc = -1; dc <= 1; dc += 2) {
            int pawnCol = col + dc;
            if (isValidSquare(pawnRow, pawnCol)) {
                Piece* piece = board.getPiece(pawnRow * 8 + pawnCol);
                if (piece != nullptr && piece->getColor() == PieceColor::Black &&
                    piece->getType() == PieceType::Pawn) {
                    return true;
                }
            }
        }
    }

    static const int knightOffsets[8][2] = {
        {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
        { 1, -2}, { 1, 2}, { 2, -1}, { 2, 1}
    };
    for (int i = 0; i < 8; ++i) {
        int r = row + knightOffsets[i][0];
        int c = col + knightOffsets[i][1];
        if (isValidSquare(r, c)) {
            Piece* piece = board.getPiece(r * 8 + c);
            if (piece != nullptr && piece->getColor() == byColor &&
                piece->getType() == PieceType::Knight) {
                return true;
            }
        }
    }

    static const int kingOffsets[8][2] = {
        {-1, -1}, {-1, 0}, {-1, 1},
        { 0, -1},          { 0, 1},
        { 1, -1}, { 1, 0}, { 1, 1}
    };
    for (int i = 0; i < 8; ++i) {
        int r = row + kingOffsets[i][0];
        int c = col + kingOffsets[i][1];
        if (isValidSquare(r, c)) {
            Piece* piece = board.getPiece(r * 8 + c);
            if (piece != nullptr && piece->getColor() == byColor &&
                piece->getType() == PieceType::King) {
                return true;
            }
        }
    }

    static const int diagonalDirections[4][2] = {
        {-1, -1}, {-1, 1}, {1, -1}, {1, 1}
    };
    for (int d = 0; d < 4; ++d) {
        int r = row + diagonalDirections[d][0];
        int c = col + diagonalDirections[d][1];
        while (isValidSquare(r, c)) {
            Piece* piece = board.getPiece(r * 8 + c);
            if (piece != nullptr) {
                if (piece->getColor() == byColor &&
                    (piece->getType() == PieceType::Bishop || piece->getType() == PieceType::Queen)) {
                    return true;
                }
                break;
            }
            r += diagonalDirections[d][0];
            c += diagonalDirections[d][1];
        }
    }

    static const int straightDirections[4][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1}
    };
    for (int d = 0; d < 4; ++d) {
        int r = row + straightDirections[d][0];
        int c = col + straightDirections[d][1];
        while (isValidSquare(r, c)) {
            Piece* piece = board.getPiece(r * 8 + c);
            if (piece != nullptr) {
                if (piece->getColor() == byColor &&
                    (piece->getType() == PieceType::Rook || piece->getType() == PieceType::Queen)) {
                    return true;
                }
                break;
            }
            r += straightDirections[d][0];
            c += straightDirections[d][1];
        }
    }

    return false;
}

bool MoveGenerator::isInCheck(const Board& board, PieceColor color) {
    int kingSquare = board.findKing(color);
    if (kingSquare < 0) return false;

    PieceColor opponent = (color == PieceColor::White) ? PieceColor::Black : PieceColor::White;
    return isSquareAttacked(board, kingSquare, opponent);
}

bool MoveGenerator::isLegalAfterMove(const Board& board, const Move& move, PieceColor color) {
    Board testBoard(board);
    testBoard.makeMove(move);
    return !isInCheck(testBoard, color);
}

std::vector<Move> MoveGenerator::generateLegalMoves(const Board& board, int square) {
    std::vector<Move> moves;

    Piece* piece = board.getPiece(square);
    if (piece == nullptr) return moves;

    PieceColor color = piece->getColor();
    if ((color == PieceColor::White) != board.isWhiteToMove()) return moves;

    switch (piece->getType()) {
        case PieceType::Pawn:   generatePawnMoves(board, square, color, moves);   break;
        case PieceType::Knight: generateKnightMoves(board, square, color, moves); break;
        case PieceType::Bishop: generateBishopMoves(board, square, color, moves); break;
        case PieceType::Rook:   generateRookMoves(board, square, color, moves);   break;
        case PieceType::Queen:  generateQueenMoves(board, square, color, moves);  break;
        case PieceType::King:   generateKingMoves(board, square, color, moves);   break;
        default: break;
    }

    std::vector<Move> legalMoves;
    for (const Move& move : moves) {
        if (isLegalAfterMove(board, move, color)) {
            legalMoves.push_back(move);
        }
    }

    return legalMoves;
}

std::vector<Move> MoveGenerator::generateAllLegalMoves(const Board& board, PieceColor color) {
    std::vector<Move> allMoves;

    for (int square = 0; square < 64; ++square) {
        Piece* piece = board.getPiece(square);
        if (piece != nullptr && piece->getColor() == color) {
            std::vector<Move> pieceMoves = generateLegalMoves(board, square);
            allMoves.insert(allMoves.end(), pieceMoves.begin(), pieceMoves.end());
        }
    }

    return allMoves;
}