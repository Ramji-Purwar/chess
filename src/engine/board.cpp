#include "board.h"
#include <cmath>
#include <cctype>

Board::Board()
    : squares(64, nullptr),
      whiteToMove(true),
      whiteCastleKingside(true),
      whiteCastleQueenside(true),
      blackCastleKingside(true),
      blackCastleQueenside(true),
      enPassantTarget(-1) {}

Board::Board(const Board& other)
    : squares(64, nullptr),
      whiteToMove(other.whiteToMove),
      whiteCastleKingside(other.whiteCastleKingside),
      whiteCastleQueenside(other.whiteCastleQueenside),
      blackCastleKingside(other.blackCastleKingside),
      blackCastleQueenside(other.blackCastleQueenside),
      enPassantTarget(other.enPassantTarget) {
    for (int i = 0; i < 64; i++) {
        if (other.squares[i]) {
            squares[i] = new Piece(*other.squares[i]);
        }
    }
}

Board& Board::operator=(const Board& other) {
    if (this == &other) return *this;

    cleanup();

    whiteToMove          = other.whiteToMove;
    whiteCastleKingside  = other.whiteCastleKingside;
    whiteCastleQueenside = other.whiteCastleQueenside;
    blackCastleKingside  = other.blackCastleKingside;
    blackCastleQueenside = other.blackCastleQueenside;
    enPassantTarget      = other.enPassantTarget;

    for (int i = 0; i < 64; i++) {
        squares[i] = other.squares[i] ? new Piece(*other.squares[i]) : nullptr;
    }
    return *this;
}

Board::~Board() {
    cleanup();
}

void Board::cleanup() {
    for (int i = 0; i < 64; i++) {
        delete squares[i];
        squares[i] = nullptr;
    }
}

void Board::initialize() {
    cleanup();

    const PieceType backRank[] = {
        PieceType::Rook,   PieceType::Knight, PieceType::Bishop, PieceType::Queen,
        PieceType::King,   PieceType::Bishop, PieceType::Knight, PieceType::Rook
    };

    for (int col = 0; col < 8; col++) {
        squares[0 * 8 + col] = new Piece(backRank[col], PieceColor::Black);
        squares[1 * 8 + col] = new Piece(PieceType::Pawn, PieceColor::Black);
        squares[6 * 8 + col] = new Piece(PieceType::Pawn, PieceColor::White);
        squares[7 * 8 + col] = new Piece(backRank[col], PieceColor::White);
    }

    whiteToMove          = true;
    whiteCastleKingside  = true;
    whiteCastleQueenside = true;
    blackCastleKingside  = true;
    blackCastleQueenside = true;
    enPassantTarget      = -1;
}

void Board::makeMove(const Move& move) {
    Piece* movingPiece = squares[move.from];
    if (!movingPiece) return;

    PieceType  type  = movingPiece->getType();
    PieceColor color = movingPiece->getColor();

    int fromRow = move.from / 8;
    int fromCol = move.from % 8;
    int toRow   = move.to   / 8;
    int toCol   = move.to   % 8;

    // En passant captures the pawn beside the origin square, not the target square.
    if (type == PieceType::Pawn && move.to == enPassantTarget) {
        int capturedSquare = fromRow * 8 + toCol;
        delete squares[capturedSquare];
        squares[capturedSquare] = nullptr;
    }

    if (squares[move.to]) {
        delete squares[move.to];
        squares[move.to] = nullptr;
    }

    squares[move.to]   = movingPiece;
    squares[move.from] = nullptr;

    if (type == PieceType::Pawn && move.promotion != PieceType::None) {
        delete squares[move.to];
        squares[move.to] = new Piece(move.promotion, color);
    }

    // Castling is encoded as the king moving two files.
    if (type == PieceType::King && std::abs(toCol - fromCol) == 2) {
        if (toCol > fromCol) {
            int rookFrom = fromRow * 8 + 7;
            int rookTo   = fromRow * 8 + 5;
            squares[rookTo]   = squares[rookFrom];
            squares[rookFrom] = nullptr;
        } else {
            int rookFrom = fromRow * 8 + 0;
            int rookTo   = fromRow * 8 + 3;
            squares[rookTo]   = squares[rookFrom];
            squares[rookFrom] = nullptr;
        }
    }

    enPassantTarget = -1;
    if (type == PieceType::Pawn && std::abs(toRow - fromRow) == 2) {
        enPassantTarget = ((fromRow + toRow) / 2) * 8 + fromCol;
    }

    if (type == PieceType::King) {
        if (color == PieceColor::White) {
            whiteCastleKingside  = false;
            whiteCastleQueenside = false;
        } else {
            blackCastleKingside  = false;
            blackCastleQueenside = false;
        }
    }

    // Moving from or capturing on a rook's home square removes that castling option.
    if (move.from == 63 || move.to == 63) whiteCastleKingside  = false;
    if (move.from == 56 || move.to == 56) whiteCastleQueenside = false;
    if (move.from ==  7 || move.to ==  7) blackCastleKingside  = false;
    if (move.from ==  0 || move.to ==  0) blackCastleQueenside = false;

    whiteToMove = !whiteToMove;
}

Piece* Board::getPiece(int square) const {
    if (square < 0 || square >= 64) return nullptr;
    return squares[square];
}

void Board::setPiece(int square, Piece* piece) {
    if (square < 0 || square >= 64) return;
    delete squares[square];
    squares[square] = piece;
}

bool Board::isWhiteToMove() const {
    return whiteToMove;
}

void Board::switchTurn() {
    whiteToMove = !whiteToMove;
}

bool Board::canCastleKingside(PieceColor color) const {
    return (color == PieceColor::White) ? whiteCastleKingside : blackCastleKingside;
}

bool Board::canCastleQueenside(PieceColor color) const {
    return (color == PieceColor::White) ? whiteCastleQueenside : blackCastleQueenside;
}

int Board::getEnPassantTarget() const {
    return enPassantTarget;
}

int Board::findKing(PieceColor color) const {
    for (int i = 0; i < 64; i++) {
        if (squares[i] &&
            squares[i]->getType()  == PieceType::King &&
            squares[i]->getColor() == color) {
            return i;
        }
    }
    return -1;
}

std::string Board::getPositionSignature() const {
    std::string signature = "";
    for (int i = 0; i < 64; ++i) {
        Piece* p = squares[i];
        if (!p) {
            signature += '.';
        } else {
            char c = '.';
            switch (p->getType()) {
                case PieceType::Pawn:   c = 'p'; break;
                case PieceType::Knight: c = 'n'; break;
                case PieceType::Bishop: c = 'b'; break;
                case PieceType::Rook:   c = 'r'; break;
                case PieceType::Queen:  c = 'q'; break;
                case PieceType::King:   c = 'k'; break;
                default:                c = '.'; break;
            }
            if (p->getColor() == PieceColor::White) {
                c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
            }
            signature += c;
        }
    }

    signature += whiteToMove ? 'w' : 'b';

    if (whiteCastleKingside)  signature += 'K';
    if (whiteCastleQueenside) signature += 'Q';
    if (blackCastleKingside)  signature += 'k';
    if (blackCastleQueenside) signature += 'q';

    signature += '_' + std::to_string(enPassantTarget);

    return signature;
}