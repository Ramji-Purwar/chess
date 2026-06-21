#include "input_handler.h"

int InputHandler::screenToSquare(sf::Vector2i mousePos) {
    int col = mousePos.x / SQUARE_SIZE;
    int row = mousePos.y / SQUARE_SIZE;

    if (row < 0 || row > 7 || col < 0 || col > 7) {
        return -1;
    }

    return row * 8 + col;
}

bool InputHandler::handleMouseClick(sf::Vector2i mousePos, const Board& board,
                                     int& selectedSquare, std::vector<Move>& legalMoves,
                                     Move& resultMove, MoveGenerator& moveGen) {
    int clickedSquare = screenToSquare(mousePos);
    if (clickedSquare < 0) {
        return false;
    }

    if (selectedSquare >= 0) {
        for (const auto& move : legalMoves) {
            if (move.to == clickedSquare) {
                resultMove = move;
                selectedSquare = -1;
                legalMoves.clear();
                return true;
            }
        }
    }

    const Piece* piece = board.getPiece(clickedSquare);
    if (piece) {
        PieceColor expectedColor = board.isWhiteToMove() ? PieceColor::White : PieceColor::Black;
        if (piece->getColor() == expectedColor) {
            selectedSquare = clickedSquare;
            legalMoves = moveGen.generateLegalMoves(board, clickedSquare);
            return false;
        }
    }

    selectedSquare = -1;
    legalMoves.clear();
    return false;
}