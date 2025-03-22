import time

from src.board import Board
from src.piece import Pawn, Knight
from src.move import Move

class Ai:

    def __init__(self, board):
        self.board = board

    def play(self, turn):
        return self.mini_max(turn, 1, -100000000, 100000000, 0)

    def reset(self, board):
        self.board = board

    def evaluate_pos(self):

        score = 0
        for row, col in self.board.pieces["white"]:
            piece = self.board.squares[row][col].piece
            score += piece.value * 100 + self.piece_table_score(row, col, piece, self.board.pieces_left)

        for row, col in self.board.pieces["black"]:
            piece = self.board.squares[row][col].piece
            score -= piece.value * 100 + self.piece_table_score(7 - row, col, piece, self.board.pieces_left)

        if self.board.castled[0] == 1:
            score += 1000

        if self.board.castled[1] == 1:
            score -= 1000

        return score

    def piece_table_score(self, row, col, piece, pieces_left):
        early_game_val = piece.piece_table_early[row][col]
        late_game_val = piece.piece_table_late[row][col]
        return (late_game_val - early_game_val) * (32 - pieces_left)/32 + early_game_val

    def _mini_max(self, turn, rem_depth, alpha, beta, n):
        moves = self.board.add_all_moves(turn)
        if self.board.check_checkmate():
            if turn == "white":
                return -1000000 + 100 * n
            else:
                return 1000000 - 100 * n

        if self.board.check_stalemate():
            return 0

        if rem_depth == 0:
            return self.evaluate_pos()

        if turn == "white":
            max_eval = -100000000
            for move in moves:
                self.board.make_move(move)
                evaluation = self._mini_max(self.board.other_color(turn), rem_depth - 1, alpha, beta, n + 1)
                self.board.undo_move(move)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = 100000000
            for move in moves:
                self.board.make_move(move)
                evaluation = self._mini_max(self.board.other_color(turn), rem_depth - 1, alpha, beta, n + 1)
                self.board.undo_move(move)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval

    def mini_max(self, turn, rem_depth, alpha, beta, n):
        moves = self.board.add_all_moves(turn)
        move_evals = []
        if turn == "white":
            max_eval = -100000000
            for move in moves:
                self.board.make_move(move)
                evaluation = self._mini_max(self.board.other_color(turn), rem_depth - 1, alpha, beta, n + 1)
                self.board.undo_move(move)
                move_evals.append(evaluation)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            best_eval = max_eval

        else:
            min_eval = 100000000
            for move in moves:
                self.board.make_move(move)
                evaluation = self._mini_max(self.board.other_color(turn), rem_depth - 1, alpha, beta, n + 1)
                self.board.undo_move(move)
                move_evals.append(evaluation)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            best_eval = min_eval

        for i in range(len(move_evals)):
            if move_evals[i] == best_eval:
                return moves[i]

if __name__ == "__main__":
    board = Board("8/2R5/k1B5/2B5/8/8/PPP5/R2K4")
    ai = Ai(board)
    turn = "white"
    start_time = time.time()
    print(ai.play(turn).make_move_readable(), time.time() - start_time)

    ## depth 4 > a8b8 1.0055675506591797
    ## depth 3 > a8b8 0.05347490310668945