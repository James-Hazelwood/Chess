from const import *
from square import Square
from piece import *
from copy import deepcopy
from move import Move

class Board:

    def __init__(self, fen= "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):
        self.squares = []

        # dict of 2 lists of piece locations (one for each color)
        self.pieces = dict()
        self.pieces["white"] = []
        self.pieces["black"] = []

        # dict of king locations
        self.kings = dict()
        self.kings["white"] = []
        self.kings["black"] = []

        # used for 50 move rule
        self.uneventful_moves = 0

        self.in_check_var = False
        self.last_piece_moved = None

        self._create()
        self._add_pieces_fen(fen)

    # moves a piece
    def make_move(self, move, testing=False):

        piece = move.piece
        row = move.start[0]
        col = move.start[1]
        new_row = move.end[0]
        new_col = move.end[1]
        promotion = move.promotion

        self.squares[row][col].piece = None
        self.pieces[piece.color].remove([row, col])
        self.uneventful_moves += 1

        # remove captures (not en passant) (in different location)
        if self.is_capture(piece, new_row, new_col):
            self.uneventful_moves = 0
            self.pieces[piece.other_color()].remove([new_row, new_col])

        # kingside castling
        if isinstance(piece, King) and new_col - col == 2:
            self.squares[new_row][new_col].piece = piece
            self.pieces[piece.color].append([new_row, new_col])

            self.squares[row][7].piece = None
            self.pieces[piece.color].remove([row, 7])
            self.squares[new_row][5].piece = Rook(piece.color)
            self.pieces[piece.color].append([new_row, new_col])

        # queenside castling
        elif isinstance(piece, King) and new_col - col == -2:
            self.squares[new_row][new_col].piece = piece
            self.pieces[piece.color].append([new_row, new_col])

            self.squares[row][0].piece = None
            self.pieces[piece.color].remove([row, 0])
            self.squares[new_row][3].piece = Rook(piece.color)
            self.pieces[piece.color].append([new_row, new_col])

        elif promotion is None:
            # make pawns that double jump enpassantable
            if isinstance(piece, Pawn):
                self.uneventful_moves = 0
                if abs(row - new_row) == 2:
                    piece.enpassantable = True

                # enpassant
                elif col != new_col and not self.squares[new_row][new_col].has_piece():
                    self.squares[row][new_col].piece = None
                    self.pieces[piece.other_color()].remove([row, new_col])

            # standard
            self.squares[new_row][new_col].piece = piece
            self.pieces[piece.color].append([new_row, new_col])

        # promotions
        else:
            new_piece = None
            if promotion == "queen":
                new_piece = Queen(piece.color)
            elif promotion == "rook":
                new_piece = Rook(piece.color)
            elif promotion == "bishop":
                new_piece = Bishop(piece.color)
            elif promotion == "knight":
                new_piece = Knight(piece.color)

            self.squares[new_row][new_col].piece = new_piece
            self.pieces[piece.color].append([new_row, new_col])

        if not testing:
            piece.moved = True

        # update king location
        if isinstance(piece, King):
            self.kings[piece.color] = [new_row, new_col]

        # check if prev last piece is pawn and reset enpasantable
        elif self.last_piece_moved is not None:
            square = self.squares[self.last_piece_moved[0]][self.last_piece_moved[1]]
            if isinstance(square.piece, Pawn) and square.piece.color != piece.color:
                square.piece.enpassantable = False

        self.last_piece_moved = [new_row, new_col]

        # check if other kings in check
        if self.king_in_check(piece.other_color()):
            self.in_check_var = piece.other_color()
        else:
            self.in_check_var = None

    # checks if the final loc has a piece of diff color (doesn't work with en passant) < fix later
    def is_capture(self, piece, new_row, new_col):
        square = self.squares[new_row][new_col]
        if square.has_piece() and square.piece.color != piece.color:
            return True
        else:
            return False

    # checks if a pawn promotion will occur
    def check_pawn_promotion(self, piece, new_row) -> bool:
        return isinstance(piece, Pawn) and (new_row == 0 or new_row == 7)

    # if there are no legal moves, its checkmate or stalemate < add later
    def check_checkmate(self, moves):
        if not moves:
            return True
        else:
            return False

    # adds all moves to color, returns full list
    def add_all_moves(self, color):
        total_moves = []
        for row, col in self.pieces[color]:
            moves = self.calc_moves(self.squares[row][col].piece, row, col)
            for move in moves:
                if self.check_pawn_promotion(self.squares[row][col].piece, move[0]):
                    move = Move(self.squares[row][col].piece, [row, col], move)
                    total_moves.extend(move.make_list_of_promotions())
                else:
                    total_moves.append(Move(self.squares[row][col].piece, [row, col], move))

        return total_moves

    def reset_all_color_moves(self, color):
        for row, col in self.pieces[color]:
            self.squares[row][col].piece.moves = []

    # move functions
    def calc_moves(self, piece, row, col):
        possible_moves = []

        if isinstance(piece, Pawn):
            possible_moves = []
            dir_ = piece.dir

            # captures
            for row_add, col_add in [[dir_, -1], [dir_, 1]]:
                new_row = row + row_add
                new_col = col + col_add
                if ROWS > new_row > -1 and COLS > new_col > -1 and self.squares[new_row][new_col].has_piece():
                    possible_moves.append([new_row,new_col])

            # moving one or two forward
            if row + dir_ != 8 and row + dir_ != -1 and self.squares[row + dir_][col].has_piece() is False:
                possible_moves.append([row + dir_, col])
                # check if at starting point
                if (row * dir_ == 1 or row * dir_ == -6) and self.squares[row + 2 * dir_][col].has_piece() is False:
                    possible_moves.append([row + 2 * dir_, col])

            # check en passant
            ep_row = 4 if piece.color == "black" else 3
            if ep_row == row:
                for new_col in [col + 1, col - 1]:
                    if COLS > new_col > -1:
                        square = self.squares[row][new_col]
                        if isinstance(square.piece, Pawn) and square.piece.enpassantable:
                            possible_moves.append([row + dir_, new_col])

        elif isinstance(piece, Knight):
            possible_moves = self.knights_move(row, col)

        elif isinstance(piece, Bishop):
            possible_moves = self.diagonals(row, col)

        elif isinstance(piece, Rook):
            possible_moves = self.straights(row, col)

        elif isinstance(piece, Queen):
            possible_moves = self.diagonals(row, col) + self.straights(row, col)

        elif isinstance(piece, King):
            possible_moves = self.king_moves_non_castling(row, col)

            # castling
            if piece.moved is False:
                new_row = 0 if piece.color == "black" else 7

                # queenside
                square = self.squares[new_row][0]
                if isinstance(square.piece, Rook) and not square.piece.moved:
                    for new_col in range(1,4):
                        if self.squares[new_row][new_col].has_piece() and (self.in_check(new_row, new_col + 1, piece.color) or new_col == 3):
                            break

                        # passed all piece checks
                        if new_col == 3:
                            possible_moves.append([new_row, 2])

                # kingside
                square = self.squares[new_row][7]
                if isinstance(square.piece, Rook) and not square.piece.moved:
                    for new_col in range(5, 7):
                        if self.squares[new_row][new_col].has_piece() and self.in_check(new_row, new_col - 1, piece.color):
                            break

                        # passed all piece checks
                        if new_col == 6:
                            possible_moves.append([new_row, 6])

        possible_moves = self.filter_same_pieces(possible_moves, piece.color)
        possible_moves = self.filter_king_suicides(piece, row, col, possible_moves)
        piece.moves = possible_moves
        return possible_moves

    # add all diagonals until it hits a roadblock
    def diagonals(self, row, col, ends_only=False):
        possible_moves = []
        ends = []
        for row_add, col_add in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
            cur_row = row + row_add
            cur_col = col + col_add
            while ROWS > cur_row > -1 and COLS > cur_col > -1:
                if self.squares[cur_row][cur_col].has_piece():
                    possible_moves.append([cur_row, cur_col])
                    ends.append([cur_row, cur_col])
                    break
                else:
                    possible_moves.append([cur_row, cur_col])
                    cur_row += row_add
                    cur_col += col_add

        if ends_only:
            return ends
        else:
            return possible_moves

    # add all straights until it hits a roadblock
    def straights(self, row, col, ends_only=False):
        possible_moves = []
        ends = []
        for row_add, col_add in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
            cur_row = row + row_add
            cur_col = col + col_add
            while ROWS > cur_row > -1 and COLS > cur_col > -1:
                if self.squares[cur_row][cur_col].has_piece():
                    possible_moves.append([cur_row, cur_col])
                    ends.append([cur_row, cur_col])
                    break
                else:
                    possible_moves.append([cur_row, cur_col])
                    cur_row += row_add
                    cur_col += col_add
        if ends_only:
            return ends
        else:
            return possible_moves

    def knights_move(self, row, col):
        possible_moves = []
        for a_add, b_add in [[1, 2], [-2, 1], [2, -1], [-1, -2]]:
            possible_moves.append([row + a_add, col + b_add])
            possible_moves.append([row + b_add, col + a_add])

        return self.filter_outside(possible_moves)

    def king_moves_non_castling(self, row, col):
        possible_moves = [[1 + row, 1 + col], [-1 + row, -1 + col]]
        for a_add, b_add in [[1, 0], [1, -1], [-1, 0]]:
            possible_moves.append([row + a_add, col + b_add])
            possible_moves.append([row + b_add, col + a_add])

        return self.filter_outside(possible_moves)

    def get_king_loc(self, color):
        return self.kings[color]

    def king_in_check(self, color):
        return self.in_check(self.kings[color][0], self.kings[color][1], color)

    # checks if a piece is in check
    def in_check(self, row, col, color):

        # check knights squares
        for new_row, new_col in self.knights_move(row, col):
            square = self.squares[new_row][new_col]
            if isinstance(square.piece, Knight) and square.piece.color != color:
                return True

        # check diagonals
        for new_row, new_col in self.diagonals(row, col, True):
            square = self.squares[new_row][new_col]
            if (isinstance(square.piece, Bishop) or isinstance(square.piece, Queen)) and square.piece.color != color:
                return True

        # check diagonals for immediate pawn
        dir_ = -1 if color == "white" else 1
        for new_row, new_col in [[row + dir_, col - 1], [row + dir_, col + 1]]:
            if ROWS > new_row > -1 and COLS > new_col > -1:
                square = self.squares[new_row][new_col]
                if isinstance(square.piece, Pawn) and square.piece.color != color:
                    return True

        # check rooks
        for new_row, new_col in self.straights(row, col, True):
            square = self.squares[new_row][new_col]
            if (isinstance(square.piece, Rook) or isinstance(square.piece, Queen)) and square.piece.color != color:
                return True

        # check surrounding for king
        for new_row, new_col in self.king_moves_non_castling(row, col):
            square = self.squares[new_row][new_col]
            if isinstance(square.piece, King) and square.piece.color != color:
                return True

        # if all that fails return False
        return False


    # filter out moves where you capture your own piece
    def filter_same_pieces(self, moves, color):
        possible_moves = []
        for a, b in moves:
            if self.squares[a][b].has_piece() and self.squares[a][b].same_piece_color(color):
                pass
            else:
                possible_moves.append([a, b])
        return possible_moves

    # filter out moves where you go outside the grid
    def filter_outside(self, moves):
        possible_moves = []
        for new_row, new_col in moves:
            if ROWS > new_row > -1 and COLS > new_col > -1:
                possible_moves.append([new_row, new_col])
        return possible_moves

    # filter our moves where opponent can take your king
    def filter_king_suicides(self, piece, row, col, moves):
        possible_moves = []

        for new_row, new_col in moves:
            new_board = deepcopy(self)
            new_board.make_move(Move(piece,[row, col], [new_row, new_col], False), True)
            if not new_board.in_check(new_board.kings[piece.color][0], new_board.kings[piece.color][1], piece.color):
                possible_moves.append([new_row, new_col])

        return possible_moves

    def other_color(self, color):
        return "white" if color == "black" else "black"

    def convert_board_to_fen(self):
        return_string = ""
        for row in self.squares:
            num_blanks = 0
            for square in row:
                if square.has_piece():
                    if num_blanks != 0:
                        return_string += f"{num_blanks}"
                    return_string += f"{square.piece.code}"
                    num_blanks = 0

                else:
                    num_blanks += 1
            if num_blanks != 0:
                return_string += f"{num_blanks}"
            return_string += "/"

        return return_string

        # extra parts to keep track of if rooks / kings moved
        # return_string += "-"
        # for row, col in [[0,0], [0,4], [0,7], [7,0], [7,4], [7,7]]:
        #     square = self.squares[row][col]
        #     if square.has_piece() and (isinstance(square.piece, Rook) and row + col != 7 or isinstance(square.piece, Rook) and row + col != 7):
        #         return_string += "1"
        #     else:
        #         return_string += "0"
        # return return_string

    # innit functions
    def _create(self):
        self.squares = [[None for _ in range(COLS)] for __ in range(ROWS)]
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces_fen(self, fen):
        cur_row = 0
        for row in fen.split("/"):
            cur_col = 0
            for char in row:
                if char.isnumeric():
                    cur_col += int(char)
                else:
                    color = "white" if char.isupper() else "black"
                    new_piece = []
                    if char.lower() == "p":
                        new_piece = Pawn(color)
                    elif char.lower() == "b":
                        new_piece = Bishop(color)
                    elif char.lower() == "n":
                        new_piece = Knight(color)
                    elif char.lower() == "r":
                        new_piece = Rook(color)
                    elif char.lower() == "q":
                        new_piece = Queen(color)
                    elif char.lower() == "k":
                        new_piece = King(color)
                        self.kings[color] = [cur_row, cur_col]

                    self.squares[cur_row][cur_col] = Square(cur_row, cur_col, new_piece)
                    self.pieces[color].append([cur_row, cur_col])
                    cur_col += 1
            cur_row += 1

