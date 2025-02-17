
class Move:

    def __init__(self, piece, start, end, promotion= None):
        self.piece = piece
        self.start = start
        self.end = end
        self.promotion = promotion

    def check_valid(self):
        return [self.end[0], self.end[1]] in self.piece.moves

    def make_list_of_promotions(self):
        return_list = []
        for piece in ["knight", "bishop", "rook", "queen"]:
            return_list.append(Move(self.piece, self.end, self.start, piece))

        return return_list