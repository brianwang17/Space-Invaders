import pygame
from pygame.sysfont import SysFont
from random import choice


class Ufo(pygame.sprite.Sprite):
    """Represents a UFO meant to move across the screen at random intervals"""
    def __init__(self, ai_settings, screen, sound=True):
        super().__init__()
        # screen, settings, score values
        self.screen = screen
        self.ai_settings = ai_settings
        self.possible_scores = ai_settings.ufo_point_values
        self.score = None

        # images, score text
        self.image = pygame.image.load('images/ufo.png')
        self.rect = self.image.get_rect()
        self.score_image = None
        self.font = SysFont(None, 32, italic=True)
        self.prep_score()

        # death frames
        self.death_frames = []
        self.death_index = None
        self.death_frames.append(pygame.image.load('images/ufo-death.png'))
        self.death_frames.append(self.score_image)
        self.last_frame = None
        self.wait_interval = 500

        # sound
        self.entrance_sound = pygame.mixer.Sound('sounds/ufo-sound.wav')
        self.death_sound = pygame.mixer.Sound('sounds/ufo-death.wav')
        self.entrance_sound.set_volume(0.6)
        self.channel = ai_settings.ufo_channel

        # initial position, speed/direction
        self.speed = ai_settings.ufo_speed * (choice([-1, 1]))
        self.rect.x = 0 if self.speed > 0 else ai_settings.screen_width
        self.rect.y = ai_settings.screen_height * 0.1

        # death flag
        self.dead = False

        if sound:
            self.channel.play(self.entrance_sound, loops=-1)

    def kill(self):
        self.channel.stop()
        super().kill()

    def begin_death(self):
        self.channel.stop()
        self.channel.play(self.death_sound)
        self.dead = True
        self.death_index = 0
        self.image = self.death_frames[self.death_index]
        self.last_frame = pygame.time.get_ticks()

    def get_score(self):
        """Get a random score from the UFO's possible score values"""
        self.score = choice(self.possible_scores)
        return self.score

    def prep_score(self):
        score_str = str(self.get_score())
        self.score_image = self.font.render(score_str, True, (255, 0, 0), self.ai_settings.intro_bg_color)

    def update(self):
        if not self.dead:
            self.rect.x += self.speed
            if self.speed > 0 and self.rect.left > self.ai_settings.screen_width:
                self.kill()
            elif self.rect.right < 0:
                self.kill()
        else:
            time_test = pygame.time.get_ticks()
            if abs(time_test - self.last_frame) > self.wait_interval:
                self.last_frame = time_test
                self.death_index += 1
                if self.death_index >= len(self.death_frames):
                    self.kill()
                else:
                    self.image = self.death_frames[self.death_index]
                    self.wait_interval += 500

    def blitme(self):
        self.screen.blit(self.image, self.rect)
