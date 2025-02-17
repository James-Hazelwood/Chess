import random
from copy import deepcopy

from board import Board

class Ai:

    def play(self, board, color):
        return self._choose_random_move(board, color)

    def _choose_random_move(self, board, color):
        possible_moves = board.add_all_moves(color)
        return possible_moves[random.randint(0, len(possible_moves) - 1)]

    def check_all_moves(self, board, color, rem_depth):

        moves = 0
        all_moves = board.add_all_moves(color)
        for move in all_moves:
            if rem_depth > 1:
                new_board = deepcopy(board)
                new_board.make_move(move)
                moves += self.check_all_moves(new_board, new_board.other_color(color), rem_depth - 1)
            else:
                moves += 1

        return moves

if __name__ == "__main__":
    b = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    ai = Ai()
    print(ai.check_all_moves(b, "white", 3))
