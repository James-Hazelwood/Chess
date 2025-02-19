import time

from board import Board

def check_all_moves(board, color, rem_depth):

    moves = 0
    all_moves = board.add_all_moves(color)
    for move in all_moves:
        if rem_depth > 1:
            board.make_move(move)
            moves += check_all_moves(board, board.other_color(color), rem_depth - 1)
            board.undo_move(move)
        else:
            moves += 1

    return moves

if __name__ == "__main__":
    board = Board()

    for i in range(1,5):
        start_time = time.time()
        print(check_all_moves(board, "white", i), time.time() - start_time)

    # print(check_all_moves("white", 5))

    # times for rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
    # 20          0.000316619873046875
    # 400         0.005789756774902344
    # 8902        0.1269993782043457
    # 197281      2.846599817276001
    # 4865609     69.75066232681274