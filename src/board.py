from const import *
from square import Square
from piece import *
from copy import deepcopy

class Board:

    def __init__(self):
        self.squares = []

        # dict of 2 lists of piece locations (one for each color)
        self.pieces = dict()
        self.pieces["white"] = []
        self.pieces["black"] = []

        # dict of king locations
        self.kings = dict()
        self.kings["white"] = [7, 4]
        self.kings["black"] = [0, 4]

        self.in_check_var = False
        self.last_piece_moved = None

        self._create()
        self._add_piece("white")
        self._add_piece("black")

    # moves a piece
    def make_move(self, piece, row, col, new_row, new_col, promotion=None, testing=False):

        self.squares[row][col].piece = None
        self.pieces[piece.color].remove([row, col])

        # remove captures (not en passant) (in different location)
        if self.is_capture(piece, new_row, new_col):
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
            if square.has_piece() and square.piece.color != piece.color and isinstance(square.piece, Pawn):
                square.piece.enpassantable = False

        self.last_piece_moved = [new_row, new_col]

        # check if other kings in check
        if self.king_in_check(piece.other_color()):
            self.in_check_var = piece.other_color()
        else:
            self.in_check_var = None

    # checks if a move is valid
    def valid_move(self, piece, new_row, new_col) -> bool:
        if not piece.moves:
            return False
        else:
            return [new_row, new_col] in piece.moves

    def is_capture(self, piece, new_row, new_col):
        square = self.squares[new_row][new_col]
        if square.has_piece() and square.piece.color != piece.color:
            return True
        else:
            return False

    # checks if a pawn promotion will occur
    def check_pawn_promotion(self, piece, new_row) -> bool:
        return isinstance(piece, Pawn) and (new_row == 0 or new_row == 7)

    # if there are no legal moves, its checkmate
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
            if moves:
                total_moves.append([[row, col], moves])

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
                if piece.moved is False and self.squares[row + 2 * dir_][col].has_piece() is False:
                    possible_moves.append([row + 2 * dir_, col])

            # check en passant
            ep_row = 4 if piece.color == "black" else 3
            if ep_row == row:
                for new_col in [col + 1, col - 1]:
                    if COLS > new_col > -1:
                        square = self.squares[row][new_col]
                        if square.has_piece() and isinstance(square.piece, Pawn) and square.piece.enpassantable:
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
            possible_moves = [[1 + row ,1 + col], [-1 + row, -1 + col]]
            for a_add, b_add in [[1,0], [1, -1], [-1, 0]]:
                possible_moves.append([row + a_add, col + b_add])
                possible_moves.append([row + b_add, col + a_add])
            possible_moves = self.filter_outside(possible_moves)

            # castling
            if piece.moved is False:
                new_row = 0 if piece.color == "black" else 7

                # queenside
                square = self.squares[new_row][0]
                if square.has_piece() and isinstance(square.piece, Rook) and not square.piece.moved:
                    for new_col in range(1,4):
                        if self.squares[new_row][new_col].has_piece():
                            break

                        # passed all piece checks
                        if new_col == 3:
                            possible_moves.append([new_row, 2])

                # kingside
                square = self.squares[new_row][7]
                if square.has_piece() and isinstance(square.piece, Rook) and not square.piece.moved:
                    for new_col in range(5, 7):
                        if self.squares[new_row][new_col].has_piece():
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

    def get_king_loc(self, color):
        return self.kings[color]

    def king_in_check(self, color):
        return self.in_check(self.kings[color][0], self.kings[color][1], color)

    # checks if a piece is in check
    def in_check(self, row, col, color):

        # check knights squares
        for new_row, new_col in self.knights_move(row, col):
            square = self.squares[new_row][new_col]
            if square.has_piece() and isinstance(square.piece, Knight) and square.piece.color != color:
                return True

        # check diagonals
        for new_row, new_col in self.diagonals(row, col, True):
            square = self.squares[new_row][new_col]
            if square.has_piece() and (isinstance(square.piece, Bishop) or isinstance(square.piece, Queen)) and square.piece.color != color:
                return True

        # check diagonals for immediate pawn
        dir_ = -1 if color == "white" else 1
        for new_row, new_col in [[row + dir_, col - 1], [row + dir_, col + 1]]:
            if ROWS > new_row > -1 and COLS > new_col > -1:
                square = self.squares[new_row][new_col]
                if square.has_piece() and isinstance(square.piece, Pawn) and square.piece.color != color:
                    return True

        # check rooks
        for new_row, new_col in self.straights(row, col, True):
            square = self.squares[new_row][new_col]
            if square.has_piece() and (isinstance(square.piece, Rook) or isinstance(square.piece, Queen)) and square.piece.color != color:
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
            new_board.make_move(piece, row, col, new_row, new_col, False,True)
            if not new_board.in_check(new_board.kings[piece.color][0], new_board.kings[piece.color][1], piece.color):
                possible_moves.append([new_row, new_col])

        return possible_moves

    # innit functions
    def _create(self):
        self.squares = [[None for _ in range(COLS)] for __ in range(ROWS)]
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_piece(self, color):
        row_pawn, row_other = (6,7) if color == "white" else (1,0)

        for col in range(COLS):
            for row in [row_pawn, row_other]:
                self.pieces[color].append([row, col])

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        for col in [1,6]:
            self.squares[row_other][col] = Square(row_other, col, Knight(color))

        # bishops
        for col in [2, 5]:
            self.squares[row_other][col] = Square(row_other, col, Bishop(color))

        # rooks
        for col in [0, 7]:
            self.squares[row_other][col] = Square(row_other, col, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color))

