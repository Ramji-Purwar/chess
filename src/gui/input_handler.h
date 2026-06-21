#ifndef INPUT_HANDLER_H
#define INPUT_HANDLER_H

#include <SFML/Graphics.hpp>
#include <vector>
#include "../engine/board.h"
#include "../engine/move.h"
#include "../engine/move_generator.h"

class InputHandler {
private:
    static constexpr int SQUARE_SIZE = 100;

public:
    int screenToSquare(sf::Vector2i mousePos);
    bool handleMouseClick(sf::Vector2i mousePos, const Board& board,
                          int& selectedSquare, std::vector<Move>& legalMoves,
                          Move& resultMove, MoveGenerator& moveGen);
};

#endif // INPUT_HANDLER_H
