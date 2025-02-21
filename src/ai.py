import random
import time

from board import Board
from piece import Pawn, Knight
from move import Move

class Ai:

    def __init__(self, board):
        self.board = board

    def play(self, turn):
        return self.mini_max(turn, 3)

    def _choose_random_move(self, board):
        possible_moves = board.legal_moves
        return possible_moves[random.randint(0, len(possible_moves) - 1)]

    def evaluate_pos(self):
        score = 0
        for row, col in self.board.pieces["white"]:
            piece = self.board.squares[row][col].piece
            score += piece.value * 100 + self.piece_table_score(row, col, piece, self.board.pieces_left)

        for row, col in self.board.pieces["black"]:
            piece = self.board.squares[row][col].piece
            score -= piece.value * 100 + self.piece_table_score(7 - row, col, piece, self.board.pieces_left)

        return score

    def piece_table_score(self, row, col, piece, pieces_left):
        early_game_val = piece.piece_table_early[row][col]
        late_game_val = piece.piece_table_late[row][col]
        return (late_game_val - early_game_val) * (32 - pieces_left)/32 + early_game_val

    def _mini_max(self, turn, rem_depth):
        if rem_depth == 0:
            return self.evaluate_pos()

        moves = self.board.add_all_moves(turn)
        move_evals = []
        for move in moves:
            self.board.make_move(move)
            move_evals.append(self._mini_max(self.board.other_color(turn), rem_depth - 1))
            self.board.undo_move(move)

        if turn == "white":
            return max(move_evals)
        else:
            return min(move_evals)

    def mini_max(self, turn, rem_depth):
        moves = self.board.add_all_moves(turn)
        move_evals = []
        for move in moves:
            self.board.make_move(move)
            move_evals.append(self._mini_max(self.board.other_color(turn), rem_depth - 1))
            self.board.undo_move(move)

        if turn == "white":
            evaluation = max(move_evals)
        else:
            evaluation = min(move_evals)

        for i in range(len(move_evals)):
            if move_evals[i] == evaluation:
                return moves[i]


