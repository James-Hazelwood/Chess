from copy import deepcopy

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

        self.sound = Sound()


    def mainloop(self):

        while True:

            # update screen every frame
            self.game.show_bg(self.screen)
            self.game.show_last_move(self.screen)
            self.game.show_in_check(self.screen)

            self.board = self.game.board

            if self.dragger.dragging:
                self.game.show_moves(self.screen, self.dragger.piece)
                self.game.show_cur_dragged_piece(self.screen, self.dragger.get_initial_loc())
                self.game.show_pieces(self.screen)
                self.dragger.update_blit(self.screen)
            else:
                self.game.show_pieces(self.screen)

            # all user inputs
            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.dragger.update_mouse(event.pos)

                    clicked_row = self.dragger.mouse_y // SQSIZE
                    clicked_col = self.dragger.mouse_x // SQSIZE

                    # checking if clicked square has a piece
                    if self.board.squares[clicked_row][clicked_col].has_piece():
                        piece = self.board.squares[clicked_row][clicked_col].piece

                        self.dragger.save_initial(clicked_row, clicked_col, piece)

                # drag
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragger.dragging:
                        self.dragger.update_mouse(event.pos)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.dragger.dragging:
                        self.dragger.update_mouse(event.pos)
                        released_row = self.dragger.mouse_y // SQSIZE
                        released_col = self.dragger.mouse_x // SQSIZE

                        if self.board.valid_move(self.dragger.piece, released_row, released_col):

                            # sfx
                            if self.board.is_capture(self.dragger.piece, released_row, released_col):
                                self.sound.capture_sound()
                            else:
                                self.sound.move_sound()

                            # pawn promotion
                            if self.board.check_pawn_promotion(self.dragger.piece, released_row):
                                promotion = show_promotion_popup()
                                if promotion is not None:
                                    self.board.make_move(self.dragger.piece, self.dragger.initial_row,
                                                        self.dragger.initial_col,
                                                        released_row, released_col, promotion)
                                    self.game.change_turn()
                            else:
                                self.board.make_move(self.dragger.piece, self.dragger.initial_row, self.dragger.initial_col,
                                                 released_row, released_col)
                                self.game.change_turn()

                        # reset moves
                        self.dragger.undrag_piece()

                elif event.type == pygame.KEYDOWN:

                    # reset
                    if event.key == pygame.K_r:
                        # make a new board and game from scratch
                        self.board = Board()
                        self.game = Game(self.dragger, self.board)

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

                # quit game
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

if __name__ == "__main__":
    main = Main()
    main.mainloop()
