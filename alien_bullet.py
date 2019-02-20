import pygame


class AlienBullet(pygame.sprite.Sprite):
    """Manages alien bullets fired from aliens"""
    def __init__(self, ai_settings, screen, alien):
        super().__init__()
        self.screen = screen

        # Initialize alien bullet image and related variables
        # self.image = pygame.image.load('images/alien_beam_resized.png')
        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width, ai_settings.bullet_height)
        self.rect.centerx = alien.rect.centerx
        self.rect.top = alien.rect.top

        # Y position and speed factor
        self.y = float(self.rect.y)
        self.color = ai_settings.alien_bullet_color
        self.speed_factor = ai_settings.alien_bullet_speed_factor

    def update(self):
        """Move the beam down the screen"""
        self.y += self.speed_factor
        self.rect.y = self.y

    def draw_alien_bullet(self):
        """Draw the beam on the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)
