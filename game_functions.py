import sys
import pygame
import random

from alien import Alien
from bullet import Bullet
from alien_bullet import AlienBullet
from high_scores import HighScoreScreen
from intro import Button, Intro, level_intro
from ufo import Ufo


def check_events(ai_settings, screen, stats, ship, bullets):
    """Handle key presses and mouse events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stats.save_high_score()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats.game_active, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)


def start_new_game(ai_settings, screen, stats, sb,
                   ship, aliens, alien_bullets, bullets):
    """Start a new game when the play button is clicked"""
    # Hide the mouse
    pygame.mouse.set_visible(False)
    # Reset settings
    ai_settings.initialize_dynamic_settings()
    # Reset game stats
    stats.reset_stats()
    stats.game_active = True
    # Reset scoreboard images
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_ships()
    # Remove all aliens and bullets
    aliens.empty()
    bullets.empty()
    alien_bullets.empty()
    # Create new alien fleet and center the ship
    create_fleet(ai_settings, screen, ship, aliens)
    stats.next_speedup = len(aliens) - (len(aliens) // 5)
    stats.aliens_left = len(aliens)
    ship.center_ship()


def check_keydown_events(event, ai_settings, screen, game_active, ship, bullets):
    """Handle key presses"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE and game_active:   # Prevent sounds from occurring when game not active
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    """Handle key releases"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet if the limit has not been reached already"""
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        ship.fire_weapon()
        bullets.add(new_bullet)


def fire_random_alien_bullet(ai_settings, screen, aliens, alien_bullets):
    """Fire a alien bullet from a random alien in the fleet"""
    firing_alien = random.choice(aliens.sprites())
    if len(alien_bullets) < ai_settings.alien_bullet_allowed and \
            (ai_settings.alien_bullet_stamp is None or
             (abs(pygame.time.get_ticks() - ai_settings.alien_bullet_stamp) > ai_settings.alien_bullet_time)):
        new_alien_bullet = AlienBullet(ai_settings, screen, firing_alien)
        firing_alien.fire_weapon()
        alien_bullets.add(new_alien_bullet)


def alien_collision_check(bullet, alien):
    if alien.dead:
        return False
    return pygame.sprite.collide_rect(bullet, alien)


def check_alien_bullet_collisions(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo):
    """Check that any aliens have been hit, handle empty fleet condition"""
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, False, collided=alien_collision_check)
    if collisions:
        for aliens_hit in collisions.values():
            for a in aliens_hit:
                stats.score += ai_settings.alien_points[str(a.alien_type)]
                a.begin_death()
            sb.prep_score()
        check_high_score(stats, sb)
    ufo_collide = pygame.sprite.groupcollide(bullets, ufo, True, False, collided=alien_collision_check)
    if ufo_collide:
        for ufo in ufo_collide.values():
            for u in ufo:
                stats.score += u.score
                u.begin_death()
            sb.prep_score()
        check_high_score(stats, sb)
    if len(aliens) == 0:
        # destroy all existing bullets and re-create fleet, reset speed, increase starting speed
        if ufo:
            for u in ufo.sprites():
                u.kill()    # kill any UFOs before start of new level
        alien_bullets.empty()
        bullets.empty()
        stats.level += 1
        level_intro(ai_settings, screen, stats)     # play an intro for the level
        ai_settings.increase_base_speed()       # increase base speed, reset speed to base
        ai_settings.reset_alien_speed()
        sb.prep_level()     # setup scoreboard
        create_fleet(ai_settings, screen, ship, aliens)
        stats.next_speedup = len(aliens) - (len(aliens) // 5)   # Get next number of aliens to speedup at
    stats.aliens_left = len(aliens)
    if stats.aliens_left <= stats.next_speedup and ai_settings.alien_speed_factor < ai_settings.alien_speed_limit:
        # If the number of aliens left is low enough, and we haven't already hit the limit, speed up aliens
        ai_settings.increase_alien_speed()
        stats.next_speedup = stats.aliens_left - (stats.aliens_left // 5)


def check_ship_alien_bullet_collisions(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo):
    """Check that any alien bullets have collided with the ship"""
    collide = pygame.sprite.spritecollideany(ship, alien_bullets)
    if collide:
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo)


def check_bunker_collisions(alien_bullets, bullets, bunkers):
    """Check if any alien bullets or ship bullets have collided with the bunkers"""
    collisions = pygame.sprite.groupcollide(bullets, bunkers, True, False)
    for b_list in collisions.values():
        for block in b_list:
            block.damage(top=False)
    collisions = pygame.sprite.groupcollide(alien_bullets, bunkers, True, False)
    for b_list in collisions.values():
        for block in b_list:
            block.damage(top=True)


def update_bullets_alien_bullet(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo):
    """Update the positions of all bullets, remove bullets that are no longer visible"""
    bullets.update()
    alien_bullets.update()
    # Remove bullets that are out of view
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    for alien_bullet in alien_bullets.copy():
        if alien_bullet.rect.bottom > ai_settings.screen_height:
            alien_bullets.remove(alien_bullet)
    check_alien_bullet_collisions(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo)
    check_ship_alien_bullet_collisions(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo)


def check_high_score(stats, sb):
    """Check to see if there's a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, bunkers, ufo_group, background):
    """Update images on the screen and flip to new screen"""
    if stats.game_active:
        ufo_event_check(ai_settings, screen, ufo_group)
    screen.fill(ai_settings.game_bg_color)
    screen.blit(background.image, background.rect)
    # Redraw all bullets
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    # Redraw all alien_bullets
    for alien_bullet in alien_bullets.sprites():
        alien_bullet.draw_alien_bullet()
    if ufo_group:
        ufo_group.update()
        for ufo in ufo_group.sprites():
            ufo.blitme()
    aliens.draw(screen)
    check_bunker_collisions(alien_bullets, bullets, bunkers)
    sb.show_score()
    ship.blitme()
    bunkers.update()
    pygame.display.flip()


def get_number_aliens(ai_settings, alien_width):
    """Determine the number of aliens that can fit in a row"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2.5 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of rows of aliens that can fit in a row"""
    available_space_y = (ai_settings.screen_height - (4 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2.5 * alien_height))
    return number_rows


def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets, alien_bullets, ufo):
    """Respond to ship being hit by an alien"""
    if ufo:     # ufos play sound, so kill them first so the death sound is clear
        for u in ufo.sprites():
            u.kill()
    ship.death()
    ship.update()

    while ship.dead:
        screen.fill(ai_settings.bg_color)
        ship.blitme()
        pygame.display.flip()
        ship.update()
    if stats.ships_left > 0:
        # Decrement lives
        stats.ships_left -= 1
        # Remove all aliens and bullets on screen
        aliens.empty()
        bullets.empty()
        alien_bullets.empty()
        # Re-create fleet and center ship
        ai_settings.reset_alien_speed()
        create_fleet(ai_settings, screen, ship, aliens)
        stats.next_speedup = len(aliens) - (len(aliens) // 5)
        stats.aliens_left = len(aliens.sprites())
        ship.center_ship()
        # Update scoreboard
        sb.prep_ships()
    else:
        ai_settings.stop_bgm()
        pygame.mixer.music.load('sounds/game-end.wav')
        pygame.mixer.music.play()
        stats.game_active = False
        stats.save_high_score()
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo):
    """Check if any aliens have reached the bottom of the screen"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treated the same as if the ship has been hit
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo)
            break


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo):
    """Check if any aliens in the fleet have reached an edge,
    then update the positions of all aliens"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    # check for alien-ship collisions
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo)
    # Check that any aliens have hit the bottom of the screen
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, alien_bullets, bullets, ufo)
    if aliens.sprites():
        fire_random_alien_bullet(ai_settings, screen, aliens, alien_bullets)


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create an alien and place it in a row"""
    if row_number < 2:
        alien_type = 1
    elif row_number < 4:
        alien_type = 2
    else:
        alien_type = 3
    alien = Alien(ai_settings, screen, alien_type)
    alien_width = alien.rect.width
    alien.x = alien_width + 1.25 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 1.25 * alien.rect.height * row_number
    alien.rect.y += int(ai_settings.screen_height / 8)
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Creates a full fleet of aliens"""
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet down, and change the fleets direction"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def check_fleet_edges(ai_settings, aliens):
    """Respond in the event any aliens have reached an edge of the screen"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def create_random_ufo(ai_settings, screen):
    """With a chance of 10% create a Ufo and return it with the time it was created"""
    ufo = None
    if random.randrange(0, 100) <= 15:  # 15% chance of ufo
        ufo = Ufo(ai_settings, screen)
    time_stamp = pygame.time.get_ticks()
    return time_stamp, ufo


def ufo_event_check(ai_settings, screen, ufo_group):
    """Check if now is a good time to create a ufo and if so create one and add it to the ufo group"""
    if not ai_settings.last_ufo and not ufo_group:
        ai_settings.last_ufo, n_ufo = create_random_ufo(ai_settings, screen)
        if n_ufo:
            ufo_group.add(n_ufo)
    elif abs(pygame.time.get_ticks() - ai_settings.last_ufo) > ai_settings.ufo_min_interval and not ufo_group:
        ai_settings.last_ufo, n_ufo = create_random_ufo(ai_settings, screen)
        if n_ufo:
            ufo_group.add(n_ufo)


def high_score_screen(ai_settings, game_stats, screen):
    """Display all high scores in a separate screen with a back button"""
    hs_screen = HighScoreScreen(ai_settings, screen, game_stats)
    back_button = Button(ai_settings, screen, 'Back To Menu', y_factor=0.85)

    while True:
        back_button.alter_text_color(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_button(*pygame.mouse.get_pos()):
                    return True
        screen.fill(ai_settings.bg_color)
        hs_screen.show_scores()
        back_button.draw_button()
        pygame.display.flip()


def startup_screen(ai_settings, game_stats, screen):
    """Display the startup menu on the screen, return False if the user wishes to quit,
    True if they are ready to play"""
    menu = Intro(ai_settings, game_stats, screen)
    play_button = Button(ai_settings, screen, 'Play Game', y_factor=0.70)
    hs_button = Button(ai_settings, screen, 'High Scores', y_factor=0.80)
    intro = True

    while intro:
        play_button.alter_text_color(*pygame.mouse.get_pos())
        hs_button.alter_text_color(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_x, click_y = pygame.mouse.get_pos()
                game_stats.game_active = play_button.check_button(click_x, click_y)
                intro = not game_stats.game_active
                if hs_button.check_button(click_x, click_y):
                    ret_hs = high_score_screen(ai_settings, game_stats, screen)
                    if not ret_hs:
                        return False
        screen.fill(ai_settings.intro_bg_color)
        menu.show_menu()
        hs_button.draw_button()
        play_button.draw_button()
        pygame.display.flip()

    return True


def play_bgm(ai_settings, stats):
    """Check that the game is still active before continue the background music"""
    if stats.game_active:
        ai_settings.continue_bgm()
