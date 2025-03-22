from src.const import *
from src.square import Square
from src.piece import *
from src.move import Move

class Board:

    # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR standard
    def __init__(self, fen= "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", destroy_matt=False):
        self.squares = []
        self.legal_moves = []
        self.turn = "white"

        # dict of 2 lists of piece locations (one for each color)
        self.pieces = dict()
        self.pieces["white"] = []
        self.pieces["black"] = []
        self.pieces_left = 0

        # dict of king locations
        self.kings = dict()
        self.kings["white"] = []
        self.kings["black"] = []

        self.castled = [0,0]
        self.in_check_var = False
        self.last_move = [[-1, -1,], [-1, -1]]

        # used for 50 move rule
        self.uneventful_moves = 0

        # create board
        self._create()
        self._add_pieces_fen(fen)

        # destroying matt
        self.destroy_matt = destroy_matt

    # moves a piece
    def make_move(self, move, testing= False):

        piece = move.piece
        row = move.start[0]
        col = move.start[1]
        new_row = move.end[0]
        new_col = move.end[1]

        self.turn = "black" if self.turn == "white" else "white"

        move.castle_rights = [row[:] for row in self.castle_rights]

        # add 1 to moves counter
        self.uneventful_moves += 1

        # if enpassant, remove capture from squares
        if move.en_passant_occur:
            self.squares[new_row - piece.dir][new_col].piece = None

        # remove captures from pieces dict and reset move counter
        if self.is_capture(move):
            self.pieces_left -= 1
            if not testing:
                self.uneventful_moves = 0

                # en passant
                if move.en_passant_occur:
                    self.pieces[piece.other_color()].remove([new_row - piece.dir, new_col])

                # normal
                else:
                    self.pieces[piece.other_color()].remove([new_row, new_col])

        # castling
        if move.castling:

            # update castled
            self.castled[row // 7] = 1

            # decide which way to castle
            rook_loc = [7, 5] if new_col - col == 2 else [0, 3]

            # remove and put rooks in correct positions
            self.squares[row][rook_loc[0]].piece = None
            self.squares[new_row][rook_loc[1]].piece = Rook(piece.color)
            if not testing:
                self.pieces[piece.color].remove([row, rook_loc[0]])
                self.pieces[piece.color].append([new_row, rook_loc[1]])

        # promotions
        elif move.promotion is not None:
            new_piece = None

            # decide what the new piece is
            if move.promotion == "queen":
                new_piece = Queen(piece.color)
            elif move.promotion == "rook":
                new_piece = Rook(piece.color)
            elif move.promotion == "bishop":
                new_piece = Bishop(piece.color)
            elif move.promotion == "knight":
                new_piece = Knight(piece.color)

            piece = new_piece

        # get rid of original piece and add new_piece
        self.squares[row][col].piece = None
        self.squares[new_row][new_col].piece = piece
        if not testing:
            self.pieces[piece.color].remove([row, col])
            self.pieces[piece.color].append([new_row, new_col])

        # update king location and castle rights
        if isinstance(piece, King):
            self.kings[piece.color] = [new_row, new_col]
            self.castle_rights[0 if piece.color == "white" else 1] = [0,0]

        # update castling rights
        elif isinstance(piece, Rook):
            check_row = 0 if piece.color == "black" else 7
            if col == 0 and row == check_row:
                self.castle_rights[0 if piece.color == "white" else 1][0] = 0
            elif col == 7 and row == check_row:
                self.castle_rights[0 if piece.color == "white" else 1][1] = 0

        # reset uneventful_moves
        elif isinstance(piece, Pawn):
            self.uneventful_moves = 0

        # reset last piece moved
        self.last_move = [[row, col], [new_row, new_col]]

        # check if other kings in check
        if self.king_in_check(piece.other_color()):
            self.in_check_var = piece.other_color()
        else:
            self.in_check_var = None

    def undo_move(self, move, testing=False):

        piece = move.piece
        row = move.start[0]
        col = move.start[1]
        new_row = move.end[0]
        new_col = move.end[1]

        self.turn = "black" if self.turn == "white" else "white"

        # subtract 1 to moves counter < note might not be correct (fix later)
        self.uneventful_moves -= 1

        # promotions
        if move.promotion is not None:
            piece = Pawn(piece.color)

        # get rid of original piece and add new_piece
        self.squares[row][col].piece = piece
        self.squares[new_row][new_col].piece = None
        if not testing:
            self.pieces[piece.color].append([row, col])
            self.pieces[piece.color].remove([new_row, new_col])

        # add captures and reset move counter
        if self.is_capture(move):
            self.uneventful_moves = 0
            self.pieces_left += 1

            # en passant
            if move.en_passant_occur:
                self.squares[new_row - piece.dir][new_col].piece = move.piece_taken
                if not testing:
                    self.pieces[piece.other_color()].append([new_row - piece.dir, new_col])

            # normal
            else:
                self.squares[new_row][new_col].piece = move.piece_taken
                if not testing:
                    self.pieces[piece.other_color()].append([new_row, new_col])

        # castling
        if move.castling:

            # update castled
            self.castled[row // 7] = 0

            # decide which way we castled
            rook_loc = [7, 5] if new_col - col == 2 else [0, 3]

            # remove and put rooks in correct positions
            self.squares[new_row][rook_loc[1]].piece = None
            self.squares[new_row][rook_loc[0]].piece = Rook(piece.color)
            if not testing:
                self.pieces[piece.color].remove([row, rook_loc[1]])
                self.pieces[piece.color].append([new_row, rook_loc[0]])

        # update king location and castle rights
        if isinstance(piece, King):
            self.kings[piece.color] = [row, col]

        self.castle_rights = [row[:] for row in move.castle_rights]

        # reset last piece moved
        self.last_move = move.last_move

        # check if other kings in check
        if self.king_in_check(piece.other_color()):
            self.in_check_var = piece.other_color()
        else:
            self.in_check_var = None

    # gets a move from start and end locations, returns None is none found
    def get_move(self, start, end):
        for move in self.legal_moves:
            if move.start == start and move.end == end:
                return move

        return None

    # checks if a move is a capture
    def is_capture(self, move):
        return move.piece_taken is not None

    # checks if a pawn promotion will occur
    def check_pawn_promotion(self, piece, new_row) -> bool:
        return isinstance(piece, Pawn) and (new_row == 0 or new_row == 7)

    # if there are no legal moves and the kings in check, its checkmate
    def check_checkmate(self):
        return True if self.king_in_check(self.turn) and not self.legal_moves else False

    # if there are no legal moves and the king is not in check, its stalemate
    def check_stalemate(self):
        return True if not self.king_in_check(self.turn) and not self.legal_moves else False

    # updates legal moves to self and returns legal moves
    def add_all_moves(self, color):
        self.legal_moves = []
        for piece_loc in self.pieces[color]:
            row, col = piece_loc
            self.legal_moves.extend(self.calc_moves(row, col))

        if self.destroy_matt and color == "black":
            self.legal_moves.append(Move(self.squares[0][4].piece, [0, 4], [7, 4], self.squares[7][4].piece,
                                                       False, self.last_move, False,
                                                       None))

        return self.legal_moves

    # move functions
    def calc_moves(self, row, col):
        possible_moves = []
        possible_move_loc = []
        piece = self.squares[row][col].piece
        last_move = self.last_move

        if isinstance(piece, Pawn):
            dir_ = piece.dir

            # used for checking captures in en passant case
            flags = [0,0]

            # captures
            for row_add, col_add, flag in [[dir_, 1, 0], [dir_, -1, 1]]:
                new_row = row + row_add
                new_col = col + col_add
                if ROWS > new_row > -1 and COLS > new_col > -1:
                    piece_taken = self.squares[new_row][new_col].piece
                    if piece_taken is not None and piece_taken.color != piece.color:
                        flags[flag] = 1
                        promotion = self.check_pawn_promotion(piece, new_row)
                        move = Move(piece, [row, col], [new_row, new_col], piece_taken,
                                                       False, last_move, False,
                                                       None)
                        if promotion:
                            possible_moves.extend(move.make_list_of_promotions())
                        else:
                            possible_moves.append(move)

            # moving one or two forward
            if row + dir_ != 8 and row + dir_ != -1 and self.squares[row + dir_][col].has_piece() is False:
                promotion = self.check_pawn_promotion(piece, new_row)
                move = Move(piece, [row, col], [row + dir_, col], None,
                                           False, last_move, False,
                                           None)
                if promotion:
                    possible_moves.extend(move.make_list_of_promotions())
                else:
                    possible_moves.append(move)

                # check if at starting point
                if (row * dir_ == 1 or row * dir_ == -6) and self.squares[row + 2 * dir_][col].has_piece() is False:
                    possible_moves.append(Move(piece, [row, col], [row + 2 * dir_, col], None,
                                               False, last_move, False,
                                               None))

            # check en passant
            ep_row = 4 if piece.color == "black" else 3
            if ep_row == row:
                for new_col, flag_check in [[col + 1, 0], [col - 1, 1]]:
                    if COLS > new_col > -1 and flags[flag_check] == 0 and abs(self.last_move[0][0] - self.last_move[1][0]) == 2:
                        square = self.squares[row][new_col]
                        if isinstance(square.piece, Pawn) and self.last_move[1][1] == new_col and self.last_move[1][0] == row:
                            possible_moves.append(Move(piece, [row, col], [row + dir_, new_col], square.piece,
                                                       False, last_move, True,
                                                       None))

        elif isinstance(piece, Knight):
            possible_move_loc = self.knights_move(row, col)

        elif isinstance(piece, Bishop):
            possible_move_loc = self.diagonals(row, col)

        elif isinstance(piece, Rook):
            possible_move_loc = self.straights(row, col)

        elif isinstance(piece, Queen):
            possible_move_loc = self.diagonals(row, col) + self.straights(row, col)

        elif isinstance(piece, King):
            possible_move_loc = self.king_moves_non_castling(row, col)
            possible_move_loc = self.filter_same_pieces(possible_move_loc, piece.color)

            for move in possible_move_loc:
                piece_taken = self.squares[move[0]][move[1]].piece
                move = Move(piece, [row, col], move, piece_taken,
                                           False, last_move, False,
                                           None)
                possible_moves.append(move)

            # castling
            # queenside
            new_row = 7 if piece.color == "white" else 0
            check_rook = self.squares[new_row][0].piece

            if self.castle_rights[0 if piece.color == "white" else 1][0] == 1 and isinstance(check_rook, Rook) and check_rook.color == piece.color:
                for new_col in range(1,4):
                    if self.squares[new_row][new_col].has_piece() or (self.in_check(new_row, new_col + 1, piece.color) and new_col != 1):
                        break

                    # passed all piece checks
                    if new_col == 3:
                        move = Move(piece, [row, col], [new_row, 2], None,
                                    True, last_move, False,
                                    None)
                        possible_moves.append(move)

            # kingside
            check_rook = self.squares[new_row][7].piece
            if self.castle_rights[0 if piece.color == "white" else 1][1] == 1 and isinstance(check_rook, Rook) and check_rook.color == piece.color:
                for new_col in range(5, 7):
                    if self.squares[new_row][new_col].has_piece() or self.in_check(new_row, new_col - 1, piece.color):
                        break

                    # passed all piece checks
                    if new_col == 6:
                        move = Move(piece, [row, col], [new_row, 6], None,
                                    True, last_move, False,
                                    None)
                        possible_moves.append(move)

        # transform potential locations to moves
        if not isinstance(piece, Pawn) and not isinstance(piece, King):
            possible_move_loc = self.filter_same_pieces(possible_move_loc, piece.color)
            for move in possible_move_loc:
                piece_taken = self.squares[move[0]][move[1]].piece
                move = Move(piece, [row, col], move, piece_taken,
                                           False, last_move, False,
                                           None)
                possible_moves.append(move)

        possible_moves = self.filter_king_suicides(possible_moves)
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
    def filter_outside(self, move_locs):
        possible_move_loc = []
        for new_row, new_col in move_locs:
            if ROWS > new_row > -1 and COLS > new_col > -1:
                possible_move_loc.append([new_row, new_col])
        return possible_move_loc

    # filter our moves where opponent can take your king
    def filter_king_suicides(self, moves):
        possible_moves = []

        for move in moves:
            self.make_move(move, True)
            color = move.piece.color
            if not self.in_check(self.kings[color][0], self.kings[color][1], color):
                possible_moves.append(move)
            self.undo_move(move, True)

        return possible_moves

    def other_color(self, color):
        return "white" if color == "black" else "black"

    def other_turn(self):
        return "black" if self.turn == "white" else "white"

    def convert_board_to_fen(self):
        substrings = []
        for row in self.squares:
            num_blanks = 0
            for square in row:
                if square.has_piece():
                    if num_blanks != 0:
                        substrings.append(f"{num_blanks}")
                    substrings.append(f"{square.piece.code}")
                    num_blanks = 0

                else:
                    num_blanks += 1
            if num_blanks != 0:
                substrings.append(f"{num_blanks}")

        return "".join(substrings)

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
                    self.pieces_left += 1
                    cur_col += 1
            cur_row += 1

        # castle rights if not given
        self.castle_rights = [[1, 1], [1, 1]]
        for row, col, color in [[0, 0, 1], [0, 7, 1], [7, 0, 0], [7, 7, 0]]:
            if not isinstance(self.squares[row][col].piece, Rook):
                self.castle_rights[color][int(col / 7)] = 0

        for row, col, color in [[0, 4, 1], [7, 4, 0]]:
            if not isinstance(self.squares[row][col].piece, King):
                self.castle_rights[color] = [0, 0]
