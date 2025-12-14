class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = ()  # (row, col) where en passant is possible
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(
            self.current_castling_rights.wks, 
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs, 
            self.current_castling_rights.bqs
        )]
        
        # --- FIX: Dictionary moved inside __init__ using 'self' ---
        self.move_functions = {
            "P": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves
        }

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        
        # Update king position
        if move.piece_moved == "wK":
            self.white_king_pos = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_pos = (move.end_row, move.end_col)

        # Pawn promotion
        if move.is_pawn_promotion:
            # For simplicity in this fix, auto-promoting to Queen to prevent input crash
            # You can change this back to input() later if you want console input
            promoted_piece = "Q" 
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece

        # En passant
        if move.is_enpassant:
            self.board[move.start_row][move.end_col] = "--"
        
        # Update en passant
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # Castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Kingside
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = "--"
            else:  # Queenside
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = "--"

        # Update castling rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(
            self.current_castling_rights.wks, 
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs, 
            self.current_castling_rights.bqs
        ))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            
            # Update king position
            if move.piece_moved == "wK":
                self.white_king_pos = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_pos = (move.start_row, move.start_col)
            
            # Undo en passant
            if move.is_enpassant:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            
            # Undo castling rights
            self.castle_rights_log.pop()  # rid of new rights
            new_rights = self.castle_rights_log[-1]
            self.current_castling_rights = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            
            # Undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # Kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = "--"
                else:  # Queenside
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = "--"

    def update_castle_rights(self, move):
        # King or rook moves
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False

    def get_valid_moves(self):
        temp_enpassant = self.enpassant_possible
        temp_castle_rights = CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bqs
        )
        
        moves = self.get_all_possible_moves()
        
        # Generate castling moves
        self.get_castle_moves(self.white_king_pos[0], self.white_king_pos[1], moves)
        self.get_castle_moves(self.black_king_pos[0], self.black_king_pos[1], moves)

        # Remove invalid moves (that leave king in check)
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        
        # Checkmate/stalemate
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        self.enpassant_possible = temp_enpassant
        self.current_castling_rights = temp_castle_rights
        return moves

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_pos[0], self.white_king_pos[1])
        else:
            return self.square_under_attack(self.black_king_pos[0], self.black_king_pos[1])

    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move  # Switch turns
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # Switch back
        for move in opp_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:  # White pawn moves
            if self.board[r-1][c] == "--":  # 1 square
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  # 2 squares
                    moves.append(Move((r, c), (r-2, c), self.board))
            # Captures
            for dc in [-1, 1]:
                if 0 <= c+dc < 8:
                    if self.board[r-1][c+dc][0] == "b":
                        moves.append(Move((r, c), (r-1, c+dc), self.board))
                    elif (r-1, c+dc) == self.enpassant_possible:
                        moves.append(Move((r, c), (r-1, c+dc), self.board, is_enpassant=True))
        else:  # Black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            for dc in [-1, 1]:
                if 0 <= c+dc < 8:
                    if self.board[r+1][c+dc][0] == "w":
                        moves.append(Move((r, c), (r+1, c+dc), self.board))
                    elif (r+1, c+dc) == self.enpassant_possible:
                        moves.append(Move((r, c), (r+1, c+dc), self.board, is_enpassant=True))

    def get_rook_moves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.get_sliding_moves(r, c, directions, moves)

    def get_knight_moves(self, r, c, moves):
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            if 0 <= r+dr < 8 and 0 <= c+dc < 8:
                if self.board[r+dr][c+dc][0] != ("w" if self.white_to_move else "b"):
                    moves.append(Move((r, c), (r+dr, c+dc), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.get_sliding_moves(r, c, directions, moves)

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        king_moves = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        for dr, dc in king_moves:
            if 0 <= r+dr < 8 and 0 <= c+dc < 8:
                if self.board[r+dr][c+dc][0] != ("w" if self.white_to_move else "b"):
                    moves.append(Move((r, c), (r+dr, c+dc), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.white_to_move and self.current_castling_rights.wks) or \
           (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or \
           (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))

    def get_sliding_moves(self, r, c, directions, moves):
        enemy_color = "b" if self.white_to_move else "w"
        for dr, dc in directions:
            for i in range(1, 8):
                end_row = r + dr * i
                end_col = c + dc * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White king side
        self.bks = bks  # Black king side
        self.wqs = wqs  # White queen side
        self.bqs = bqs  # Black queen side

class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        
        # Pawn promotion
        self.is_pawn_promotion = (self.piece_moved[1] == "P" and 
                                 (self.end_row == 0 or self.end_row == 7))
        
        # En passant
        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self.piece_captured = "bP" if self.piece_moved == "wP" else "wP"
            
        # Castling
        self.is_castle_move = is_castle_move
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.start_row == other.start_row and
                    self.start_col == other.start_col and
                    self.end_row == other.end_row and
                    self.end_col == other.end_col)
        return False
    
    def get_chess_notation(self):
        return (self.get_rank_file(self.start_row, self.start_col) + 
                self.get_rank_file(self.end_row, self.end_col))
    
    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]