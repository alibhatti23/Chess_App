import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", 
              "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not game_over:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])
                            move_made = True
                            sq_selected = ()
                            player_clicks = []
                    if not move_made:
                        player_clicks = [sq_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    game_over = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    game_over = False

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, valid_moves, sq_selected)
        
        if gs.checkmate:
            game_over = True
            text = "Black wins by checkmate" if gs.white_to_move else "White wins by checkmate"
            draw_text(screen, text)
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected:
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)

if __name__ == "__main__":
    main()