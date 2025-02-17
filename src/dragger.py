import pygame

class Dragger:

    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.dragging = False
        self.piece = None
        self.initial_row = -1
        self.initial_col = -1

    # blit methods
    def update_blit(self, surface):
        img = pygame.image.load(self.piece.image)
        img_center = self.mouse_x, self.mouse_y
        self.piece.image_rect = img.get_rect(center=img_center)
        surface.blit(img, self.piece.image_rect)

    # other methods
    def update_mouse(self, pos):
        self.mouse_x, self.mouse_y = pos

    def save_initial(self, clicked_row, clicked_col, piece):
        self.initial_row = clicked_row
        self.initial_col = clicked_col
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False
        self.initial_row = -1
        self.initial_col = -1

    def get_initial_loc(self):
        return self.initial_row, self.initial_col