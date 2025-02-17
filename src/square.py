
class Square:

    def __init__(self, row, col, piece = None):
        self.row = row
        self.col = col
        self.piece = piece

    def has_piece(self):
        return self.piece is not None

    def same_piece_color(self, color):
        return self.piece.color == color

    def dif_piece_color(self, color):
        return self.piece.color != color