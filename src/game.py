import pygame

from const import *
from ai import Ai

class Game:

    def __init__(self, dragger, board):
        self.board = board
        self.dragger = dragger
        self.turn = "white"
        self.board.add_all_moves(self.turn)

        self.game_log_fen = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]
        self.game_log_moves = [None]
        self.index = 0

        self.player_white = Ai(self.board)
        self.player_black = Ai(self.board)
        self.game_over = False

    def ai_play(self):
        move = self.player_black.play(self.board, self.turn)
        self.board.make_move(move)
        self.change_turn(move)

    def change_turn(self, move):
        self.remove_future_states()
        self.index += 1
        new_fen = self.board.convert_board_to_fen()

        # check draws (stalemate later)
        if self.check_50_move_rule() or self.threefold_rep(new_fen):
            self.game_over = True

        self.game_log_fen.append(new_fen)
        self.game_log_moves.append(move)
        self.board.reset_all_color_moves(self.turn)
        self.turn = "black" if self.turn == "white" else "white"

        self.board.add_all_moves(self.turn)

        # check checkmate and stalemate
        if self.board.check_checkmate():
            self.game_over = True

    def undo_move(self):
        if self.index != 0:
            self.game_over = False
            self.turn = "black" if self.turn == "white" else "white"
            self.board.undo_move(self.game_log_moves[self.index])
            self.board.add_all_moves(self.turn)
            self.index -= 1

    def redo_move(self):
        if self.index != len(self.game_log_fen) - 1:
            self.index += 1
            self.turn = "black" if self.turn == "white" else "white"
            self.board.make_move(self.game_log_moves[self.index])
            self.board.add_all_moves(self.turn)
            if self.board.check_checkmate():
                self.game_over = True

    def remove_future_states(self):
        del self.game_log_fen[self.index + 1:]
        del self.game_log_moves[self.index + 1:]

    def check_50_move_rule(self):
        if self.board.uneventful_moves > 99:
            return True

    def threefold_rep(self, fen):
        matches = 0
        for prev_pos in self.game_log_fen:
            if prev_pos == fen:
                matches+= 1

        return True if matches > 1 else False

    # blit methods
    def show_bg(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    # light green
                    color = WHITE_COLOR
                else:
                    # dark green
                    color = BLACK_COLOR

                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_pieces(self, surface):
        for key in self.board.pieces.keys():
            for row, col in self.board.pieces[key]:

                # blit all pieces except the one dragging
                piece = self.board.squares[row][col].piece
                if [row, col] != [self.dragger.initial_row, self.dragger.initial_col]:
                    img = pygame.image.load(piece.image)
                    img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                    piece.image_rect = img.get_rect(center=img_center)
                    surface.blit(img, piece.image_rect)

    def show_moves(self, surface, row, col):
        for move in self.board.legal_moves:
            if move.start[0] == row and move.start[1] == col:
                if (move.end[0] + move.end[1]) % 2 == 0:
                    # light red
                    color = WHITE_COLOR_POSSIBLE
                else:
                    # darker red
                    color = BLACK_COLOR_POSSIBLE

                rect = (move.end[1] * SQSIZE, move.end[0] * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        if self.board.last_move[0][0] != -1:
            rect = (self.board.last_move[0][1] * SQSIZE, self.board.last_move[0][0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, LAST_COLOR, rect)
            rect = (self.board.last_move[1][1] * SQSIZE, self.board.last_move[1][0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, LAST_COLOR, rect)

    def show_cur_dragged_piece(self, surface, row_col):
        rect = (row_col[1] * SQSIZE, row_col[0] * SQSIZE, SQSIZE, SQSIZE)
        pygame.draw.rect(surface, CUR_DRAG, rect)

    def show_in_check(self, surface):
        if self.board.in_check_var:
            loc = self.board.get_king_loc(self.board.in_check_var)
            rect = (loc[1] * SQSIZE, loc[0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, CHECK, rect)
