#include "renderer.h"
#include <algorithm>
#include <stdexcept>

static std::string pieceKey(const Piece* piece) {
    std::string key;
    key += (piece->getColor() == PieceColor::White) ? 'w' : 'b';
    switch (piece->getType()) {
        case PieceType::Pawn:   key += 'p'; break;
        case PieceType::Knight: key += 'n'; break;
        case PieceType::Bishop: key += 'b'; break;
        case PieceType::Rook:   key += 'r'; break;
        case PieceType::Queen:  key += 'q'; break;
        case PieceType::King:   key += 'k'; break;
        default: break;
    }
    return key;
}

Renderer::Renderer(sf::RenderWindow& window) : window(window) {}

void Renderer::loadTextures() {
    const std::string pieces[] = {
        "wp", "wn", "wb", "wr", "wq", "wk",
        "bp", "bn", "bb", "br", "bq", "bk"
    };

    for (const auto& name : pieces) {
        sf::Texture tex;
        std::string path = "assets/pieces/" + name + ".png";
        if (!tex.loadFromFile(path)) {
            throw std::runtime_error("Failed to load texture: " + path);
        }
        textures[name] = std::move(tex);
    }

    // Load system font safely for premium typography UI
    hasFont = font.openFromFile("C:/Windows/Fonts/arial.ttf");
    if (!hasFont) {
        hasFont = font.openFromFile("C:/Windows/Fonts/calibri.ttf");
    }
    if (!hasFont) {
        hasFont = font.openFromFile("C:/Windows/Fonts/segoeui.ttf");
    }
}

void Renderer::drawBoard() {
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            sf::RectangleShape square({static_cast<float>(SQUARE_SIZE),
                                       static_cast<float>(SQUARE_SIZE)});
            square.setPosition({static_cast<float>(col * SQUARE_SIZE),
                                static_cast<float>(row * SQUARE_SIZE)});

            if ((row + col) % 2 == 0) {
                square.setFillColor(sf::Color(240, 217, 181));
            } else {
                square.setFillColor(sf::Color(181, 136, 99));
            }

            window.draw(square);
        }
    }
}

void Renderer::drawPieces(const Board& board) {
    for (int sq = 0; sq < 64; ++sq) {
        const Piece* piece = board.getPiece(sq);
        if (!piece) continue;

        std::string key = pieceKey(piece);
        const sf::Texture& tex = textures.at(key);
        sf::Sprite sprite(tex);

        sf::Vector2u texSize = tex.getSize();
        float targetSize = SQUARE_SIZE * 0.68f;
        float scale = targetSize / static_cast<float>(std::max(texSize.x, texSize.y));
        sprite.setScale({scale, scale});

        int row = sq / 8;
        int col = sq % 8;
        float pieceWidth = static_cast<float>(texSize.x) * scale;
        float pieceHeight = static_cast<float>(texSize.y) * scale;
        float x = col * SQUARE_SIZE + (SQUARE_SIZE - pieceWidth) / 2.0f;
        float y = row * SQUARE_SIZE + (SQUARE_SIZE - pieceHeight) / 2.0f;
        sprite.setPosition({x, y});

        window.draw(sprite);
    }
}

void Renderer::drawSelectedSquare(int square) {
    if (square < 0) return;

    int row = square / 8;
    int col = square % 8;

    sf::RectangleShape highlight({static_cast<float>(SQUARE_SIZE),
                                   static_cast<float>(SQUARE_SIZE)});
    highlight.setPosition({static_cast<float>(col * SQUARE_SIZE),
                           static_cast<float>(row * SQUARE_SIZE)});
    highlight.setFillColor(sf::Color(255, 255, 0, 100));

    window.draw(highlight);
}

void Renderer::drawHighlights(const Board& board, const std::vector<int>& squares) {
    for (int sq : squares) {
        int row = sq / 8;
        int col = sq % 8;

        if (board.getPiece(sq) != nullptr) {
            // Occupied square (capture move): draw a red outline ring
            float outerRadius = SQUARE_SIZE * 0.43f;
            sf::CircleShape ring(outerRadius);
            ring.setOrigin({outerRadius, outerRadius});
            ring.setPosition({col * SQUARE_SIZE + SQUARE_SIZE / 2.0f,
                                row * SQUARE_SIZE + SQUARE_SIZE / 2.0f});
            ring.setFillColor(sf::Color::Transparent);
            ring.setOutlineThickness(6.0f);
            ring.setOutlineColor(sf::Color(231, 76, 60, 180)); // Semi-transparent red (coral)
            window.draw(ring);
        } else {
            // Empty square: draw a standard small grey circle
            float radius = SQUARE_SIZE * 0.15f;
            sf::CircleShape circle(radius);
            circle.setOrigin({radius, radius});
            circle.setFillColor(sf::Color(0, 0, 0, 80));
            circle.setPosition({col * SQUARE_SIZE + SQUARE_SIZE / 2.0f,
                                row * SQUARE_SIZE + SQUARE_SIZE / 2.0f});
            window.draw(circle);
        }
    }
}

void Renderer::drawCheckHighlight(int square) {
    if (square < 0) return;

    int row = square / 8;
    int col = square % 8;

    sf::RectangleShape highlight({static_cast<float>(SQUARE_SIZE),
                                   static_cast<float>(SQUARE_SIZE)});
    highlight.setPosition({static_cast<float>(col * SQUARE_SIZE),
                           static_cast<float>(row * SQUARE_SIZE)});
    highlight.setFillColor(sf::Color(231, 76, 60, 140)); // Semi-transparent red (coral)

    window.draw(highlight);
}

void Renderer::drawPromotionMenu(PieceColor color, sf::Vector2i mousePos) {
    // 1. Draw a semi-transparent dark overlay over the entire board
    sf::RectangleShape overlay({800.0f, 800.0f});
    overlay.setFillColor(sf::Color(0, 0, 0, 150));
    window.draw(overlay);

    // 2. Draw the background panel for the promotion choice
    sf::RectangleShape panel({400.0f, 120.0f});
    panel.setPosition({200.0f, 340.0f});
    panel.setFillColor(sf::Color(240, 240, 240));
    panel.setOutlineThickness(4.0f);
    panel.setOutlineColor(sf::Color(100, 100, 100));
    window.draw(panel);

    // 3. Draw the 4 options: Queen, Rook, Bishop, Knight
    std::string pieceNames[] = { "q", "r", "b", "n" };
    float buttonX[] = { 216.0f, 312.0f, 408.0f, 504.0f };
    float buttonY = 360.0f;
    float buttonSize = 80.0f;

    for (int i = 0; i < 4; ++i) {
        sf::FloatRect bounds({buttonX[i], buttonY}, {buttonSize, buttonSize});
        bool isHovered = bounds.contains({static_cast<float>(mousePos.x), static_cast<float>(mousePos.y)});

        // Draw button background
        sf::RectangleShape btn({buttonSize, buttonSize});
        btn.setPosition({buttonX[i], buttonY});
        if (isHovered) {
            btn.setFillColor(sf::Color(220, 220, 220)); // darker highlight on hover
            btn.setOutlineThickness(3.0f);
            btn.setOutlineColor(sf::Color(41, 128, 185)); // Nice blue outline
        } else {
            btn.setFillColor(sf::Color(255, 255, 255));
            btn.setOutlineThickness(1.0f);
            btn.setOutlineColor(sf::Color(200, 200, 200));
        }
        window.draw(btn);

        // Draw the piece image inside the button
        std::string key = (color == PieceColor::White ? "w" : "b") + pieceNames[i];
        const sf::Texture& tex = textures.at(key);
        sf::Sprite sprite(tex);
        
        // Scale and center piece in button
        sf::Vector2u texSize = tex.getSize();
        float targetSize = buttonSize * 0.85f;
        float scaleX = targetSize / static_cast<float>(texSize.x);
        float scaleY = targetSize / static_cast<float>(texSize.y);
        sprite.setScale({scaleX, scaleY});

        float offset = (buttonSize - targetSize) / 2.0f;
        sprite.setPosition({buttonX[i] + offset, buttonY + offset});
        window.draw(sprite);
    }
}

void Renderer::drawStartMenu(sf::Vector2i mousePos) {
    // 1. Draw a semi-transparent dark overlay over the entire board
    sf::RectangleShape overlay({800.0f, 800.0f});
    overlay.setFillColor(sf::Color(0, 0, 0, 160));
    window.draw(overlay);

    // 2. Draw shadow rectangle
    sf::RectangleShape shadow({500.0f, 490.0f});
    shadow.setPosition({154.0f, 154.0f});
    shadow.setFillColor(sf::Color(0, 0, 0, 100));
    window.draw(shadow);

    // 3. Draw the background panel (deep slate blue/grey)
    sf::RectangleShape panel({500.0f, 490.0f});
    panel.setPosition({150.0f, 150.0f});
    panel.setFillColor(sf::Color(23, 27, 36, 245));
    panel.setOutlineThickness(3.0f);
    panel.setOutlineColor(sf::Color(0, 180, 216, 220)); // cyan border
    window.draw(panel);

    // 4. Draw Title and Subtitle if font is loaded
    if (hasFont) {
        sf::Text title(font, "CHESS ENGINE", 34);
        title.setStyle(sf::Text::Style::Bold);
        title.setFillColor(sf::Color(248, 249, 250));
        
        sf::FloatRect titleBounds = title.getLocalBounds();
        title.setOrigin(sf::Vector2f(titleBounds.position.x + titleBounds.size.x / 2.0f, titleBounds.position.y + titleBounds.size.y / 2.0f));
        title.setPosition({400.0f, 185.0f});
        window.draw(title);

        sf::Text subtitle(font, "Choose your opponent to begin", 15);
        subtitle.setFillColor(sf::Color(173, 181, 189));
        
        sf::FloatRect subBounds = subtitle.getLocalBounds();
        subtitle.setOrigin(sf::Vector2f(subBounds.position.x + subBounds.size.x / 2.0f, subBounds.position.y + subBounds.size.y / 2.0f));
        subtitle.setPosition({400.0f, 225.0f});
        window.draw(subtitle);
    }

    // 5. Draw divider line
    sf::RectangleShape divider({420.0f, 2.0f});
    divider.setPosition({190.0f, 245.0f});
    divider.setFillColor(sf::Color(73, 80, 87, 180));
    window.draw(divider);

    // 6. Draw 3 options: Human vs Human, Human vs AI, AI vs Human
    struct MenuOption {
        std::string text;
        std::string piece1;
        std::string piece2;
        float y;
    };

    std::vector<MenuOption> options = {
        {"Human vs Human", "wk", "bk", 270.0f},
        {"Human vs AI (Play as White)", "wk", "bn", 370.0f},
        {"AI vs Human (Play as Black)", "wn", "bk", 470.0f}
    };

    float buttonWidth = 420.0f;
    float buttonHeight = 75.0f;

    for (const auto& opt : options) {
        sf::FloatRect bounds({190.0f, opt.y}, {buttonWidth, buttonHeight});
        bool isHovered = bounds.contains({static_cast<float>(mousePos.x), static_cast<float>(mousePos.y)});

        // Draw button background
        sf::RectangleShape btn({buttonWidth, buttonHeight});
        btn.setPosition({190.0f, opt.y});
        if (isHovered) {
            btn.setFillColor(sf::Color(0, 119, 182, 230)); // Nice bright ocean blue
            btn.setOutlineThickness(2.5f);
            btn.setOutlineColor(sf::Color(255, 255, 255, 220));
        } else {
            btn.setFillColor(sf::Color(33, 37, 41, 220)); // Dark button
            btn.setOutlineThickness(1.5f);
            btn.setOutlineColor(sf::Color(108, 117, 125, 150));
        }
        window.draw(btn);

        // Draw pieces on the left side of the button
        float pieceSize = 50.0f;
        float pieceY = opt.y + (buttonHeight - pieceSize) / 2.0f;

        // Piece 1
        if (textures.find(opt.piece1) != textures.end()) {
            const sf::Texture& tex1 = textures.at(opt.piece1);
            sf::Sprite sprite1(tex1);
            sf::Vector2u texSize1 = tex1.getSize();
            float scale1 = pieceSize / static_cast<float>(std::max(texSize1.x, texSize1.y));
            sprite1.setScale({scale1, scale1});
            float pieceX1 = 190.0f + 20.0f;
            sprite1.setPosition({pieceX1, pieceY});
            window.draw(sprite1);
        }

        // Piece 2
        if (textures.find(opt.piece2) != textures.end()) {
            const sf::Texture& tex2 = textures.at(opt.piece2);
            sf::Sprite sprite2(tex2);
            sf::Vector2u texSize2 = tex2.getSize();
            float scale2 = pieceSize / static_cast<float>(std::max(texSize2.x, texSize2.y));
            sprite2.setScale({scale2, scale2});
            float pieceX2 = 190.0f + 65.0f;
            sprite2.setPosition({pieceX2, pieceY});
            window.draw(sprite2);
        }

        // Draw text
        if (hasFont) {
            sf::Text btnText(font, opt.text, 18);
            if (isHovered) {
                btnText.setFillColor(sf::Color::White);
                btnText.setStyle(sf::Text::Style::Bold);
            } else {
                btnText.setFillColor(sf::Color(222, 226, 230));
            }
            sf::FloatRect textBounds = btnText.getLocalBounds();
            // Center vertically, align left starting at x = 320.f
            btnText.setOrigin(sf::Vector2f(0.0f, textBounds.position.y + textBounds.size.y / 2.0f));
            btnText.setPosition({320.0f, opt.y + buttonHeight / 2.0f});
            window.draw(btnText);
        }
    }
}

void Renderer::drawLastMoveHighlight(const Move& lastMove) {
    if (lastMove.from < 0 || lastMove.from >= 64 || lastMove.to < 0 || lastMove.to >= 64) {
        return;
    }

    // A nice soft yellow-green color (similar to chess.com last move highlight)
    sf::Color highlightColor(186, 202, 68, 120);

    for (int square : {lastMove.from, lastMove.to}) {
        int row = square / 8;
        int col = square % 8;

        sf::RectangleShape highlight({static_cast<float>(SQUARE_SIZE),
                                       static_cast<float>(SQUARE_SIZE)});
        highlight.setPosition({static_cast<float>(col * SQUARE_SIZE),
                               static_cast<float>(row * SQUARE_SIZE)});
        highlight.setFillColor(highlightColor);

        window.draw(highlight);
    }
}

void Renderer::drawGameOverMenu(const std::string& status, sf::Vector2i mousePos) {
    // 1. Draw a semi-transparent dark overlay over the entire board
    sf::RectangleShape overlay({800.0f, 800.0f});
    overlay.setFillColor(sf::Color(0, 0, 0, 160));
    window.draw(overlay);

    // 2. Draw shadow rectangle
    sf::RectangleShape shadow({500.0f, 320.0f});
    shadow.setPosition({154.0f, 244.0f});
    shadow.setFillColor(sf::Color(0, 0, 0, 100));
    window.draw(shadow);

    // 3. Draw the background panel (deep slate/charcoal)
    sf::RectangleShape panel({500.0f, 320.0f});
    panel.setPosition({150.0f, 240.0f});
    panel.setFillColor(sf::Color(23, 27, 36, 245));
    panel.setOutlineThickness(3.0f);
    panel.setOutlineColor(sf::Color(231, 76, 60, 220)); // red/coral border for game over
    window.draw(panel);

    // 4. Draw Game Over title and status
    if (hasFont) {
        sf::Text title(font, "GAME OVER", 30);
        title.setStyle(sf::Text::Style::Bold);
        title.setFillColor(sf::Color(248, 249, 250));
        sf::FloatRect titleBounds = title.getLocalBounds();
        title.setOrigin(sf::Vector2f(titleBounds.position.x + titleBounds.size.x / 2.0f, titleBounds.position.y + titleBounds.size.y / 2.0f));
        title.setPosition({400.0f, 280.0f});
        window.draw(title);

        sf::Text statusText(font, status, 18);
        statusText.setFillColor(sf::Color(173, 181, 189));
        sf::FloatRect statusBounds = statusText.getLocalBounds();
        statusText.setOrigin(sf::Vector2f(statusBounds.position.x + statusBounds.size.x / 2.0f, statusBounds.position.y + statusBounds.size.y / 2.0f));
        statusText.setPosition({400.0f, 325.0f});
        window.draw(statusText);
    }

    // 5. Draw divider line
    sf::RectangleShape divider({420.0f, 2.0f});
    divider.setPosition({190.0f, 355.0f});
    divider.setFillColor(sf::Color(73, 80, 87, 180));
    window.draw(divider);

    // 6. Draw 2 buttons: "Play Again" and "Main Menu"
    struct MenuOption {
        std::string text;
        float y;
        sf::Color hoverColor;
    };

    std::vector<MenuOption> options = {
        {"Play Again (R)", 380.0f, sf::Color(46, 204, 113, 230)}, // Nice green
        {"Main Menu (M)", 460.0f, sf::Color(52, 152, 219, 230)}   // Nice blue
    };

    float buttonWidth = 320.0f;
    float buttonHeight = 55.0f;
    float buttonX = 240.0f;

    for (const auto& opt : options) {
        sf::FloatRect bounds({buttonX, opt.y}, {buttonWidth, buttonHeight});
        bool isHovered = bounds.contains({static_cast<float>(mousePos.x), static_cast<float>(mousePos.y)});

        sf::RectangleShape btn({buttonWidth, buttonHeight});
        btn.setPosition({buttonX, opt.y});
        if (isHovered) {
            btn.setFillColor(opt.hoverColor);
            btn.setOutlineThickness(2.0f);
            btn.setOutlineColor(sf::Color::White);
        } else {
            btn.setFillColor(sf::Color(33, 37, 41, 220));
            btn.setOutlineThickness(1.5f);
            btn.setOutlineColor(sf::Color(108, 117, 125, 150));
        }
        window.draw(btn);

        if (hasFont) {
            sf::Text btnText(font, opt.text, 16);
            if (isHovered) {
                btnText.setFillColor(sf::Color::White);
                btnText.setStyle(sf::Text::Style::Bold);
            } else {
                btnText.setFillColor(sf::Color(222, 226, 230));
            }
            sf::FloatRect textBounds = btnText.getLocalBounds();
            btnText.setOrigin(sf::Vector2f(textBounds.position.x + textBounds.size.x / 2.0f, textBounds.position.y + textBounds.size.y / 2.0f));
            btnText.setPosition({400.0f, opt.y + buttonHeight / 2.0f});
            window.draw(btnText);
        }
    }
}

void Renderer::render(const Board& board, int selectedSquare,
                      const std::vector<int>& legalMoveSquares,
                      int checkKingSquare,
                      bool isPromoting,
                      PieceColor promotingColor,
                      sf::Vector2i mousePos,
                      bool isShowingMenu,
                      Move lastMove,
                      bool isGameOver,
                      const std::string& gameStatus) {
    window.clear();
    drawBoard();
    drawLastMoveHighlight(lastMove);
    drawSelectedSquare(selectedSquare);
    if (checkKingSquare >= 0) {
        drawCheckHighlight(checkKingSquare);
    }
    drawPieces(board);
    drawHighlights(board, legalMoveSquares);
    if (isPromoting) {
        drawPromotionMenu(promotingColor, mousePos);
    }
    if (isGameOver) {
        drawGameOverMenu(gameStatus, mousePos);
    }
    if (isShowingMenu) {
        drawStartMenu(mousePos);
    }
    window.display();
}
