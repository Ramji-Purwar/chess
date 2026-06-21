#ifndef RENDERER_H
#define RENDERER_H

#include <SFML/Graphics.hpp>
#include <map>
#include <string>
#include <vector>
#include "../engine/board.h"

class Renderer {
private:
    sf::RenderWindow& window;
    std::map<std::string, sf::Texture> textures;
    static constexpr int SQUARE_SIZE = 100;

    void drawCheckHighlight(int square);
    void drawLastMoveHighlight(const Move& lastMove);
    void drawPromotionMenu(PieceColor color, sf::Vector2i mousePos);
    void drawStartMenu(sf::Vector2i mousePos);
    void drawGameOverMenu(const std::string& status, sf::Vector2i mousePos);

    sf::Font font;
    bool hasFont = false;

public:
    explicit Renderer(sf::RenderWindow& window);

    void loadTextures();
    void drawBoard();
    void drawPieces(const Board& board);
    void drawHighlights(const Board& board, const std::vector<int>& squares);
    void drawSelectedSquare(int square);
    void render(const Board& board, int selectedSquare,
                const std::vector<int>& legalMoveSquares,
                int checkKingSquare = -1,
                bool isPromoting = false,
                PieceColor promotingColor = PieceColor::White,
                sf::Vector2i mousePos = {0, 0},
                bool isShowingMenu = false,
                Move lastMove = Move(),
                bool isGameOver = false,
                const std::string& gameStatus = "");
};

#endif // RENDERER_H
