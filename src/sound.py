import pygame
import os

class Sound:

    def __init__(self):
        self.move_sfx = pygame.mixer.Sound(os.path.join("../assets/sounds/move.wav"))
        self.capture_sfx = pygame.mixer.Sound(os.path.join("../assets/sounds/capture.wav"))

    def move_sound(self):
        self.move_sfx.play()

    def capture_sound(self):
        self.capture_sfx.play()
