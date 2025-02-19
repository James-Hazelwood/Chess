import random
import time

from board import Board

class Ai:

    def __init__(self, board):
        self.board = board

    def play(self, board, color):
        return self._choose_random_move(board, color)

    def _choose_random_move(self, board, color):
        possible_moves = board.legal_moves
        return possible_moves[random.randint(0, len(possible_moves) - 1)]

    def check_all_moves(self, color, rem_depth):

        moves = 0
        all_moves = self.board.add_all_moves(color)
        for move in all_moves:
            if rem_depth > 1:
                self.board.make_move(move)
                moves += self.check_all_moves(self.board.other_color(color), rem_depth - 1)
                self.board.undo_move(move)
            else:
                moves += 1

        return moves
