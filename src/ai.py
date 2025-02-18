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

    def check_all_moves(self, color, rem_depth, cur_move):

        moves = 0
        all_moves = self.board.add_all_moves(color)
        for move in all_moves:
            cur_move[rem_depth - 1] = move.make_move_readable()
            if rem_depth > 1:
                print(cur_move)
                self.board.make_move(move)
                moves += self.check_all_moves(self.board.other_color(color), rem_depth - 1, cur_move)
                self.board.undo_move(move)
            else:
                moves += 1

        return moves

if __name__ == "__main__":
    b = Board("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R")
    ai = Ai(b)

    print(ai.check_all_moves("white", 4, [0,0,0,0,0]))

    # times for rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
    # 20      0.0003483295440673828
    # 400      0.007602691650390625
    # 8902      0.16727614402770996
    # 197281      3.696542501449585
    # 4865591      131.15147471427917
