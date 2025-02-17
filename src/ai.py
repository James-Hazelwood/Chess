import random
from board import Board

class Ai:

    def __init__(self, board):
        self.board = board

    def play(self):
        return self._choose_random_move()

    def _choose_random_move(self):
        possible_moves = self.board.add_all_moves()
        return possible_moves[random.randint(0, len(possible_moves) - 1)]
