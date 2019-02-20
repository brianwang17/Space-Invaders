from pygame.font import Font
from pygame import display, time, image
from pygame import mixer


class Button:
    """Represents a click-able button style text, with altering text color"""
    def __init__(self, settings, screen, msg, y_factor=0.65):
        self.settings = settings
        self.screen = screen
        self.screen_rect = screen.get_rect()

        # Dimensions and properties of the button
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.alt_color = (0, 255, 0)
        self.font = Font('fonts/space_invaders.ttf', 48)
        self.y_factor = y_factor

        # Prep button message
        self.msg = msg
        self.msg_image, self.msg_image_rect = None, None
        self.prep_msg(self.text_color)

    def check_button(self, mouse_x, mouse_y):
        """Check if the given button has been pressed"""
        if self.msg_image_rect.collidepoint(mouse_x, mouse_y):
            return True
        else:
            return False

    def alter_text_color(self, mouse_x, mouse_y):
        """Change text color if the mouse coordinates collide with the button"""
        if self.check_button(mouse_x, mouse_y):
            self.prep_msg(self.alt_color)
        else:
            self.prep_msg(self.text_color)

    def prep_msg(self, color):
        """Turn msg into a rendered image and center it on the button"""
        self.msg_image = self.font.render(self.msg, True, color, self.settings.intro_bg_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.centerx = (self.settings.screen_width // 2)
        self.msg_image_rect.centery = int(self.settings.screen_height * self.y_factor)

    def draw_button(self):
        """blit message to the screen"""
        self.screen.blit(self.msg_image, self.msg_image_rect)


class EnemyDisplay:
    def __init__(self, ai_settings, screen, y_start):
        self.screen = screen
        self.settings = ai_settings
        self.aliens = []
        images = [
            image.load('images/alien1_1.png'),
            image.load('images/alien2_1.png'),
            image.load('images/alien3_1.png'),
            image.load('images/ufo.png')
        ]
        for img in images:
            self.aliens.append((img, img.get_rect()))
        self.example_scores = [
            Subtitle(ai_settings.intro_bg_color, self.screen, ' = ' + str(ai_settings.alien_points['1']),
                     text_color=(255, 255, 255)),
            Subtitle(ai_settings.intro_bg_color, self.screen, ' = ' + str(ai_settings.alien_points['2']),
                     text_color=(255, 255, 255)),
            Subtitle(ai_settings.intro_bg_color, self.screen, ' = ' + str(ai_settings.alien_points['3']),
                     text_color=(255, 255, 255)),
            Subtitle(ai_settings.intro_bg_color, self.screen, ' = ???', text_color=(255, 255, 255))
        ]
        self.score_images = []
        self.y_start = y_start
        self.prep_images()

    def prep_images(self):
        y_offset = self.y_start
        for a, es in zip(self.aliens, self.example_scores):
            a[1].centery = y_offset
            a[1].centerx = (self.settings.screen_width // 2) - a[1].width
            es.prep_image()
            es.image_rect.centery = y_offset
            es.image_rect.centerx = (self.settings.screen_width // 2) + a[1].width
            y_offset += int(a[1].height * 1.5)

    def show_examples(self):
        for a in self.aliens:
            self.screen.blit(a[0], a[1])
        for es in self.example_scores:
            es.blitme()


class Title:
    def __init__(self, bg_color, screen, text, text_size=40, text_color=(255, 255, 0)):
        self.bg_color = bg_color
        self.screen = screen
        self.text = text
        self.text_color = text_color
        self.font = Font('fonts/space_invaders.ttf', text_size)
        self.image = None
        self.image_rect = None

    def prep_image(self):
        self.image = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.image_rect = self.image.get_rect()

    def blitme(self):
        self.screen.blit(self.image, self.image_rect)


class Subtitle:
    def __init__(self, bg_color, screen, text, text_size=30, text_color=(0, 255, 0)):
        self.bg_color = bg_color
        self.screen = screen
        self.text = text
        self.text_color = text_color
        self.font = Font('fonts/space_invaders.ttf', text_size)
        self.image = None
        self.image_rect = None

    def prep_image(self):
        self.image = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.image_rect = self.image.get_rect()

    def blitme(self):
        self.screen.blit(self.image, self.image_rect)


class Intro:
    def __init__(self, settings, game_stats, screen):
        # settings, settings, stats
        self.settings = settings
        self.game_stats = game_stats
        self.screen = screen

        # text/image information
        self.title = Title(settings.intro_bg_color, self.screen, 'PIKACHU', text_size=72)
        self.subtitle = Subtitle(settings.intro_bg_color, self.screen, 'INVADERS', text_size=62)
        self.enemy_display = EnemyDisplay(settings, self.screen, self.settings.screen_height // 3)
        self.prep_image()

        # intro music

        self.intro_bgm = mixer.Sound('sounds/pokemon-opening.wav')

    def prep_image(self):
        self.title.prep_image()
        self.title.image_rect.centerx = (self.settings.screen_width // 2)
        self.title.image_rect.centery = (self.settings.screen_height // 5) - self.title.image_rect.height
        self.subtitle.prep_image()
        self.subtitle.image_rect.centerx = (self.settings.screen_width // 2)
        self.subtitle.image_rect.centery = (self.settings.screen_height // 5) + (self.title.image_rect.height // 3)

    def show_menu(self):
        self.title.blitme()
        self.subtitle.blitme()
        self.enemy_display.show_examples()


def level_intro(ai_settings, screen, stats):
    if stats.game_active:
        level_text = Title(ai_settings.bg_color, screen, 'Level: ' + str(stats.level))
        level_text.prep_image()
        level_text.image_rect.centerx = (ai_settings.screen_width // 2)
        level_text.image_rect.centery = (ai_settings.screen_height // 2) - level_text.image_rect.height
        start_time = time.get_ticks()
        while abs(start_time - time.get_ticks()) <= 1500:
            screen.fill(ai_settings.bg_color)
            level_text.blitme()
            display.flip()
