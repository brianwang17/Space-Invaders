import pygame


class Bullet(pygame.sprite.Sprite):
    """Manages bullets fired from a ship"""
    def __init__(self, ai_settings, screen, ship):
        """Create a bullet object at the given ship's current position."""
        super().__init__()
        self.screen = screen
        # Create bullet at (0, 0) then set to correct position
        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width, ai_settings.bullet_height)
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top
        # Store bullet's position as a decimal value
        self.y = float(self.rect.y)

        self.color = ai_settings.bullet_color
        self.speed_factor = ai_settings.bullet_speed_factor

    def update(self):
        """Move bullet up the screen"""
        self.y -= self.speed_factor
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw bullet on the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)
