import time

import pygame
import sys

from const import *
from game import Game
from dragger import Dragger
from sound import Sound

class Main:

    def __init__(self):
        pygame.init()

        # basic pygame setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        empty_icon = pygame.Surface((1, 1))
        pygame.display.set_icon(empty_icon)

        # change this to change start of the game
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

        # lol
        self.destroy_matt = False

        self.dragger = Dragger()
        self.game = Game(self.dragger, self.fen, self.destroy_matt)

        # used for promotions
        self.promotion_state = False
        self.promotion_move = None

        # change who's playing
        self.white_player = "bot"
        self.black_player = "bot"
        self.human_move = False

        self.time_between_ai_move = 0.00
        self.stop_flag = False

        self.sound = Sound()

    def mainloop(self, simulation):

        while True:

            self.update_screen()
            self.human_move = self.white_player == "human" and self.game.turn == "white" or self.black_player == "human" and self.game.turn == "black"

            if self.game.game_state != "play" and simulation:
                if self.game.game_state == "draw":
                    return 0
                elif self.game.game_state == "white wins":
                    return 1
                else:
                    return -1


            if not self.human_move and not self.stop_flag and self.game.game_state == "play":
                self.game.ai_play()
                time.sleep(self.time_between_ai_move)

            # all user inputs
            for event in pygame.event.get():

                # if it's not a human turn, don't allow humans to interact
                if self.human_move and self.game.game_state == "play":
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

        if self.dragger.dragging:
            self.game.show_moves(self.screen, self.dragger.initial_row, self.dragger.initial_col)
            self.game.show_cur_dragged_piece(self.screen, self.dragger.get_initial_loc())
            self.game.show_pieces(self.screen)
            self.dragger.update_blit(self.screen)
        else:
            self.game.show_pieces(self.screen)

        if self.promotion_state:
            self.game.show_promotion(self.screen, self.promotion_move)

    def click(self, event):
        self.dragger.update_mouse(event.pos)

        clicked_row = self.dragger.mouse_y // SQSIZE
        clicked_col = self.dragger.mouse_x // SQSIZE

        # see if user selects piece in promotion_state
        if self.promotion_state:
            if self.promotion_move.end[1] == clicked_col:
                direction = self.promotion_move.piece.dir
                start_row = self.promotion_move.end[0]
                i = 0
                for piece in ["queen", "rook", "knight", "bishop"]:
                    if clicked_row == start_row + (i * -direction):
                        self.promotion_move.promotion = piece
                        self.game.board.make_move(self.promotion_move)
                        self.game.change_turn(self.promotion_move)
                    i += 1
            # reset promotions       
            self.promotion_move = None
            self.promotion_state = False
            return

        # checking if clicked square has a piece
        elif self.game.board.squares[clicked_row][clicked_col].has_piece():
            piece = self.game.board.squares[clicked_row][clicked_col].piece

            self.dragger.save_initial(clicked_row, clicked_col, piece)

    def drag(self, event):
        if self.dragger.dragging:
            self.dragger.update_mouse(event.pos)

    def release(self, event):
        if self.dragger.dragging:
            self.dragger.update_mouse(event.pos)
            released_row = self.dragger.mouse_y // SQSIZE
            released_col = self.dragger.mouse_x // SQSIZE

            move = self.game.board.get_move([self.dragger.initial_row, self.dragger.initial_col], [released_row, released_col])

            if move:

                # sfx
                if self.game.board.is_capture(move):
                    self.sound.capture_sound()
                else:
                    self.sound.move_sound()

                # pawn promotion
                if move.promotion is not None:
                    self.promotion_state = True
                    self.promotion_move = move

                else:
                    self.game.board.make_move(move)
                    self.game.change_turn(move)

            # reset moves
            self.dragger.undrag_piece()

    def key_press(self, event):
        # reset
        if event.key == pygame.K_r:
            self.game.reset(self.fen, self.destroy_matt)

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

    def simulation(self, n):
        sign = 1
        x = 0
        for i in range(n):
            result = main.mainloop(True)
            self.game.reset()
            print(f"Game {i + 1}: {result}")

            x += sign * result

            sign *= -1
            self.game.player_white, self.game.player_black = self.game.player_black, self.game.player_white
            self.game.player_white.reset(self.game.board)
            self.game.player_black.reset(self.game.board)

        print(f"p1: {1000 - x}, p2: {x}")

if __name__ == "__main__":
    main = Main()
    main.mainloop(False)
    # main.simulation(1000)