#ifndef GAME_H
#define GAME_H

#include <SFML/Graphics.hpp>
#include <vector>
#include <string>
#include <atomic>
#include <thread>
#include "board.h"
#include "move.h"
#include "move_generator.h"
#include "../gui/renderer.h"
#include "../gui/input_handler.h"
#include "ai/ai_engine.h"

class Game {
public:
    enum class GameMode {
        HumanVsHuman,
        HumanVsAI,  // Human is White, AI is Black
        AIVsHuman   // AI is White, Human is Black
    };

private:
    sf::RenderWindow window;
    Board board;
    Renderer renderer;
    InputHandler inputHandler;
    MoveGenerator moveGenerator;

    int selectedSquare;
    std::vector<Move> currentLegalMoves;
    bool gameOver;
    std::string gameStatus;

    // Promotion state variables
    bool isPromoting;
    int pendingMoveFrom;
    int pendingMoveTo;
    PieceColor promotingColor;

    // Menu state
    bool isShowingMenu;

    // Last move tracking
    Move lastMove;

    // Draw by repetition and 50-move rule tracking
    std::vector<std::string> positionHistory;
    int halfmoveClock;

    // AI Integration fields
    GameMode mode;
    int aiMaxDepth;
    ai::AIEngine* blackAI;
    ai::AIEngine* whiteAI;

    // AI thread synchronization
    std::atomic<bool> aiSearchActive;
    std::atomic<bool> aiSearchDone;
    ai::AIMove aiBestMove;
    std::string aiSearchStartPosSignature;

public:
    Game();
    ~Game();

    void run();

private:
    void handleEvents();
    void render();
    void processMove(const Move& move);
    void checkGameState();
    void updateAI();
    void resetGame();
    void updateWindowTitle();
};

#endif

