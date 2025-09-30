"""
Enhanced Chess Position Evaluation Function with Advanced Pattern Recognition
Based on traditional hand-crafted evaluation principles with sophisticated tactical and strategic patterns
"""

# Piece-Square Tables for different game phases (positional bonuses in centipawns)

# PAWN TABLES
PST_PAWN_OPENING = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

PST_PAWN_MIDDLEGAME = [
     0,  0,  0,  0,  0,  0,  0,  0,
    80, 80, 80, 80, 80, 80, 80, 80,
    25, 25, 30, 40, 40, 30, 25, 25,
    15, 15, 20, 35, 35, 20, 15, 15,
     5,  5, 10, 30, 30, 10,  5,  5,
     5, -5,-10,  5,  5,-10, -5,  5,
     5, 10, 10,-15,-15, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

PST_PAWN_ENDGAME = [
     0,  0,  0,  0,  0,  0,  0,  0,
   120,120,120,120,120,120,120,120,
    60, 60, 60, 60, 60, 60, 60, 60,
    40, 40, 40, 40, 40, 40, 40, 40,
    20, 20, 20, 20, 20, 20, 20, 20,
    10, 10, 10, 10, 10, 10, 10, 10,
     5,  5,  5,  5,  5,  5,  5,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

# KNIGHT TABLES
PST_KNIGHT_OPENING = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

PST_KNIGHT_MIDDLEGAME = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -30,  0, 15, 25, 25, 15,  0,-30,
    -30,  5, 25, 35, 35, 25,  5,-30,
    -30,  0, 25, 35, 35, 25,  0,-30,
    -30,  5, 15, 25, 25, 15,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

PST_KNIGHT_ENDGAME = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20, -5, -5, -5, -5,-20,-40,
    -30, -5, 10, 15, 15, 10, -5,-30,
    -30, -5, 15, 20, 20, 15, -5,-30,
    -30, -5, 15, 20, 20, 15, -5,-30,
    -30, -5, 10, 15, 15, 10, -5,-30,
    -40,-20, -5, -5, -5, -5,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

# BISHOP TABLES
PST_BISHOP_OPENING = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

PST_BISHOP_MIDDLEGAME = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 15, 15, 10, 10,-10,
    -10,  0, 15, 20, 20, 15,  0,-10,
    -10,  5, 10, 20, 20, 10,  5,-10,
    -10,  0, 10, 15, 15, 10,  0,-10,
    -10,  5,  5,  5,  5,  5,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

PST_BISHOP_ENDGAME = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0, -5, -5, -5, -5,  0,-10,
    -10, -5,  5, 10, 10,  5, -5,-10,
    -10, -5, 10, 15, 15, 10, -5,-10,
    -10, -5, 10, 15, 15, 10, -5,-10,
    -10, -5,  5, 10, 10,  5, -5,-10,
    -10,  0, -5, -5, -5, -5,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

# ROOK TABLES
PST_ROOK_OPENING = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

PST_ROOK_MIDDLEGAME = [
     0,  0,  0,  5,  5,  0,  0,  0,
    15, 20, 20, 20, 20, 20, 20, 15,
     0,  5,  5,  5,  5,  5,  5,  0,
     0,  5,  5,  5,  5,  5,  5,  0,
     0,  5,  5,  5,  5,  5,  5,  0,
     0,  5,  5,  5,  5,  5,  5,  0,
     0,  5,  5,  5,  5,  5,  5,  0,
     5,  5,  5, 10, 10,  5,  5,  5
]

PST_ROOK_ENDGAME = [
    10, 10, 10, 10, 10, 10, 10, 10,
    10, 15, 15, 15, 15, 15, 15, 10,
     5, 10, 10, 10, 10, 10, 10,  5,
     5, 10, 10, 10, 10, 10, 10,  5,
     5, 10, 10, 10, 10, 10, 10,  5,
     5, 10, 10, 10, 10, 10, 10,  5,
     5, 10, 10, 10, 10, 10, 10,  5,
    10, 10, 10, 15, 15, 10, 10, 10
]

# QUEEN TABLES
PST_QUEEN_OPENING = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

PST_QUEEN_MIDDLEGAME = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5, 10, 10, 10, 10,  0,-10,
      0,  0, 10, 15, 15, 10,  0,  0,
     -5,  5, 10, 15, 15, 10,  0, -5,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

PST_QUEEN_ENDGAME = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  5, 15, 20, 20, 15,  5,-10,
     -5,  5, 20, 25, 25, 20,  5, -5,
     -5,  5, 20, 25, 25, 20,  5, -5,
    -10,  5, 15, 20, 20, 15,  5,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

# KING TABLES
PST_KING_OPENING = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

PST_KING_MIDDLEGAME = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     25, 25,  5,  5,  5,  5, 25, 25,
     25, 35, 15,  5,  5, 15, 35, 25
]

PST_KING_ENDGAME = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]


def get_game_phase(board_string):
    """
    Get numeric game phase (0.0 = opening, 1.0 = endgame)
    
    Args:
        board_string: 64-character string representing the board
    
    Returns:
        Float between 0.0 and 1.0 representing game phase
    """
    # Starting material value (without kings)
    starting_material = 2 * (8*100 + 2*320 + 2*330 + 2*500 + 900)  # 7800
    
    current_material = 0
    PIECE_VALUES = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900,
                    'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900}
    
    for piece in board_string:
        if piece in PIECE_VALUES:
            current_material += PIECE_VALUES[piece]
    
    # Phase ranges from 0.0 (opening) to 1.0 (endgame)
    phase = 1.0 - (current_material / starting_material)
    return max(0.0, min(1.0, phase))


def evaluate_advanced_patterns(board, white_pieces, black_pieces, white_pawns, black_pawns, 
                              white_bishops, black_bishops, white_knights, black_knights,
                              white_rooks, black_rooks, white_queen_pos, black_queen_pos,
                              white_king_pos, black_king_pos, game_phase):
    """
    Evaluate advanced chess patterns and return score
    
    Args:
        board: 8x8 board array
        Various piece position lists
        game_phase: Current game phase (0.0 = opening, 1.0 = endgame)
    
    Returns:
        Pattern evaluation score (positive favors white)
    """
    pattern_score = 0
    
    # Helper function to check if square is attacked
    def is_attacked_by(rank, file, color):
        """Check if square is attacked by given color"""
        # Simplified - in real implementation would check all piece attacks
        if color == 'white':
            # Check pawn attacks
            if rank < 7:
                if file > 0 and board[rank+1][file-1] == 'P':
                    return True
                if file < 7 and board[rank+1][file+1] == 'P':
                    return True
        else:
            if rank > 0:
                if file > 0 and board[rank-1][file-1] == 'p':
                    return True
                if file < 7 and board[rank-1][file+1] == 'p':
                    return True
        return False
    
    # ========== PIECE COORDINATION PATTERNS ==========
    
    # 1. BATTERY PATTERNS (Queen/Rook alignment)
    # Queen-Rook battery on file
    if white_queen_pos and white_rooks:
        qr, qf = white_queen_pos
        for rr, rf in white_rooks:
            if qf == rf:  # Same file
                pattern_score += 15
                # Extra bonus if pointing at weak pawn
                for r in range(min(qr, rr)):
                    if board[r][qf] == 'p':
                        pattern_score += 10
                        break
            elif qr == rr:  # Same rank
                pattern_score += 12
    
    if black_queen_pos and black_rooks:
        qr, qf = black_queen_pos
        for rr, rf in black_rooks:
            if qf == rf:
                pattern_score -= 15
                for r in range(max(qr, rr) + 1, 8):
                    if board[r][qf] == 'P':
                        pattern_score -= 10
                        break
            elif qr == rr:
                pattern_score -= 12
    
    # 2. ENHANCED BISHOP PATTERNS
    # Bishop pair bonus (enhanced)
    if len(white_bishops) >= 2:
        pattern_score += 35
        # Extra bonus if bishops on opposite colors
        if len(white_bishops) == 2:
            b1r, b1f = white_bishops[0]
            b2r, b2f = white_bishops[1]
            if (b1r + b1f) % 2 != (b2r + b2f) % 2:
                pattern_score += 15  # Opposite colored bishops
    
    if len(black_bishops) >= 2:
        pattern_score -= 35
        if len(black_bishops) == 2:
            b1r, b1f = black_bishops[0]
            b2r, b2f = black_bishops[1]
            if (b1r + b1f) % 2 != (b2r + b2f) % 2:
                pattern_score -= 15
    
    # Bad bishop (bishop blocked by own pawns)
    for br, bf in white_bishops:
        bishop_color = (br + bf) % 2  # 0 for dark, 1 for light
        blocked_count = 0
        for pr, pf in white_pawns:
            if (pr + pf) % 2 == bishop_color:
                blocked_count += 1
        if blocked_count >= 5:
            pattern_score -= 25  # Bad bishop
        elif blocked_count >= 3:
            pattern_score -= 10
    
    for br, bf in black_bishops:
        bishop_color = (br + bf) % 2
        blocked_count = 0
        for pr, pf in black_pawns:
            if (pr + pf) % 2 == bishop_color:
                blocked_count += 1
        if blocked_count >= 5:
            pattern_score += 25
        elif blocked_count >= 3:
            pattern_score += 10
    
    # 3. ENHANCED KNIGHT PATTERNS
    # Knight fork potential (attacking multiple pieces)
    knight_moves = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
    
    for nr, nf in white_knights:
        targets = 0
        high_value_targets = 0
        for dr, df in knight_moves:
            new_r, new_f = nr + dr, nf + df
            if 0 <= new_r < 8 and 0 <= new_f < 8:
                target = board[new_r][new_f]
                if target and target.islower():
                    targets += 1
                    if target in 'rq':
                        high_value_targets += 1
        
        if targets >= 2:
            pattern_score += 5
            if high_value_targets >= 1:
                pattern_score += 10
    
    for nr, nf in black_knights:
        targets = 0
        high_value_targets = 0
        for dr, df in knight_moves:
            new_r, new_f = nr + dr, nf + df
            if 0 <= new_r < 8 and 0 <= new_f < 8:
                target = board[new_r][new_f]
                if target and target.isupper():
                    targets += 1
                    if target in 'RQ':
                        high_value_targets += 1
        
        if targets >= 2:
            pattern_score -= 5
            if high_value_targets >= 1:
                pattern_score -= 10
    
    # 4. ENHANCED ROOK PATTERNS
    # Doubled rooks (on same file)
    if len(white_rooks) >= 2:
        for i, (r1r, r1f) in enumerate(white_rooks):
            for r2r, r2f in white_rooks[i+1:]:
                if r1f == r2f:
                    pattern_score += 20
                    # Even better if on open file
                    if not any(pf == r1f for pr, pf in white_pawns):
                        pattern_score += 15
    
    if len(black_rooks) >= 2:
        for i, (r1r, r1f) in enumerate(black_rooks):
            for r2r, r2f in black_rooks[i+1:]:
                if r1f == r2f:
                    pattern_score -= 20
                    if not any(pf == r1f for pr, pf in black_pawns):
                        pattern_score -= 15
    
    # Rook behind passed pawn
    for pr, pf in white_pawns:
        # Check if pawn is passed
        is_passed = True
        for r in range(pr - 1, -1, -1):
            for f in [pf-1, pf, pf+1]:
                if 0 <= f < 8 and board[r][f] == 'p':
                    is_passed = False
                    break
        
        if is_passed:
            # Check for rook behind
            for r in range(pr + 1, 8):
                if board[r][pf] == 'R':
                    pattern_score += 20
                    break
                elif board[r][pf] and board[r][pf] != '.':
                    break
    
    for pr, pf in black_pawns:
        is_passed = True
        for r in range(pr + 1, 8):
            for f in [pf-1, pf, pf+1]:
                if 0 <= f < 8 and board[r][f] == 'P':
                    is_passed = False
                    break
        
        if is_passed:
            for r in range(pr - 1, -1, -1):
                if board[r][pf] == 'r':
                    pattern_score -= 20
                    break
                elif board[r][pf] and board[r][pf] != '.':
                    break
    
    # 5. PAWN MAJORITY PATTERNS
    white_queenside_pawns = sum(1 for r, f in white_pawns if f <= 3)
    white_kingside_pawns = sum(1 for r, f in white_pawns if f >= 4)
    black_queenside_pawns = sum(1 for r, f in black_pawns if f <= 3)
    black_kingside_pawns = sum(1 for r, f in black_pawns if f >= 4)
    
    # Queenside majority valuable in endgame
    if game_phase > 0.6:
        if white_queenside_pawns > black_queenside_pawns:
            pattern_score += 15
        elif black_queenside_pawns > white_queenside_pawns:
            pattern_score -= 15
    
    # 6. KING ACTIVITY (in endgame)
    if game_phase > 0.7:  # Endgame
        # Centralized king is good
        if white_king_pos:
            kr, kf = white_king_pos
            if 2 <= kr <= 5 and 2 <= kf <= 5:
                pattern_score += 20
            # King supporting passed pawns
            for pr, pf in white_pawns:
                if abs(kr - pr) <= 1 and abs(kf - pf) <= 1:
                    pattern_score += 5
        
        if black_king_pos:
            kr, kf = black_king_pos
            if 2 <= kr <= 5 and 2 <= kf <= 5:
                pattern_score -= 20
            for pr, pf in black_pawns:
                if abs(kr - pr) <= 1 and abs(kf - pf) <= 1:
                    pattern_score -= 5
    
    # 7. TACTICAL PATTERNS - PIN DETECTION
    # Check for pieces pinned to king
    if white_king_pos:
        kr, kf = white_king_pos
        # Check diagonals for bishop/queen pins
        for dr, df in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            for i in range(1, 8):
                r, f = kr + dr*i, kf + df*i
                if not (0 <= r < 8 and 0 <= f < 8):
                    break
                if board[r][f]:
                    if board[r][f].isupper():
                        # Found own piece, check if pinned
                        for j in range(i+1, 8):
                            r2, f2 = kr + dr*j, kf + df*j
                            if not (0 <= r2 < 8 and 0 <= f2 < 8):
                                break
                            if board[r2][f2]:
                                if board[r2][f2] in 'bq':
                                    # Piece is pinned
                                    pattern_score -= 15
                                break
                    break
    
    # Similar for black king
    if black_king_pos:
        kr, kf = black_king_pos
        for dr, df in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            for i in range(1, 8):
                r, f = kr + dr*i, kf + df*i
                if not (0 <= r < 8 and 0 <= f < 8):
                    break
                if board[r][f]:
                    if board[r][f].islower():
                        for j in range(i+1, 8):
                            r2, f2 = kr + dr*j, kf + df*j
                            if not (0 <= r2 < 8 and 0 <= f2 < 8):
                                break
                            if board[r2][f2]:
                                if board[r2][f2] in 'BQ':
                                    pattern_score += 15
                                break
                    break
    
    # 8. WEAK SQUARES (holes in pawn structure)
    for rank in range(2, 6):  # Middle of board
        for file in range(8):
            # Check if square is a hole for white
            is_hole = True
            if file > 0 and any(r > rank and f == file-1 for r, f in white_pawns):
                is_hole = False
            if file < 7 and any(r > rank and f == file+1 for r, f in white_pawns):
                is_hole = False
            
            if is_hole and rank <= 3:  # Hole in white's position
                pattern_score -= 5
                # Worse if occupied by enemy piece
                if board[rank][file] and board[rank][file].islower():
                    pattern_score -= 10
            
            # Same for black
            is_hole = True
            if file > 0 and any(r < rank and f == file-1 for r, f in black_pawns):
                is_hole = False
            if file < 7 and any(r < rank and f == file+1 for r, f in black_pawns):
                is_hole = False
            
            if is_hole and rank >= 4:
                pattern_score += 5
                if board[rank][file] and board[rank][file].isupper():
                    pattern_score += 10
    
    # 9. FIANCHETTOED BISHOP
    # Bishop on long diagonal with pawn shield
    if (1, 1) in white_bishops:  # b7
        if board[2][0] == 'P' and board[2][1] == 'P' and board[2][2] == 'P':
            pattern_score += 10
    if (1, 6) in white_bishops:  # g7
        if board[2][5] == 'P' and board[2][6] == 'P' and board[2][7] == 'P':
            pattern_score += 10
    
    if (6, 1) in black_bishops:  # b2
        if board[5][0] == 'p' and board[5][1] == 'p' and board[5][2] == 'p':
            pattern_score -= 10
    if (6, 6) in black_bishops:  # g2
        if board[5][5] == 'p' and board[5][6] == 'p' and board[5][7] == 'p':
            pattern_score -= 10
    
    # 10. CONNECTED ROOKS
    # Rooks defending each other
    if len(white_rooks) == 2:
        r1r, r1f = white_rooks[0]
        r2r, r2f = white_rooks[1]
        if r1r == r2r or r1f == r2f:  # On same rank or file
            # Check if clear path between them
            clear_path = True
            if r1r == r2r:
                for f in range(min(r1f, r2f) + 1, max(r1f, r2f)):
                    if board[r1r][f]:
                        clear_path = False
                        break
            else:
                for r in range(min(r1r, r2r) + 1, max(r1r, r2r)):
                    if board[r][r1f]:
                        clear_path = False
                        break
            
            if clear_path:
                pattern_score += 8
    
    # Same for black
    if len(black_rooks) == 2:
        r1r, r1f = black_rooks[0]
        r2r, r2f = black_rooks[1]
        if r1r == r2r or r1f == r2f:
            clear_path = True
            if r1r == r2r:
                for f in range(min(r1f, r2f) + 1, max(r1f, r2f)):
                    if board[r1r][f]:
                        clear_path = False
                        break
            else:
                for r in range(min(r1r, r2r) + 1, max(r1r, r2r)):
                    if board[r][r1f]:
                        clear_path = False
                        break
            
            if clear_path:
                pattern_score -= 8
    
    return pattern_score


def evaluate_position(board_string, white_turn):
    """
    Evaluate a chess position from the perspective of the side to move.
    
    Args:
        board_string: 64-character string representing the board (a8-h1)
        white_turn: Boolean indicating if it's white's turn
    
    Returns:
        Integer evaluation score (positive favors side to move)
    """
    
    # Piece values (centipawns - 1 pawn = 100)
    PIECE_VALUES = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
        'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
    }
    
    # Determine game phase
    game_phase = get_game_phase(board_string)
    
    # Helper function to get interpolated piece-square table value
    def get_pst_value(piece, square_index, game_phase):
        """Get piece-square table value interpolated by game phase"""
        if piece == 'P':
            opening_val = PST_PAWN_OPENING[square_index]
            middle_val = PST_PAWN_MIDDLEGAME[square_index]
            endgame_val = PST_PAWN_ENDGAME[square_index]
        elif piece == 'p':
            opening_val = -PST_PAWN_OPENING[63 - square_index]
            middle_val = -PST_PAWN_MIDDLEGAME[63 - square_index]
            endgame_val = -PST_PAWN_ENDGAME[63 - square_index]
        elif piece == 'N':
            opening_val = PST_KNIGHT_OPENING[square_index]
            middle_val = PST_KNIGHT_MIDDLEGAME[square_index]
            endgame_val = PST_KNIGHT_ENDGAME[square_index]
        elif piece == 'n':
            opening_val = -PST_KNIGHT_OPENING[63 - square_index]
            middle_val = -PST_KNIGHT_MIDDLEGAME[63 - square_index]
            endgame_val = -PST_KNIGHT_ENDGAME[63 - square_index]
        elif piece == 'B':
            opening_val = PST_BISHOP_OPENING[square_index]
            middle_val = PST_BISHOP_MIDDLEGAME[square_index]
            endgame_val = PST_BISHOP_ENDGAME[square_index]
        elif piece == 'b':
            opening_val = -PST_BISHOP_OPENING[63 - square_index]
            middle_val = -PST_BISHOP_MIDDLEGAME[63 - square_index]
            endgame_val = -PST_BISHOP_ENDGAME[63 - square_index]
        elif piece == 'R':
            opening_val = PST_ROOK_OPENING[square_index]
            middle_val = PST_ROOK_MIDDLEGAME[square_index]
            endgame_val = PST_ROOK_ENDGAME[square_index]
        elif piece == 'r':
            opening_val = -PST_ROOK_OPENING[63 - square_index]
            middle_val = -PST_ROOK_MIDDLEGAME[63 - square_index]
            endgame_val = -PST_ROOK_ENDGAME[63 - square_index]
        elif piece == 'Q':
            opening_val = PST_QUEEN_OPENING[square_index]
            middle_val = PST_QUEEN_MIDDLEGAME[square_index]
            endgame_val = PST_QUEEN_ENDGAME[square_index]
        elif piece == 'q':
            opening_val = -PST_QUEEN_OPENING[63 - square_index]
            middle_val = -PST_QUEEN_MIDDLEGAME[63 - square_index]
            endgame_val = -PST_QUEEN_ENDGAME[63 - square_index]
        elif piece == 'K':
            opening_val = PST_KING_OPENING[square_index]
            middle_val = PST_KING_MIDDLEGAME[square_index]
            endgame_val = PST_KING_ENDGAME[square_index]
        elif piece == 'k':
            opening_val = -PST_KING_OPENING[63 - square_index]
            middle_val = -PST_KING_MIDDLEGAME[63 - square_index]
            endgame_val = -PST_KING_ENDGAME[63 - square_index]
        else:
            return 0
        
        # Interpolate between phases
        if game_phase < 0.5:  # Opening to middlegame transition
            phase_factor = game_phase * 2  # 0.0 to 1.0
            return opening_val + (middle_val - opening_val) * phase_factor
        else:  # Middlegame to endgame transition
            phase_factor = (game_phase - 0.5) * 2  # 0.0 to 1.0
            return middle_val + (endgame_val - middle_val) * phase_factor
    
    # Convert board string to 2D array
    board = []
    for i in range(8):
        row = []
        for j in range(8):
            piece = board_string[i * 8 + j]
            if piece == '.':
                piece = None
            row.append(piece)
        board.append(row)
    
    # Helper functions
    def is_valid(r, f):
        return 0 <= r < 8 and 0 <= f < 8
    
    def get_piece_moves(piece, rank, file):
        """Get pseudo-legal moves for mobility calculation"""
        moves = []
        
        if piece in 'Pp':
            # Pawns - simplified mobility
            if piece == 'P':
                if rank > 0:
                    if board[rank-1][file] is None:
                        moves.append((rank-1, file))
                    # Captures
                    if file > 0 and board[rank-1][file-1] and board[rank-1][file-1].islower():
                        moves.append((rank-1, file-1))
                    if file < 7 and board[rank-1][file+1] and board[rank-1][file+1].islower():
                        moves.append((rank-1, file+1))
            else:  # black pawn
                if rank < 7:
                    if board[rank+1][file] is None:
                        moves.append((rank+1, file))
                    # Captures
                    if file > 0 and board[rank+1][file-1] and board[rank+1][file-1].isupper():
                        moves.append((rank+1, file-1))
                    if file < 7 and board[rank+1][file+1] and board[rank+1][file+1].isupper():
                        moves.append((rank+1, file+1))
        
        elif piece in 'Nn':
            # Knight moves
            knight_moves = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
            for dr, df in knight_moves:
                new_r, new_f = rank + dr, file + df
                if is_valid(new_r, new_f):
                    target = board[new_r][new_f]
                    if target is None or (piece.isupper() != target.isupper()):
                        moves.append((new_r, new_f))
        
        elif piece in 'Bb':
            # Bishop moves
            for dr, df in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                for i in range(1, 8):
                    new_r, new_f = rank + dr*i, file + df*i
                    if not is_valid(new_r, new_f):
                        break
                    target = board[new_r][new_f]
                    if target is None:
                        moves.append((new_r, new_f))
                    else:
                        if piece.isupper() != target.isupper():
                            moves.append((new_r, new_f))
                        break
        
        elif piece in 'Rr':
            # Rook moves
            for dr, df in [(0,1), (0,-1), (1,0), (-1,0)]:
                for i in range(1, 8):
                    new_r, new_f = rank + dr*i, file + df*i
                    if not is_valid(new_r, new_f):
                        break
                    target = board[new_r][new_f]
                    if target is None:
                        moves.append((new_r, new_f))
                    else:
                        if piece.isupper() != target.isupper():
                            moves.append((new_r, new_f))
                        break
        
        elif piece in 'Qq':
            # Queen moves (combination of rook and bishop)
            for dr, df in [(0,1), (0,-1), (1,0), (-1,0), (-1,-1), (-1,1), (1,-1), (1,1)]:
                for i in range(1, 8):
                    new_r, new_f = rank + dr*i, file + df*i
                    if not is_valid(new_r, new_f):
                        break
                    target = board[new_r][new_f]
                    if target is None:
                        moves.append((new_r, new_f))
                    else:
                        if piece.isupper() != target.isupper():
                            moves.append((new_r, new_f))
                        break
        
        elif piece in 'Kk':
            # King moves
            for dr in [-1, 0, 1]:
                for df in [-1, 0, 1]:
                    if dr == 0 and df == 0:
                        continue
                    new_r, new_f = rank + dr, file + df
                    if is_valid(new_r, new_f):
                        target = board[new_r][new_f]
                        if target is None or (piece.isupper() != target.isupper()):
                            moves.append((new_r, new_f))
        
        return moves
    
    # Initialize evaluation components
    material_score = 0
    position_score = 0
    pawn_structure_score = 0
    mobility_score = 0
    center_control_score = 0
    king_safety_score = 0
    space_score = 0
    tempo_score = 0
    trapped_pieces_penalty = 0
    pattern_score = 0
    
    # Count pieces for game phase
    total_pieces = 0
    queen_count = 0
    rook_count = 0
    minor_count = 0
    
    for piece in board_string:
        if piece in 'QRBNqrbn':
            total_pieces += 1
            if piece in 'Qq':
                queen_count += 1
            elif piece in 'Rr':
                rook_count += 1
            elif piece in 'BNbn':
                minor_count += 1
    
    # Game phase (0 = opening/middlegame, 1 = endgame)
    is_endgame = (queen_count == 0) or (total_pieces <= 10)
    
    # Piece lists for analysis (enhanced collection)
    white_pieces = []
    black_pieces = []
    white_pawns = []
    black_pawns = []
    white_bishops = []
    black_bishops = []
    white_knights = []
    black_knights = []
    white_rooks = []
    black_rooks = []
    white_king_pos = None
    black_king_pos = None
    white_queen_pos = None
    black_queen_pos = None
    
    # First pass: collect pieces and basic material
    for rank in range(8):
        for file in range(8):
            piece = board[rank][file]
            if piece is None:
                continue
            
            square_index = rank * 8 + file
            
            # Material
            material_score += PIECE_VALUES.get(piece, 0)
            
            # Collect piece positions (enhanced)
            if piece.isupper():
                white_pieces.append((piece, rank, file))
                if piece == 'P':
                    white_pawns.append((rank, file))
                elif piece == 'N':
                    white_knights.append((rank, file))
                elif piece == 'B':
                    white_bishops.append((rank, file))
                elif piece == 'R':
                    white_rooks.append((rank, file))
                elif piece == 'Q':
                    white_queen_pos = (rank, file)
                elif piece == 'K':
                    white_king_pos = (rank, file)
            else:
                black_pieces.append((piece, rank, file))
                if piece == 'p':
                    black_pawns.append((rank, file))
                elif piece == 'n':
                    black_knights.append((rank, file))
                elif piece == 'b':
                    black_bishops.append((rank, file))
                elif piece == 'r':
                    black_rooks.append((rank, file))
                elif piece == 'q':
                    black_queen_pos = (rank, file)
                elif piece == 'k':
                    black_king_pos = (rank, file)
            
            # Piece-square tables (phase-dependent)
            position_score += get_pst_value(piece, square_index, game_phase)
    
    # MOBILITY EVALUATION
    white_mobility = 0
    black_mobility = 0
    
    for piece, rank, file in white_pieces:
        moves = get_piece_moves(piece, rank, file)
        # Weight mobility by piece type
        if piece == 'N':
            white_mobility += len(moves) * 4
        elif piece == 'B':
            white_mobility += len(moves) * 3
        elif piece == 'R':
            white_mobility += len(moves) * 2
        elif piece == 'Q':
            white_mobility += len(moves) * 1
    
    for piece, rank, file in black_pieces:
        moves = get_piece_moves(piece, rank, file)
        if piece == 'n':
            black_mobility += len(moves) * 4
        elif piece == 'b':
            black_mobility += len(moves) * 3
        elif piece == 'r':
            black_mobility += len(moves) * 2
        elif piece == 'q':
            black_mobility += len(moves) * 1
    
    mobility_score = white_mobility - black_mobility
    
    # SPACE EVALUATION (control of squares in enemy territory)
    white_space = 0
    black_space = 0
    
    # Count attacked squares in opponent's half
    for piece, rank, file in white_pieces:
        moves = get_piece_moves(piece, rank, file)
        for mr, mf in moves:
            if mr < 4:  # Upper half (black's territory)
                white_space += 1
    
    for piece, rank, file in black_pieces:
        moves = get_piece_moves(piece, rank, file)
        for mr, mf in moves:
            if mr >= 4:  # Lower half (white's territory)
                black_space += 1
    
    space_score = (white_space - black_space) * 2
    
    # ADVANCED PAWN STRUCTURE
    for rank, file in white_pawns:
        # Doubled pawns
        doubled = sum(1 for r, f in white_pawns if f == file and r != rank)
        if doubled > 0:
            pawn_structure_score -= 15 * doubled
        
        # Isolated pawns
        isolated = True
        for f in [file - 1, file + 1]:
            if 0 <= f <= 7:
                if any(f2 == f for r, f2 in white_pawns):
                    isolated = False
                    break
        if isolated:
            pawn_structure_score -= 25
        
        # Passed pawns
        passed = True
        for r in range(rank - 1, -1, -1):
            for f in [file - 1, file, file + 1]:
                if 0 <= f <= 7 and board[r][f] == 'p':
                    passed = False
                    break
        if passed:
            # More valuable in endgame and closer to promotion
            bonus = 20 + (7 - rank) * 15
            if is_endgame:
                bonus *= 2
            pawn_structure_score += bonus
        
        # Backward pawns
        if rank < 6:  # Not on 2nd or 7th rank
            backward = True
            # Check if pawn can advance
            if board[rank-1][file] is None:
                # Check if adjacent pawns are more advanced
                for f in [file - 1, file + 1]:
                    if 0 <= f <= 7:
                        for r, f2 in white_pawns:
                            if f2 == f and r <= rank:
                                backward = False
                                break
            else:
                backward = False
            
            if backward:
                pawn_structure_score -= 15
        
        # Pawn chains (connected pawns)
        connected = False
        for f in [file - 1, file + 1]:
            if 0 <= f <= 7:
                if board[rank][f] == 'P' or (rank < 7 and board[rank+1][f] == 'P'):
                    connected = True
                    break
        if connected:
            pawn_structure_score += 5
    
    # Same for black pawns
    for rank, file in black_pawns:
        doubled = sum(1 for r, f in black_pawns if f == file and r != rank)
        if doubled > 0:
            pawn_structure_score += 15 * doubled
        
        isolated = True
        for f in [file - 1, file + 1]:
            if 0 <= f <= 7:
                if any(f2 == f for r, f2 in black_pawns):
                    isolated = False
                    break
        if isolated:
            pawn_structure_score += 25
        
        passed = True
        for r in range(rank + 1, 8):
            for f in [file - 1, file, file + 1]:
                if 0 <= f <= 7 and board[r][f] == 'P':
                    passed = False
                    break
        if passed:
            bonus = 20 + rank * 15
            if is_endgame:
                bonus *= 2
            pawn_structure_score -= bonus
        
        # Backward pawns
        if rank > 1:
            backward = True
            if board[rank+1][file] is None:
                for f in [file - 1, file + 1]:
                    if 0 <= f <= 7:
                        for r, f2 in black_pawns:
                            if f2 == f and r >= rank:
                                backward = False
                                break
            else:
                backward = False
            
            if backward:
                pawn_structure_score += 15
        
        # Pawn chains
        connected = False
        for f in [file - 1, file + 1]:
            if 0 <= f <= 7:
                if board[rank][f] == 'p' or (rank > 0 and board[rank-1][f] == 'p'):
                    connected = True
                    break
        if connected:
            pawn_structure_score -= 5
    
    # TRAPPED PIECES EVALUATION
    for piece, rank, file in white_pieces:
        if piece in 'NBR':
            moves = get_piece_moves(piece, rank, file)
            if len(moves) <= 2:  # Very limited mobility
                if piece == 'N':
                    trapped_pieces_penalty -= 50
                elif piece == 'B':
                    trapped_pieces_penalty -= 50
                elif piece == 'R' and len(moves) == 0:
                    trapped_pieces_penalty -= 100
    
    for piece, rank, file in black_pieces:
        if piece in 'nbr':
            moves = get_piece_moves(piece, rank, file)
            if len(moves) <= 2:
                if piece == 'n':
                    trapped_pieces_penalty += 50
                elif piece == 'b':
                    trapped_pieces_penalty += 50
                elif piece == 'r' and len(moves) == 0:
                    trapped_pieces_penalty += 100
    
    # EVALUATION PATTERNS
    
    # Bishop pair bonus (original logic - now enhanced in advanced patterns)
    white_bishops_count = sum(1 for p, r, f in white_pieces if p == 'B')
    black_bishops_count = sum(1 for p, r, f in black_pieces if p == 'b')
    if white_bishops_count >= 2:
        pattern_score += 35
    if black_bishops_count >= 2:
        pattern_score -= 35
    
    # Knight outpost (knight on strong square protected by pawn)
    for piece, rank, file in white_pieces:
        if piece == 'N' and rank <= 3:  # In enemy territory
            # Check if protected by pawn
            protected = False
            if rank < 7:
                if file > 0 and board[rank+1][file-1] == 'P':
                    protected = True
                if file < 7 and board[rank+1][file+1] == 'P':
                    protected = True
            
            if protected:
                # Check if can't be attacked by enemy pawns
                safe = True
                if rank > 0:
                    for f in [file - 1, file + 1]:
                        if 0 <= f <= 7:
                            for r in range(rank):
                                if board[r][f] == 'p':
                                    safe = False
                                    break
                
                if safe:
                    pattern_score += 30
    
    for piece, rank, file in black_pieces:
        if piece == 'n' and rank >= 4:
            protected = False
            if rank > 0:
                if file > 0 and board[rank-1][file-1] == 'p':
                    protected = True
                if file < 7 and board[rank-1][file+1] == 'p':
                    protected = True
            
            if protected:
                safe = True
                if rank < 7:
                    for f in [file - 1, file + 1]:
                        if 0 <= f <= 7:
                            for r in range(rank + 1, 8):
                                if board[r][f] == 'P':
                                    safe = False
                                    break
                
                if safe:
                    pattern_score -= 30
    
    # Rook on 7th rank bonus
    for piece, rank, file in white_pieces:
        if piece == 'R' and rank == 1:  # 7th rank
            pattern_score += 20
            # Extra bonus if doubled rooks on 7th
            if any(p == 'R' and r == 1 and f != file for p, r, f in white_pieces):
                pattern_score += 10
    
    for piece, rank, file in black_pieces:
        if piece == 'r' and rank == 6:  # 2nd rank
            pattern_score -= 20
            if any(p == 'r' and r == 6 and f != file for p, r, f in black_pieces):
                pattern_score -= 10
    
    # Rook on open/semi-open file
    for file in range(8):
        has_white_pawn = any(f == file for r, f in white_pawns)
        has_black_pawn = any(f == file for r, f in black_pawns)
        has_white_rook = any(p == 'R' and f == file for p, r, f in white_pieces)
        has_black_rook = any(p == 'r' and f == file for p, r, f in black_pieces)
        
        if has_white_rook and not has_white_pawn:
            if not has_black_pawn:
                pattern_score += 25  # Open file
            else:
                pattern_score += 12  # Semi-open file
        
        if has_black_rook and not has_black_pawn:
            if not has_white_pawn:
                pattern_score -= 25
            else:
                pattern_score -= 12
    
    # TEMPO EVALUATION (development in opening)
    if not is_endgame and total_pieces > 20:  # Opening/early middlegame
        # Penalize undeveloped pieces
        if board[7][1] == 'N':  # Knight on b1
            tempo_score -= 10
        if board[7][6] == 'N':  # Knight on g1
            tempo_score -= 10
        if board[7][2] == 'B':  # Bishop on c1
            tempo_score -= 10
        if board[7][5] == 'B':  # Bishop on f1
            tempo_score -= 10
        
        if board[0][1] == 'n':  # Knight on b8
            tempo_score += 10
        if board[0][6] == 'n':  # Knight on g8
            tempo_score += 10
        if board[0][2] == 'b':  # Bishop on c8
            tempo_score += 10
        if board[0][5] == 'b':  # Bishop on f8
            tempo_score += 10
        
        # Bonus for castling
        if white_king_pos:
            kr, kf = white_king_pos
            if kr == 7 and (kf <= 2 or kf >= 6):  # Likely castled
                tempo_score += 25
        
        if black_king_pos:
            kr, kf = black_king_pos
            if kr == 0 and (kf <= 2 or kf >= 6):  # Likely castled
                tempo_score -= 25
    
    # ENHANCED CENTER CONTROL
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    extended_center = [(2, 2), (2, 3), (2, 4), (2, 5),
                       (3, 2), (3, 5), (4, 2), (4, 5),
                       (5, 2), (5, 3), (5, 4), (5, 5)]
    
    # Pieces controlling center
    for rank, file in center_squares:
        piece = board[rank][file]
        if piece:
            if piece.isupper():
                center_control_score += 20
            else:
                center_control_score -= 20
        
        # Control by pawns is especially valuable
        # Check white pawn control
        if rank < 7:
            if file > 0 and board[rank+1][file-1] == 'P':
                center_control_score += 15
            if file < 7 and board[rank+1][file+1] == 'P':
                center_control_score += 15
        
        # Check black pawn control
        if rank > 0:
            if file > 0 and board[rank-1][file-1] == 'p':
                center_control_score -= 15
            if file < 7 and board[rank-1][file+1] == 'p':
                center_control_score -= 15
    
    for rank, file in extended_center:
        piece = board[rank][file]
        if piece:
            if piece.isupper():
                center_control_score += 5
            else:
                center_control_score -= 5
    
    # KING SAFETY (enhanced)
    if not is_endgame:
        # White king safety
        if white_king_pos:
            kr, kf = white_king_pos
            safety = 0
            
            # Pawn shield
            if kr >= 6:  # King on back ranks
                shield_files = []
                if kf > 0:
                    shield_files.append(kf - 1)
                shield_files.append(kf)
                if kf < 7:
                    shield_files.append(kf + 1)
                
                for f in shield_files:
                    if kr > 0 and board[kr-1][f] == 'P':
                        safety += 10
                    elif kr > 1 and board[kr-2][f] == 'P':
                        safety += 5
            
            # Penalty for open files near king
            for f in range(max(0, kf-1), min(8, kf+2)):
                if not any(r_pos == f for r_pos, f_pos in white_pawns):
                    safety -= 15
            
            king_safety_score += safety
        
        # Black king safety
        if black_king_pos:
            kr, kf = black_king_pos
            safety = 0
            
            if kr <= 1:
                shield_files = []
                if kf > 0:
                    shield_files.append(kf - 1)
                shield_files.append(kf)
                if kf < 7:
                    shield_files.append(kf + 1)
                
                for f in shield_files:
                    if kr < 7 and board[kr+1][f] == 'p':
                        safety += 10
                    elif kr < 6 and board[kr+2][f] == 'p':
                        safety += 5
            
            # Penalty for open files near king
            for f in range(max(0, kf-1), min(8, kf+2)):
                if not any(f_pos == f for r_pos, f_pos in black_pawns):
                    safety -= 15
            
            king_safety_score -= safety
    
    # ADVANCED PATTERN RECOGNITION
    advanced_pattern_score = evaluate_advanced_patterns(
        board, white_pieces, black_pieces, white_pawns, black_pawns,
        white_bishops, black_bishops, white_knights, black_knights,
        white_rooks, black_rooks, white_queen_pos, black_queen_pos,
        white_king_pos, black_king_pos, game_phase
    )
    
    # TOTAL EVALUATION (enhanced with pattern recognition)
    total_score = (material_score + 
                   position_score + 
                   pawn_structure_score + 
                   mobility_score * 2 + 
                   center_control_score + 
                   king_safety_score + 
                   space_score + 
                   tempo_score + 
                   trapped_pieces_penalty + 
                   pattern_score +
                   advanced_pattern_score)  # Added advanced patterns
    
    # Return from perspective of side to move
    if white_turn:
        return total_score
    else:
        return -total_score


def evaluate_material_only(board_string):
    """
    Quick material-only evaluation for move ordering
    
    Args:
        board_string: 64-character string representing the board
    
    Returns:
        Material balance in centipawns (positive favors white)
    """
    PIECE_VALUES = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0,
        'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': 0
    }
    
    score = 0
    for piece in board_string:
        if piece in PIECE_VALUES:
            score += PIECE_VALUES[piece]
    
    return score


def is_endgame(board_string):
    """
    Determine if position is in endgame phase
    
    Args:
        board_string: 64-character string representing the board
    
    Returns:
        Boolean indicating if position is endgame
    """
    queen_count = board_string.count('Q') + board_string.count('q')
    piece_count = sum(1 for c in board_string if c in 'QRBNqrbn')
    
    return queen_count == 0 or piece_count <= 10


# Debug function for evaluation breakdown
def evaluate_position_detailed(board_string, white_turn):
    """
    Detailed evaluation with component breakdown for debugging
    
    Args:
        board_string: 64-character string representing the board
        white_turn: Boolean indicating if it's white's turn
    
    Returns:
        Tuple of (total_score, component_dict)
    """
    # This would be similar to evaluate_position but return detailed breakdown
    # Implementation omitted for brevity - use for debugging AI decisions
    pass


def demonstrate_phase_differences(piece='P', square=35):  # d4 square
    """
    Demonstrate how piece values change across game phases
    
    Args:
        piece: Piece character ('P', 'N', 'B', 'R', 'Q', 'K')
        square: Square index (0-63)
    """
    print(f"\n=== {piece} on square {square} (rank {square//8 + 1}, file {chr(ord('a') + square%8)}) ===")
    
    # Get PST tables for the piece
    if piece == 'P':
        opening_table = PST_PAWN_OPENING
        middle_table = PST_PAWN_MIDDLEGAME  
        endgame_table = PST_PAWN_ENDGAME
    elif piece == 'N':
        opening_table = PST_KNIGHT_OPENING
        middle_table = PST_KNIGHT_MIDDLEGAME
        endgame_table = PST_KNIGHT_ENDGAME
    elif piece == 'B':
        opening_table = PST_BISHOP_OPENING
        middle_table = PST_BISHOP_MIDDLEGAME
        endgame_table = PST_BISHOP_ENDGAME
    elif piece == 'R':
        opening_table = PST_ROOK_OPENING
        middle_table = PST_ROOK_MIDDLEGAME
        endgame_table = PST_ROOK_ENDGAME
    elif piece == 'Q':
        opening_table = PST_QUEEN_OPENING
        middle_table = PST_QUEEN_MIDDLEGAME
        endgame_table = PST_QUEEN_ENDGAME
    elif piece == 'K':
        opening_table = PST_KING_OPENING
        middle_table = PST_KING_MIDDLEGAME
        endgame_table = PST_KING_ENDGAME
    else:
        print("Unknown piece")
        return
    
    print(f"Opening value:   {opening_table[square]:+4d}")
    print(f"Middlegame value: {middle_table[square]:+4d}")
    print(f"Endgame value:   {endgame_table[square]:+4d}")
    
    # Show interpolated values at different phases
    for phase in [0.0, 0.25, 0.5, 0.75, 1.0]:
        if phase < 0.5:
            phase_factor = phase * 2
            value = opening_table[square] + (middle_table[square] - opening_table[square]) * phase_factor
        else:
            phase_factor = (phase - 0.5) * 2
            value = middle_table[square] + (endgame_table[square] - middle_table[square]) * phase_factor
        
        phase_name = ["Opening", "Early Mid", "Middlegame", "Late Mid", "Endgame"][int(phase * 4)]
        print(f"Phase {phase:.2f} ({phase_name}): {value:+6.1f}")


def analyze_position_by_phase(board_string):
    """
    Show how position evaluation changes if it were in different game phases
    
    Args:
        board_string: 64-character string representing the board
    """
    print(f"\n=== POSITION ANALYSIS ACROSS PHASES ===")
    print(f"Actual game phase: {get_game_phase(board_string):.3f}")
    
    # Temporarily modify the get_game_phase function behavior
    original_phase = get_game_phase(board_string)
    
    phases = [0.0, 0.25, 0.5, 0.75, 1.0]
    phase_names = ["Opening", "Early Mid", "Middlegame", "Late Mid", "Endgame"]
    
    for i, phase in enumerate(phases):
        # Create a dummy board string that would result in this phase
        # This is a hack for demonstration - in practice you'd modify the evaluation function
        print(f"{phase_names[i]} (phase {phase:.2f}): ", end="")
        
        # For demonstration, we'll show the difference in PST values only
        material_score = 0
        position_score = 0
        
        PIECE_VALUES = {
            'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
            'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
        }
        
        for square_index, piece in enumerate(board_string):
            if piece == '.':
                continue
                
            # Material
            material_score += PIECE_VALUES.get(piece, 0)
            
            # Position (simplified calculation)
            if piece == 'P':
                opening_val = PST_PAWN_OPENING[square_index]
                middle_val = PST_PAWN_MIDDLEGAME[square_index]
                endgame_val = PST_PAWN_ENDGAME[square_index]
            elif piece == 'p':
                opening_val = -PST_PAWN_OPENING[63 - square_index]
                middle_val = -PST_PAWN_MIDDLEGAME[63 - square_index]
                endgame_val = -PST_PAWN_ENDGAME[63 - square_index]
            elif piece == 'N':
                opening_val = PST_KNIGHT_OPENING[square_index]
                middle_val = PST_KNIGHT_MIDDLEGAME[square_index]
                endgame_val = PST_KNIGHT_ENDGAME[square_index]
            elif piece == 'n':
                opening_val = -PST_KNIGHT_OPENING[63 - square_index]
                middle_val = -PST_KNIGHT_MIDDLEGAME[63 - square_index]
                endgame_val = -PST_KNIGHT_ENDGAME[63 - square_index]
            else:
                opening_val = middle_val = endgame_val = 0
            
            # Interpolate
            if phase < 0.5:
                phase_factor = phase * 2
                pst_value = opening_val + (middle_val - opening_val) * phase_factor
            else:
                phase_factor = (phase - 0.5) * 2
                pst_value = middle_val + (endgame_val - middle_val) * phase_factor
            
            position_score += pst_value
        
        total_simplified = material_score + position_score
        print(f"{total_simplified:+7.1f} (Material: {material_score:+5.0f}, Position: {position_score:+6.1f})")


if __name__ == "__main__":
    # Test the enhanced evaluation function with pattern recognition
    starting_position = "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR"
    
    print("=== ENHANCED EVALUATION WITH ADVANCED PATTERNS ===")
    print("Starting position evaluation:")
    print(f"Score: {evaluate_position(starting_position, True)}")
    print(f"Material only: {evaluate_material_only(starting_position)}")
    print(f"Is endgame: {is_endgame(starting_position)}")
    print(f"Game phase: {get_game_phase(starting_position):.2f}")
    
    # Test position with advanced patterns
    print("\n=== PATTERN RECOGNITION TESTS ===")
    
    # 1. Position with knight outpost on d5
    outpost_pos = "r1bqkb1rpppp1ppp....n......NP.................................PPPP.PPPRNBQKB1R"
    print(f"\nKnight outpost position: {evaluate_position(outpost_pos, True)}")
    
    # 2. Position with bishop pair
    bishop_pair_pos = "r1bqk2rpppp1pppn.......b..........P...........N...........PPPP.PPPRNBQK2R"
    print(f"Bishop pair position: {evaluate_position(bishop_pair_pos, True)}")
    
    # 3. Position with doubled rooks
    doubled_rooks_pos = "....k...........r.......r...............................R.......R.......K..."
    print(f"Doubled rooks position: {evaluate_position(doubled_rooks_pos, True)}")
    
    # 4. Endgame with king activity
    active_king_pos = "........k.......p...............................P.......K........"
    print(f"Active king endgame: {evaluate_position(active_king_pos, True)}")
    
    # 5. Test endgame position
    endgame_position = "........k.......................................................K......."
    print(f"\nEndgame position evaluation: {evaluate_position(endgame_position, True)}")
    print(f"Is endgame: {is_endgame(endgame_position)}")
    print(f"Game phase: {get_game_phase(endgame_position):.2f}")
    
    print("\n=== PATTERN FEATURES IMPLEMENTED ===")
    print("✓ Queen-Rook batteries")
    print("✓ Enhanced bishop pair evaluation")
    print("✓ Bad bishop detection") 
    print("✓ Knight fork potential")
    print("✓ Doubled rooks on files")
    print("✓ Rook behind passed pawn")
    print("✓ Pawn majority evaluation")
    print("✓ King activity in endgame")
    print("✓ Pin detection (tactical)")
    print("✓ Weak square identification")
    print("✓ Fianchettoed bishop patterns")
    print("✓ Connected rook evaluation")
    print("✓ All integrated with phase-dependent evaluation!")