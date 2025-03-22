import random

class AiRandom:

    def __init__(self, board):
        self.board = board

    def play(self, turn):
        return self._choose_random_move(self.board)

    def reset(self, board):
        self.board = board

    def _choose_random_move(self, board):
        possible_moves = board.legal_moves
        return possible_moves[random.randint(0, len(possible_moves) - 1)]