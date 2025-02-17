import os

class Piece:

    def __init__(self, name, color, value, code, image=None, image_rect=None):
        self.name = name
        self.color = color

        value_sign = 1 if color == "white" else -1
        self.value = value * value_sign
        self.moves = []
        self.moved = False
        self.image = image
        self.set_image()
        self.image_rect = image_rect

        if color == "white":
            self.code = code.upper()
        else:
            self.code = code

    def set_image(self, size=80):
        self.image = os.path.join(
            f"../assets/images/imgs-{size}px/{self.color}_{self.name}.png"
        )

    def set_possible_moves(self, moves):
        self.moves = moves

    def other_color(self):
        return "black" if self.color == "white" else "white"

class Pawn(Piece):

    def __init__(self, color):
        self.dir = -1 if color == "white" else 1
        self.enpassantable = False
        super().__init__("pawn", color, 1.0, "p")

class Knight(Piece):

    def __init__(self, color):
        super().__init__("knight", color, 3.0, "n")

class Bishop(Piece):

    def __init__(self, color):
        super().__init__("bishop", color, 3.1, "b")

class Rook(Piece):

    def __init__(self, color):
        super().__init__("rook", color, 5.0, "r")

class Queen(Piece):

    def __init__(self, color):
        super().__init__("queen", color, 9.0, "q")

class King(Piece):

    def __init__(self, color):
        super().__init__("king", color, 10000.0, "k")