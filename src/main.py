import time

import pygame
import sys

from const import *
from game import Game
from board import Board
from dragger import Dragger
from promotion import *
from sound import Sound

class Main:

    def __init__(self):
        pygame.init()

        # basic pygame setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        empty_icon = pygame.Surface((1, 1))
        pygame.display.set_icon(empty_icon)

        self.board = Board()
        self.dragger = Dragger()
        self.game = Game(self.dragger, self.board)

        # change who's playing
        self.white_player = "human"
        self.black_player = "human"
        self.human_move = False

        self.time_between_ai_move = 0.20

        self.stop_flag = False

        self.sound = Sound()


    def mainloop(self):

        while True:

            self.update_screen()
            self.human_move = self.white_player == "human" and self.game.turn == "white" or self.black_player == "human" and self.game.turn == "black"

            if not self.human_move and not self.stop_flag and not self.game.game_over:
                self.game.ai_play()
                time.sleep(self.time_between_ai_move)

            # all user inputs
            for event in pygame.event.get():

                # if it's not a human turn, don't allow humans to interact
                if self.human_move and not self.game.game_over:
                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.click(event)

                    # drag
                    elif event.type == pygame.MOUSEMOTION:
                        self.drag(event)

                    # click release
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.release(event)

                # key press
                if event.type == pygame.KEYDOWN:
                        self.key_press(event)

                # quit game
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

    # update screen every frame
    def update_screen(self):
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_in_check(self.screen)

        self.board = self.game.board

        if self.dragger.dragging:
            self.game.show_moves(self.screen, self.dragger.initial_row, self.dragger.initial_col)
            self.game.show_cur_dragged_piece(self.screen, self.dragger.get_initial_loc())
            self.game.show_pieces(self.screen)
            self.dragger.update_blit(self.screen)
        else:
            self.game.show_pieces(self.screen)

    def click(self, event):
        self.dragger.update_mouse(event.pos)

        clicked_row = self.dragger.mouse_y // SQSIZE
        clicked_col = self.dragger.mouse_x // SQSIZE

        # checking if clicked square has a piece
        if self.board.squares[clicked_row][clicked_col].has_piece():
            piece = self.board.squares[clicked_row][clicked_col].piece

            self.dragger.save_initial(clicked_row, clicked_col, piece)

    def drag(self, event):
        if self.dragger.dragging:
            self.dragger.update_mouse(event.pos)

    def release(self, event):
        if self.dragger.dragging:
            self.dragger.update_mouse(event.pos)
            released_row = self.dragger.mouse_y // SQSIZE
            released_col = self.dragger.mouse_x // SQSIZE

            move = self.board.get_move([self.dragger.initial_row, self.dragger.initial_col], [released_row, released_col])

            if move:

                # sfx
                if self.board.is_capture(move):
                    self.sound.capture_sound()
                else:
                    self.sound.move_sound()

                # pawn promotion
                if move.promotion is not None:
                    promotion = show_promotion_popup()
                    move.promotion = promotion
                    if promotion is None:
                        return

                self.board.make_move(move)
                self.game.change_turn(move)

            # reset moves
            self.dragger.undrag_piece()

    def key_press(self, event):
        # reset
        if event.key == pygame.K_r:
            # make a new board and game from scratch
            self.board = Board()
            self.game = Game(self.dragger, self.board)

        if event.key == pygame.K_s:
            # stop ai from making moves
            self.stop_flag = False if self.stop_flag else True

        # quit game
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        # undo
        if event.key == pygame.K_LEFT:
            self.game.undo_move()

        # redo
        if event.key == pygame.K_RIGHT:
            self.game.redo_move()


if __name__ == "__main__":
    main = Main()
    main.mainloop()

# ['b6a4', 'c3b5', 'f6g8', 'e5c4', 0]
# r3k1Nr/p1ppqpb1/bn2pnp1/3P4/1pN1P3/2N2Q1p/PPPBBPPP/R3K2R/ 0 6 [2, 5] [0, 6]
