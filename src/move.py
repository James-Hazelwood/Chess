
class Move:

    def __init__(self, piece, start, end, piece_taken=None, castling=False, last_move=None,
                 en_passant_occur=False, promotion=None):
        self.piece = piece
        self.start = start
        self.end = end
        self.piece_taken = piece_taken
        self.castling = castling

        # this gets updated by move, not input
        self.castle_rights = None

        self.last_move = last_move
        self.en_passant_occur = en_passant_occur
        self.promotion = promotion

    def make_list_of_promotions(self):
        return_list = []
        for piece in ["knight", "bishop", "rook", "queen"]:
            return_list.append(Move(self.piece, self.start, self.end, self.piece_taken, self.castling,
                                    self.last_move, self.en_passant_occur,  piece))

        return return_list

    def make_move_readable(self):
        return_str = ""
        for num1, num2 in [self.start, self.end]:
            return_str += f"{chr(97 + num2)}{8 - num1}"

        if self.promotion is not None:
            if self.promotion == "knight":
                return_str += "n"
            elif self.promotion == "bishop":
                return_str += "b"
            elif self.promotion == "rook":
                return_str += "r"
            elif self.promotion == "queen":
                return_str += "q"

        return return_str