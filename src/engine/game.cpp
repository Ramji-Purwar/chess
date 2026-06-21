#include "game.h"
#include <iostream>

Game::Game()
    : window(sf::VideoMode({800, 800}), "Chess"),
      renderer(window),
      selectedSquare(-1),
      gameOver(false),
      isPromoting(false),
      pendingMoveFrom(-1),
      pendingMoveTo(-1),
      promotingColor(PieceColor::White),
      isShowingMenu(true),
      mode(GameMode::HumanVsHuman),
      aiMaxDepth(5),
      blackAI(new ai::AIEngine("b")),
      whiteAI(new ai::AIEngine("w")),
      lastMove(),
      halfmoveClock(0),
      aiSearchActive(false),
      aiSearchDone(false) {
    renderer.loadTextures();
    board.initialize();
    positionHistory.push_back(board.getPositionSignature());
    updateWindowTitle();
}

Game::~Game() {
    delete blackAI;
    delete whiteAI;
}

void Game::run() {
    while (window.isOpen()) {
        handleEvents();
        updateAI();
        render();
    }
}

void Game::handleEvents() {
    while (const auto event = window.pollEvent()) {
        if (event->is<sf::Event::Closed>()) {
            window.close();
            return;
        }

        // Mode selection shortcuts
        if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
            if (keyPressed->code == sf::Keyboard::Key::Num1) {
                mode = GameMode::HumanVsHuman;
                resetGame();
                isShowingMenu = false;
                updateWindowTitle();
                continue;
            } else if (keyPressed->code == sf::Keyboard::Key::Num2) {
                mode = GameMode::HumanVsAI;
                resetGame();
                isShowingMenu = false;
                updateWindowTitle();
                continue;
            } else if (keyPressed->code == sf::Keyboard::Key::Num3) {
                mode = GameMode::AIVsHuman;
                resetGame();
                isShowingMenu = false;
                updateWindowTitle();
                continue;
            }
        }

        // Start menu input interception
        if (isShowingMenu) {
            if (const auto* mousePressed =
                    event->getIf<sf::Event::MouseButtonPressed>()) {
                if (mousePressed->button == sf::Mouse::Button::Left) {
                    float px = static_cast<float>(mousePressed->position.x);
                    float py = static_cast<float>(mousePressed->position.y);

                    float btnWidth = 420.0f;
                    float btnHeight = 75.0f;
                    float btnX = 190.0f;

                    // Option 1: Human vs Human (Y: 270)
                    if (px >= btnX && px <= btnX + btnWidth) {
                        if (py >= 270.0f && py <= 270.0f + btnHeight) {
                            mode = GameMode::HumanVsHuman;
                            resetGame();
                            isShowingMenu = false;
                            updateWindowTitle();
                            continue;
                        }
                        // Option 2: Human vs AI (Y: 370)
                        else if (py >= 370.0f && py <= 370.0f + btnHeight) {
                            mode = GameMode::HumanVsAI;
                            resetGame();
                            isShowingMenu = false;
                            updateWindowTitle();
                            continue;
                        }
                        // Option 3: AI vs Human (Y: 470)
                        else if (py >= 470.0f && py <= 470.0f + btnHeight) {
                            mode = GameMode::AIVsHuman;
                            resetGame();
                            isShowingMenu = false;
                            updateWindowTitle();
                            continue;
                        }
                    }
                }
            }
            continue;
        }

        if (gameOver) {
            if (const auto* mousePressed =
                    event->getIf<sf::Event::MouseButtonPressed>()) {
                if (mousePressed->button == sf::Mouse::Button::Left) {
                    float px = static_cast<float>(mousePressed->position.x);
                    float py = static_cast<float>(mousePressed->position.y);

                    float btnWidth = 320.0f;
                    float btnHeight = 55.0f;
                    float btnX = 240.0f;

                    // Option 1: Play Again (Y: 380)
                    if (px >= btnX && px <= btnX + btnWidth) {
                        if (py >= 380.0f && py <= 380.0f + btnHeight) {
                            resetGame();
                            updateWindowTitle();
                            continue;
                        }
                        // Option 2: Main Menu (Y: 460)
                        else if (py >= 460.0f && py <= 460.0f + btnHeight) {
                            isShowingMenu = true;
                            resetGame();
                            updateWindowTitle();
                            continue;
                        }
                    }
                }
            }
            if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
                if (keyPressed->code == sf::Keyboard::Key::R) {
                    resetGame();
                    updateWindowTitle();
                    continue;
                } else if (keyPressed->code == sf::Keyboard::Key::M) {
                    isShowingMenu = true;
                    resetGame();
                    updateWindowTitle();
                    continue;
                }
            }
            continue;
        }

        // Block human interaction if it's the AI's turn
        bool isAITurn = (mode == GameMode::HumanVsAI && !board.isWhiteToMove()) ||
                        (mode == GameMode::AIVsHuman && board.isWhiteToMove());
        if (isAITurn) continue;

        if (const auto* mousePressed =
                event->getIf<sf::Event::MouseButtonPressed>()) {
            if (mousePressed->button == sf::Mouse::Button::Left) {
                if (isPromoting) {
                    float px = static_cast<float>(mousePressed->position.x);
                    float py = static_cast<float>(mousePressed->position.y);
                    float buttonX[] = { 216.0f, 312.0f, 408.0f, 504.0f };
                    float buttonY = 360.0f;
                    float buttonSize = 80.0f;

                    PieceType chosenType = PieceType::None;
                    if (py >= buttonY && py <= buttonY + buttonSize) {
                        if (px >= buttonX[0] && px <= buttonX[0] + buttonSize) {
                            chosenType = PieceType::Queen;
                        } else if (px >= buttonX[1] && px <= buttonX[1] + buttonSize) {
                            chosenType = PieceType::Rook;
                        } else if (px >= buttonX[2] && px <= buttonX[2] + buttonSize) {
                            chosenType = PieceType::Bishop;
                        } else if (px >= buttonX[3] && px <= buttonX[3] + buttonSize) {
                            chosenType = PieceType::Knight;
                        }
                    }

                    if (chosenType != PieceType::None) {
                        Move finalMove(pendingMoveFrom, pendingMoveTo, chosenType);
                        processMove(finalMove);
                        isPromoting = false;
                    }
                    continue;
                }

                if (selectedSquare >= 0) {
                    int clickedSquare = inputHandler.screenToSquare(mousePressed->position);
                    bool isPromotionMove = false;
                    for (const auto& move : currentLegalMoves) {
                        if (move.to == clickedSquare && move.promotion != PieceType::None) {
                            isPromotionMove = true;
                            break;
                        }
                    }

                    if (isPromotionMove) {
                        isPromoting = true;
                        pendingMoveFrom = selectedSquare;
                        pendingMoveTo = clickedSquare;
                        promotingColor = board.isWhiteToMove() ? PieceColor::White : PieceColor::Black;
                        selectedSquare = -1;
                        currentLegalMoves.clear();
                        continue;
                    }
                }

                Move resultMove;
                bool moveProduced = inputHandler.handleMouseClick(
                    mousePressed->position, board,
                    selectedSquare, currentLegalMoves,
                    resultMove, moveGenerator);

                if (moveProduced) {
                    processMove(resultMove);
                }
            }
        }
    }
}

void Game::processMove(const Move& move) {
    // Check if the move is a pawn move or capture to update the halfmove clock
    bool isPawnMove = false;
    const Piece* movingPiece = board.getPiece(move.from);
    if (movingPiece && movingPiece->getType() == PieceType::Pawn) {
        isPawnMove = true;
    }
    bool isCapture = (board.getPiece(move.to) != nullptr);
    if (movingPiece && movingPiece->getType() == PieceType::Pawn && move.to == board.getEnPassantTarget()) {
        isCapture = true;
    }

    board.makeMove(move);
    lastMove = move;

    // Update halfmove clock (resets on pawn move or capture)
    if (isPawnMove || isCapture) {
        halfmoveClock = 0;
    } else {
        halfmoveClock++;
    }

    // Record position in history
    positionHistory.push_back(board.getPositionSignature());

    selectedSquare = -1;
    currentLegalMoves.clear();
    checkGameState();
    updateWindowTitle();
}

void Game::checkGameState() {
    PieceColor currentColor =
        board.isWhiteToMove() ? PieceColor::White : PieceColor::Black;

    bool hasLegal = false;
    for (int sq = 0; sq < 64; sq++) {
        Piece* piece = board.getPiece(sq);
        if (piece && piece->getColor() == currentColor) {
            auto moves = moveGenerator.generateLegalMoves(board, sq);
            if (!moves.empty()) {
                hasLegal = true;
                break;
            }
        }
    }

    if (!hasLegal) {
        gameOver = true;
        if (moveGenerator.isInCheck(board, currentColor)) {
            std::string winner =
                (currentColor == PieceColor::White) ? "Black" : "White";
            gameStatus = winner + " wins by checkmate!";
        } else {
            gameStatus = "Stalemate! Game is a draw.";
        }
        std::cout << gameStatus << std::endl;
        return;
    }

    // Check 50-move rule (100 plies)
    if (halfmoveClock >= 100) {
        gameOver = true;
        gameStatus = "Draw by 50-move rule!";
        std::cout << gameStatus << std::endl;
        return;
    }

    // Check threefold repetition
    std::string currentPos = board.getPositionSignature();
    int occurrences = 0;
    for (const auto& pos : positionHistory) {
        if (pos == currentPos) {
            occurrences++;
        }
    }

    if (occurrences >= 3) {
        gameOver = true;
        gameStatus = "Draw by threefold repetition!";
        std::cout << gameStatus << std::endl;
        return;
    }
}

void Game::render() {
    std::vector<int> legalSquares;
    for (const auto& move : currentLegalMoves) {
        legalSquares.push_back(move.to);
    }

    PieceColor currentColor = board.isWhiteToMove() ? PieceColor::White : PieceColor::Black;
    int checkKingSquare = -1;
    if (moveGenerator.isInCheck(board, currentColor)) {
        checkKingSquare = board.findKing(currentColor);
    }

    sf::Vector2i mousePos = sf::Mouse::getPosition(window);
    renderer.render(board, selectedSquare, legalSquares, checkKingSquare, isPromoting, promotingColor, mousePos, isShowingMenu, lastMove, gameOver, gameStatus);
}

void Game::updateAI() {
    if (gameOver) return;
    if (isShowingMenu) return;

    bool isAITurn = (mode == GameMode::HumanVsAI && !board.isWhiteToMove()) ||
                    (mode == GameMode::AIVsHuman && board.isWhiteToMove());
    if (!isAITurn) return;

    // If the AI search has not started yet, kick it off
    if (!aiSearchActive && !aiSearchDone) {
        // Draw the latest human move first so screen is updated
        render();

        // AI thinking status in window title
        std::string thinkingTitle = "";
        if (mode == GameMode::HumanVsAI) {
            thinkingTitle = "Chess (Human vs AI) - AI is thinking...";
        } else {
            thinkingTitle = "Chess (AI vs Human) - AI is thinking...";
        }
        window.setTitle(thinkingTitle);

        aiSearchActive = true;
        aiSearchStartPosSignature = board.getPositionSignature();
        Board boardCopy = board;
        std::vector<std::string> historyCopy = positionHistory;

        std::thread([this, boardCopy, historyCopy]() {
            ai::AIMove best;
            if (mode == GameMode::HumanVsAI) {
                best = blackAI->get_best_move(boardCopy, aiMaxDepth, historyCopy);
            } else {
                best = whiteAI->get_best_move(boardCopy, aiMaxDepth, historyCopy);
            }
            aiBestMove = best;
            aiSearchDone = true;
            aiSearchActive = false;
        }).detach();
    }

    // Check if the AI search is complete
    if (aiSearchDone) {
        aiSearchDone = false; // Reset flag

        // Apply move ONLY if the board is still in the same state as when we started the search
        if (board.getPositionSignature() == aiSearchStartPosSignature) {
            ai::AIMove best = aiBestMove;

            // Convert AIMove to GUI Move
            if (best.start != -1 && best.end != -1) {
                int from = ai::mailboxSqToGui(best.start);
                int to = ai::mailboxSqToGui(best.end);
                
                PieceType promotion = PieceType::None;
                if (best.special[0] == 'P') {
                    switch (best.special[1]) {
                        case 'q': promotion = PieceType::Queen; break;
                        case 'r': promotion = PieceType::Rook; break;
                        case 'b': promotion = PieceType::Bishop; break;
                        case 'n': promotion = PieceType::Knight; break;
                    }
                }
                
                Move guiMove(from, to, promotion);
                processMove(guiMove);
            } else {
                // If AI could not produce a valid move (e.g. checkmate/stalemate but game wasn't marked over yet)
                checkGameState();
                updateWindowTitle();
            }
        }
    }
}

void Game::resetGame() {
    board.initialize();
    lastMove = Move();
    positionHistory.clear();
    positionHistory.push_back(board.getPositionSignature());
    halfmoveClock = 0;
    selectedSquare = -1;
    currentLegalMoves.clear();
    gameOver = false;
    gameStatus = "";
    isPromoting = false;
    aiSearchActive = false;
    aiSearchDone = false;
    std::cout << "Game reset. Mode: " 
              << (mode == GameMode::HumanVsHuman ? "Human vs Human" : 
                 (mode == GameMode::HumanVsAI ? "Human vs AI" : "AI vs Human")) 
              << std::endl;
}

void Game::updateWindowTitle() {
    std::string title = "";
    switch (mode) {
        case GameMode::HumanVsHuman: title = "Chess (Human vs Human)"; break;
        case GameMode::HumanVsAI:    title = "Chess (Human vs AI)"; break;
        case GameMode::AIVsHuman:    title = "Chess (AI vs Human)"; break;
    }

    if (gameOver) {
        title += " - " + gameStatus;
    } else {
        title += board.isWhiteToMove() ? " - White to Move" : " - Black to Move";
    }
    window.setTitle(title);
}