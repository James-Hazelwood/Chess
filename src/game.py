import pygame

from copy import deepcopy
from const import *
from ai import Ai
from board import Board

class Game:

    def __init__(self, dragger, board):
        self.board = board
        self.dragger = dragger
        self.turn = "white"
        self.board.add_all_moves(self.turn)

        self.game_log = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]
        self.index = 0

        self.player_white = Ai()
        self.player_black = Ai()
        self.game_over = False

    def ai_play(self):
        move = self.player_black.play(self.board, self.turn)
        self.board.make_move(move)
        self.change_turn()

    def change_turn(self):

        self.remove_future_states()
        self.index += 1
        new_fen = self.board.convert_board_to_fen()

        # check draws (stalemate later)
        if self.check_50_move_rule() or self.threefold_rep(new_fen):
            self.game_over = True

        self.game_log.append(new_fen)
        self.board.reset_all_color_moves(self.turn)
        self.turn = "black" if self.turn == "white" else "white"
        moves = self.board.add_all_moves(self.turn)

        # check checkmate and stalemate
        if self.board.check_checkmate(moves):
            self.game_over = True

    def undo_move(self):
        if self.index != 0:
            self.index -= 1
            self.game_over = False
            self.turn = "black" if self.turn == "white" else "white"
            print(self.game_log, self.index)
            self.board = Board(self.game_log[self.index])
            self.board.add_all_moves(self.turn)

    def redo_move(self):
        if self.index != len(self.game_log) - 1:
            self.index += 1
            self.turn = "black" if self.turn == "white" else "white"
            print(self.game_log, self.index)
            self.board = Board(self.game_log[self.index])
            moves = self.board.add_all_moves(self.turn)
            if self.board.check_checkmate(moves):
                self.game_over = True

    def remove_future_states(self):
        del self.game_log[self.index + 1:]

    def check_50_move_rule(self):
        if self.board.uneventful_moves > 99:
            return True

    def threefold_rep(self, fen):
        matches = 0
        for prev_pos in self.game_log:
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
        for row in range(ROWS):
            for col in range(COLS):

                # check for pieces
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    # blit all pieces except the one dragging
                    if [row, col] != [self.dragger.initial_row, self.dragger.initial_col]:
                        img = pygame.image.load(piece.image)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.image_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.image_rect)

    def show_moves(self, surface, piece):
        for row, col in piece.moves:
            if (row + col) % 2 == 0:
                # light red
                color = WHITE_COLOR_POSSIBLE
            else:
                # darker red
                color = BLACK_COLOR_POSSIBLE

            rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        if self.board.last_piece_moved is not None:
            rect = (self.board.last_piece_moved[1] * SQSIZE, self.board.last_piece_moved[0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, LAST_COLOR, rect)

    def show_cur_dragged_piece(self, surface, row_col):
        rect = (row_col[1] * SQSIZE, row_col[0] * SQSIZE, SQSIZE, SQSIZE)
        pygame.draw.rect(surface, CUR_DRAG, rect)

    def show_in_check(self, surface):
        if self.board.in_check_var:
            loc = self.board.get_king_loc(self.board.in_check_var)
            rect = (loc[1] * SQSIZE, loc[0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, CHECK, rect)
