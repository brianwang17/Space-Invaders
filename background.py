import pygame

from pygame import *


class Background(sprite.Sprite):
    def __init__(self, image_file, location, screen):
        super().__init__()
        self.screen = screen
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

    def blitme(self):
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.image, self.rect)
