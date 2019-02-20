import pygame


class Ship(pygame.sprite.Sprite):
    def __init__(self, ai_settings, screen):
        """Initialize ship and set starting position"""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        # Load ship image and set rect attributes
        self.ship_image = pygame.image.load('images/pikachu.v1.png')
        self.image = self.ship_image
        self.death_images = [
            pygame.image.load('images/ship_death/ship_death1.png'),
            pygame.image.load('images/ship_death/ship_death2.png'),
            pygame.image.load('images/ship_death/ship_death3.png'),
            pygame.image.load('images/ship_death/ship_death4.png'),
            pygame.image.load('images/ship_death/ship_death5.png'),
            pygame.image.load('images/ship_death/ship_death6.png'),
            pygame.image.load('images/ship_death/ship_death7.png'),
            pygame.image.load('images/ship_death/ship_death8.png')
        ]
        self.death_index = None
        self.last_frame = None
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        # sound
        self.ship_death_sound = pygame.mixer.Sound('sounds/pikachu-dying.wav')
        self.ship_shoot = pygame.mixer.Sound('sounds/puika.wav')
        self.ship_death_sound.set_volume(0.5)
        self.ship_shoot.set_volume(0.5)
        self.channel = ai_settings.ship_channel
        # Moving status flags
        self.moving_right = False
        self.moving_left = False
        # Store center as decimal
        self.center = float(self.rect.centerx)
        self.dead = False

    def fire_weapon(self):
        """Play the audio for the ship firing its weapon"""
        self.channel.play(self.ship_shoot)

    def update(self):
        """Update ship's position based on moving state"""
        # Move right/left based on moving status flags, unless the ship is at the edge of the screen
        if not self.dead:
            if self.moving_right and self.rect.right < self.screen_rect.right:
                self.center += self.ai_settings.ship_speed_factor
            if self.moving_left and self.rect.left > 0:
                self.center -= self.ai_settings.ship_speed_factor

            self.rect.centerx = self.center
        else:
            time_test = pygame.time.get_ticks()
            if abs(time_test - self.last_frame) > 250:
                self.death_index += 1
                if self.death_index < len(self.death_images):
                    self.image = self.death_images[self.death_index]
                    self.last_frame = time_test
                else:
                    self.dead = False
                    self.image = self.ship_image

    def center_ship(self):
        """Center the ship on the screen"""
        self.center = self.screen_rect.centerx

    def death(self):
        """Switch ship to death image briefly and pause"""
        self.dead = True
        self.death_index = 0
        self.image = self.death_images[self.death_index]
        self.last_frame = pygame.time.get_ticks()
        self.channel.play(self.ship_death_sound)

    def blitme(self):
        self.screen.blit(self.image, self.rect)
