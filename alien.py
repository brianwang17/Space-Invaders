import pygame


class Alien(pygame.sprite.Sprite):
    """Represents a single alien in the fleet"""
    def __init__(self, ai_settings, screen, alien_type=3):
        """Initialize alien and set starting position"""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        self.alien_type = alien_type

        # Load alien image and set rect attribute
        self.images = None
        self.image = None
        self.image_index = None
        self.death_index = None
        self.last_frame = None
        self.death_frames = None
        self.rect = None
        self.initialize_images()

        # sound
        self.death_sound = pygame.mixer.Sound('sounds/alien_death.wav')
        self.fire_sound = pygame.mixer.Sound('sounds/alien_shoot.wav')
        self.death_sound.set_volume(0.4)
        self.fire_sound.set_volume(0.4)
        self.channel = ai_settings.alien_channel

        # Start new aliens at top left of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store alien's exact position
        self.x = float(self.rect.x)

        # Killed flag
        self.dead = False

    def fire_weapon(self):
        """Play the audio for the alien firing its weapon"""
        self.channel.play(self.fire_sound)

    def initialize_images(self):
        if self.alien_type == 1:
            self.images = [
                pygame.image.load('images/alien1_1.png'),
                pygame.image.load('images/alien1_2.png')
            ]
            self.death_frames = [
                pygame.image.load('images/alien_death/alien_purple_death1.png'),
                pygame.image.load('images/alien_death/alien_purple_death2.png'),
                pygame.image.load('images/alien_death/alien_purple_death3.png'),
                pygame.image.load('images/alien_death/alien_purple_death4.png')
            ]
        elif self.alien_type == 2:
            self.images = [
                pygame.image.load('images/alien2_1.png'),
                pygame.image.load('images/alien2_2.png')
            ]
            self.death_frames = [
                pygame.image.load('images/alien_death/alien_blue_death1.png'),
                pygame.image.load('images/alien_death/alien_blue_death2.png'),
                pygame.image.load('images/alien_death/alien_blue_death3.png'),
                pygame.image.load('images/alien_death/alien_blue_death4.png')
            ]
        else:
            self.images = [
                pygame.image.load('images/alien3_1.png'),
                pygame.image.load('images/alien3_2.png')
            ]
            self.death_frames = [
                pygame.image.load('images/alien_death/alien_green_death1.png'),
                pygame.image.load('images/alien_death/alien_green_death2.png'),
                pygame.image.load('images/alien_death/alien_green_death3.png'),
                pygame.image.load('images/alien_death/alien_green_death4.png')
            ]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.last_frame = pygame.time.get_ticks()

    def check_edges(self):
        """Return True if alien is at edge of screen"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True
        else:
            return False

    def begin_death(self):
        """Set alien's death flag and begin death animation"""
        self.dead = True
        self.death_index = 0
        self.image = self.death_frames[self.death_index]
        self.last_frame = pygame.time.get_ticks()
        self.channel.play(self.death_sound)

    def update(self):
        """Move alien to the right or left, play idle animations or death animations"""
        self.x += (self.ai_settings.alien_speed_factor * self.ai_settings.fleet_direction)
        self.rect.x = self.x
        time_test = pygame.time.get_ticks()
        if not self.dead:
            if abs(self.last_frame - time_test) > 1000:
                self.last_frame = time_test
                self.image_index = (self.image_index + 1) % len(self.images)   # Loop over frames
                self.image = self.images[self.image_index]
        else:
            if abs(self.last_frame - time_test) > 20:   # At least 20 millisecond delay between frames
                self.last_frame = time_test     # Delay should ensure animation is perceivable at high fps
                self.death_index += 1
                if self.death_index >= len(self.death_frames):
                    self.kill()
                else:
                    self.image = self.death_frames[self.death_index]

    def blitme(self):
        """Draw alien at its current location"""
        self.screen.blit(self.image, self.rect)
