from pygame import *
from random import randint
import time
import math

mixer.init()
mixer.music.load("nachalo.mp3")
mixer.music.play()

natusk_sound = mixer.Sound("natusk.mp3")
boss_sound = mixer.Sound("boss.mp3")

music_list = {
    "easy": "easy.mp3",
    "medium": "medium.mp3",
    "hard": "hard.mp3",
    "demon": "demon.mp3",
    "open": "open.mp3",
    "without_mission": "without_mission.mp3",
    "boss_mission": "boss.mp3"
}

fire_sound = mixer.Sound("laser.mp3")
boss_laser_sound = mixer.Sound("boss_laser.mp3")

score = 0
lost = 0
max_lost = 7
goal = 0
goal_list = {
    "easy": 11,
    "medium": 26,
    "hard": 51,
    "demon": 101,
    "open": 999999999999999999,
    "without_mission": 999999999999999999999,
    "boss_mission": 101
}

win_width = 700
win_height = 500

font.init()
font3 = font.Font('pixel_font.ttf', 90)
font1 = font.Font('pixel_font.ttf', 50)
win_text = font1.render(' Мiсiя виконана!', True, (0, 255, 0))
lose_text = font1.render('        Мiсiя проваленна!', True, (250, 0, 0))
boss_win_text = font1.render('   Боса знищено!', True, (0, 255, 255))
boss_lose_text = font1.render(' Ти програв босу!', True, (255, 0, 255))
font2 = font.Font('pixel_font.ttf', 30)
font_pause = font.Font('pixel_font.ttf', 40)

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.original_image = image.load(player_image).convert_alpha()
        self.image = transform.scale(self.original_image, (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

bullets = sprite.Group()
boss_bullets = sprite.Group()

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

class BossBullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, dx=0, dy=0):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.spawn_time = time.time()
        self.dx = dx
        self.dy = dy

    def update(self):
        current_time = time.time()
        if current_time - self.spawn_time < 0.7:
            return
        self.rect.x += self.dx
        self.rect.y += self.dy
        if current_time - self.spawn_time >= 3:
            self.kill()
        elif self.rect.bottom > win_height or self.rect.right < 0 or self.rect.left > win_width or self.rect.top > win_height:
            self.kill()

class Player(GameSprite):
    def update(self):
        keys_pressed = key.get_pressed()
        if keys_pressed[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet("pyli.png", self.rect.centerx, self.rect.top, 15, 40, -25)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = -40
            lost = lost + 1

class Meteor(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = -40

class End(GameSprite):
    def __init__(self, end_image, end_x, end_y, size_x, size_y, end_speed, fire_rate):
        super().__init__(end_image, end_x, end_y, size_x, size_y, end_speed)
        self.fire_rate = fire_rate
        self.last_shot = time.time()

    def update(self):
        if self.rect.x <= 0 or self.rect.x >= win_width - self.rect.width:
            self.speed = -self.speed
        self.rect.x += self.speed
        if time.time() - self.last_shot >= self.fire_rate:
            self.fire()
            self.last_shot = time.time()

    def fire(self):
        bullet = Bullet("pyli.png", self.rect.centerx, self.rect.bottom, 15, 40, 10)
        bullets.add(bullet)

class Boss(GameSprite):
    def __init__(self, boss_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(boss_image, player_x, player_y, size_x, size_y, player_speed)
        self.health = goal_list["boss_mission"]
        self.direction = 1
        self.last_shot_time = time.time()
        self.fire_interval = 3
        self.original_y = player_y
        self.speed = player_speed * 3.5
        self.preparing_to_fire = False
        self.prepare_start_time = 0
        self.prepare_duration = 1.5  
        self.fire_threshold = 20  
        self.pause_after_fire = False
        self.pause_start_time = 0
        self.pause_duration = 0.7  

    def update(self):
        current_time = time.time()
        self.rect.y = self.original_y + math.sin(time.time() * 2) * 20

        if self.pause_after_fire:
            if current_time - self.pause_start_time >= self.pause_duration:
                self.pause_after_fire = False
                self.last_shot_time = current_time
            else:
                return

        if self.preparing_to_fire:
            if abs(self.rect.centerx - player.rect.centerx) > self.fire_threshold:
                if self.rect.centerx < player.rect.centerx:
                    self.rect.x += self.speed
                else:
                    self.rect.x -= self.speed
            else:
                self.fire()
                self.preparing_to_fire = False
                self.pause_after_fire = True
                self.pause_start_time = current_time
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.right > win_width or self.rect.left < 0:
                self.direction *= -1

            if current_time - self.last_shot_time >= self.fire_interval:
                self.preparing_to_fire = True
                self.prepare_start_time = current_time

    def fire(self):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        dx = dx / distance * 10  
        dy = dy / distance * 10

        bullet = BossBullet("laser_boss.png", self.rect.centerx - 50, self.rect.bottom - 60, 90, 300, 10, dx, dy)
        boss_bullets.add(bullet)
        boss_laser_sound.play()

init()

background = transform.scale(image.load("background.jpg"), (win_width, win_height))
loading_screen = transform.scale(image.load("nachalo.png"), (win_width, win_height))
twow_window = transform.scale(image.load("Twowindow.jpg"), (win_width, win_height))
pause_background = Surface((win_width, win_height), SRCALPHA)
pause_background.fill((0, 0, 0, 128))

window = display.set_mode((win_width, win_height))

text_color = (255, 255, 255)

button_missions_text = font2.render("Місії", True, text_color)
button_missions_rect = button_missions_text.get_rect(center=(win_width // 2, win_height // 2 - 65))
button_modes_text = font2.render("Режими", True, text_color)
button_modes_rect = button_modes_text.get_rect(center=(win_width // 2, win_height // 2 - 10))

button_exit_game_text = font2.render("Вийти з гри", True, text_color)
button_exit_game_rect = button_exit_game_text.get_rect(center=(win_width // 2, win_height // 2 + 45))

button_boss_text = font2.render("Бос Місія", True, text_color)
button_boss_rect = button_boss_text.get_rect(center=(win_width // 2, win_height // 2 + 25))

boss_mission_text = font2.render("Бос Місія", True, text_color)
boss_mission_rect = boss_mission_text.get_rect(center=(win_width // 2, win_height // 2 + 163))
button_back_text = font2.render("Назад", True, text_color)
button_back_rect = button_back_text.get_rect(bottomleft=(20, win_height - 20))

mission_buttons_texts_surfaces = {
    "easy": font2.render("Легка мiсiя", True, text_color),
    "medium": font2.render("Середня мiсiя", True, text_color),
    "hard": font2.render("Важка мiсiя", True, text_color),
    "demon": font2.render("Демон мiсiя", True, text_color)
}

mission_buttons_rects = {}
y_offset_missions = win_height // 2 - 55
for text_surface in mission_buttons_texts_surfaces.values():
    rect = text_surface.get_rect(center=(win_width // 2, y_offset_missions + text_surface.get_height() // 2))
    mission_buttons_rects[list(mission_buttons_texts_surfaces.keys())[list(mission_buttons_texts_surfaces.values()).index(text_surface)]] = rect
    y_offset_missions += 50

mode_buttons_texts_surfaces = {
    "open": font2.render("Вiдкритий режим", True, text_color),
    "without_mission": font2.render("Режим без мiсiї", True, text_color)
}

mode_buttons_rects = {}
y_offset_modes = win_height // 2 - 35
for text_surface in mode_buttons_texts_surfaces.values():
    rect = text_surface.get_rect(center=(win_width // 2, y_offset_modes + text_surface.get_height() // 2))
    mode_buttons_rects[list(mode_buttons_texts_surfaces.keys())[list(mode_buttons_texts_surfaces.values()).index(text_surface)]] = rect
    y_offset_modes += 50

current_menu = "main"
game_paused = False
boss_active = False
boss_group = sprite.Group()
boss_instance = None

star_left_img_original = image.load("star.png").convert_alpha()
star_right_img_original = image.load("star2.png").convert_alpha()
logo_img_original = image.load("logo.png").convert_alpha()
star3_img_original = image.load("Star3.png").convert_alpha()
star4_img_original = image.load("Star4.png").convert_alpha()

star_scale = 0.5
logo_scale = 2
star3_scale = 2
star4_scale = 2

star_left_img = transform.scale(star_left_img_original, (int(star_left_img_original.get_width() * star_scale), int(star_left_img_original.get_height() * star_scale)))
star_right_img = transform.scale(star_right_img_original, (int(star_right_img_original.get_width() * star_scale), int(star_right_img_original.get_height() * star_scale)))
logo_img = transform.scale(logo_img_original, (int(logo_img_original.get_width() * logo_scale), int(logo_img_original.get_height() * logo_scale)))
star3_img = transform.scale(star3_img_original, (int(star3_img_original.get_width() * star3_scale), int(star3_img_original.get_height() * star3_scale)))
star4_img = transform.scale(star4_img_original, (int(star4_img_original.get_width() * star4_scale), int(star4_img_original.get_height() * star4_scale)))

star_left_rect = star_left_img.get_rect()
star_right_rect = star_right_img.get_rect()
logo_rect = logo_img.get_rect(centerx=win_width // 2 + 17, y=0)
star3_left_rect = star3_img.get_rect(topleft=(-90, -50))
star3_right_rect = star3_img.get_rect(topright=(win_width + 85, -50))
star4_left_rect = star4_img.get_rect(topleft=(-90, 200))
star4_right_rect = star4_img.get_rect(topright=(win_width + 85, 200))
star4_down_rect = star4_img.get_rect(topright=(win_width - 50, 300))

class AnimatedSprite:
    def __init__(self, image, rect, fade_duration=1000, start_time=None):
        self.original_image = image
        self.rect = rect
        self.fade_duration = fade_duration
        if start_time is None:
            self.start_time = time.time() * 1000
        else:
            self.start_time = start_time
        self.fading_in = True

    def update(self):
        current_time = time.time() * 1000
        elapsed_time = current_time - self.start_time
        alpha = 0
        if self.fading_in:
            alpha = int((elapsed_time / self.fade_duration) * 255)
            if alpha > 255:
                alpha = 255
                self.fading_in = False
                self.start_time = current_time
        else:
            alpha = 255 - int((elapsed_time / self.fade_duration) * 255)
            if alpha < 125:
                alpha = 50
                self.fading_in = True
                self.start_time = current_time

        self.image = self.original_image.copy()
        self.image.set_alpha(alpha)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

animated_star_left_missions = AnimatedSprite(star_left_img, star_left_rect.copy(), fade_duration=randint(500, 1500))
animated_star_right_missions = AnimatedSprite(star_right_img, star_right_rect.copy(), fade_duration=randint(800, 2000), start_time=(time.time() * 1000) + randint(0, 500))
animated_star_left_modes = AnimatedSprite(star_left_img, star_left_rect.copy(), fade_duration=randint(700, 1800), start_time=(time.time() * 1000) + randint(200, 800))
animated_star_right_modes = AnimatedSprite(star_right_img, star_right_rect.copy(), fade_duration=randint(600, 1600))
animated_logo = AnimatedSprite(logo_img, logo_rect.copy(), fade_duration=2000)
animated_star3_left = AnimatedSprite(star3_img, star3_left_rect.copy(), fade_duration=randint(1000, 2500), start_time=(time.time() * 1000) + randint(0, 1000))
animated_star3_right = AnimatedSprite(star3_img, star3_right_rect.copy(), fade_duration=randint(900, 2200))
animated_star4_left = AnimatedSprite(star4_img, star4_left_rect.copy(), fade_duration=randint(1200, 2800), start_time=(time.time() * 1000) + randint(300, 900))
animated_star4_right = AnimatedSprite(star4_img, star4_right_rect.copy(), fade_duration=randint(1100, 2600))
animated_star4_down = AnimatedSprite(star4_img, star4_down_rect.copy(), fade_duration=randint(1300, 3000), start_time=(time.time() * 1000) + randint(100, 600))

player = Player("raketa.png", 5, win_height - 100, 80, 100, 10)

monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy("monsters.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

meteors = sprite.Group()
for i in range(1, 6):
    meteor = Meteor("meteor.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    meteors.add(meteor)

class MenuRocket(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, target_rect=None):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.start_time = time.time()
        self.animation_interval = 7
        self.target_rect = target_rect
        self.active = False
        self.spawn_time = 0
        self.base_speed = player_speed
        self.speed_multiplier = 0.7

    def update(self):
        current_time = time.time()
        if not self.active and current_time - self.spawn_time >= self.animation_interval:
            self.rect.x = -self.rect.width
            self.rect.y = randint(50, win_height - 150)
            self.active = True
            self.speed = self.base_speed * self.speed_multiplier
            if self.target_rect:
                angle = math.atan2(self.target_rect.centery - self.rect.centery, self.target_rect.centerx - self.rect.centerx)
                self.dx = self.speed * math.cos(angle)
                self.dy = self.speed * math.sin(angle)
            else:
                self.dx = self.speed
                self.dy = 0
            self.spawn_time = current_time

        if self.active:
            self.rect.x += self.dx
            self.rect.y += self.dy
            if self.rect.left > win_width or self.rect.top < -self.rect.height or self.rect.bottom > win_height:
                self.kill()

menu_rockets = sprite.Group()
last_rocket_spawn_time = time.time()
rocket_spawn_interval = 8
rocket_speed = 4

def spawn_menu_rocket(target_rect=None):
    global last_rocket_spawn_time, rocket_speed
    current_time = time.time()
    if current_time - last_rocket_spawn_time >= rocket_spawn_interval:
        rocket = MenuRocket("raketa2.png", -100, win_height // 2, 80, 100, rocket_speed, target_rect)
        menu_rockets.add(rocket)
        last_rocket_spawn_time = current_time

def draw_main_menu():
    window.blit(loading_screen, (0, 0))
    animated_logo.update()
    animated_logo.draw(window)
    animated_star3_left.update()
    animated_star3_left.draw(window)
    animated_star3_right.update()
    animated_star3_right.draw(window)
    animated_star4_left.update()
    animated_star4_left.draw(window)
    animated_star4_right.update()
    animated_star4_right.draw(window)
    animated_star4_down.update()
    animated_star4_down.draw(window)

    animated_star_left_missions.rect.right = button_missions_rect.left - 10
    animated_star_left_missions.rect.centery = button_missions_rect.centery
    animated_star_left_missions.update()
    animated_star_left_missions.draw(window)

    animated_star_right_missions.rect.left = button_missions_rect.right + 10
    animated_star_right_missions.rect.centery = button_missions_rect.centery
    animated_star_right_missions.update()
    animated_star_right_missions.draw(window)

    animated_star_left_modes.rect.right = button_modes_rect.left - 10
    animated_star_left_modes.rect.centery = button_modes_rect.centery
    animated_star_left_modes.update()
    animated_star_left_modes.draw(window)

    animated_star_right_modes.rect.left = button_modes_rect.right + 10
    animated_star_right_modes.rect.centery = button_modes_rect.centery
    animated_star_right_modes.update()
    animated_star_right_modes.draw(window)

    if button_missions_rect.collidepoint(mouse.get_pos()):
        scaled_missions_text = transform.scale(button_missions_text, (int(button_missions_text.get_width() * 1.25), int(button_missions_text.get_height() * 1.25)))
        scaled_missions_rect = scaled_missions_text.get_rect(center=button_missions_rect.center)
        window.blit(scaled_missions_text, scaled_missions_rect)
    else:
        window.blit(button_missions_text, button_missions_rect)

    if button_modes_rect.collidepoint(mouse.get_pos()):
        scaled_modes_text = transform.scale(button_modes_text, (int(button_modes_text.get_width() * 1.25), int(button_modes_text.get_height() * 1.25)))
        scaled_modes_rect = scaled_modes_text.get_rect(center=button_modes_rect.center)
        window.blit(scaled_modes_text, scaled_modes_rect)
    else:
        window.blit(button_modes_text, button_modes_rect)

    if button_exit_game_rect.collidepoint(mouse.get_pos()):
        scaled_exit_game_text = transform.scale(button_exit_game_text, (int(button_exit_game_text.get_width() * 1.25), int(button_exit_game_text.get_height() * 1.25)))
        scaled_exit_game_rect = scaled_exit_game_text.get_rect(center=button_exit_game_rect.center)
        window.blit(scaled_exit_game_text, scaled_exit_game_rect)
    else:
        window.blit(button_exit_game_text, button_exit_game_rect)

    menu_rockets.update()
    menu_rockets.draw(window)

    display.update()

def draw_missions_menu():
    window.blit(loading_screen, (0, 0))
    animated_logo.update()
    animated_logo.draw(window)
    animated_star3_left.update()
    animated_star3_left.draw(window)
    animated_star3_right.update()
    animated_star3_right.draw(window)
    animated_star4_left.update()
    animated_star4_left.draw(window)
    animated_star4_right.update()
    animated_star4_right.draw(window)
    animated_star4_down.update()
    animated_star4_down.draw(window)
    missions_text = font2.render("Оберіть місію:", True, text_color)
    missions_text_rect = missions_text.get_rect(center=(win_width // 2, win_height // 2 - 80)) 
    window.blit(missions_text, missions_text_rect)

    if button_back_rect.collidepoint(mouse.get_pos()):
        scaled_back_text = transform.scale(button_back_text, (int(button_back_text.get_width() * 1.25), int(button_back_text.get_height() * 1.25)))
        scaled_back_rect = scaled_back_text.get_rect(bottomleft=button_back_rect.bottomleft)
        window.blit(scaled_back_text, scaled_back_rect)
    else:
        window.blit(button_back_text, button_back_rect)

    for level, text_surface in mission_buttons_texts_surfaces.items():
        rect = mission_buttons_rects[level]
        if rect.collidepoint(mouse.get_pos()):
            scaled_text = transform.scale(text_surface, (int(text_surface.get_width() * 1.25), int(text_surface.get_height() * 1.25)))
            scaled_rect = scaled_text.get_rect(center=rect.center)
            window.blit(scaled_text, scaled_rect)
        else:
            window.blit(text_surface, rect)

    boss_mission_text = font2.render("Бос Місія", True, text_color)
    boss_mission_rect = boss_mission_text.get_rect(center=(win_width // 2, win_height // 2 + 163))
    if boss_mission_rect.collidepoint(mouse.get_pos()):
        scaled_boss_text = transform.scale(boss_mission_text, (int(boss_mission_text.get_width() * 1.25), int(boss_mission_text.get_height() * 1.25)))
        scaled_boss_rect = scaled_boss_text.get_rect(center=boss_mission_rect.center)
        window.blit(scaled_boss_text, scaled_boss_rect)
    else:
        window.blit(boss_mission_text, boss_mission_rect)

    menu_rockets.update()
    menu_rockets.draw(window)

    display.update()

def draw_modes_menu():
    window.blit(loading_screen, (0, 0))
    animated_logo.update()
    animated_logo.draw(window)
    animated_star3_left.update()
    animated_star3_left.draw(window)
    animated_star3_right.update()
    animated_star3_right.draw(window)
    animated_star4_left.update()
    animated_star4_left.draw(window)
    animated_star4_right.update()
    animated_star4_right.draw(window)
    animated_star4_down.update()
    animated_star4_down.draw(window)
    modes_text = font2.render("Оберіть режим:", True, text_color)
    modes_text_rect = modes_text.get_rect(center=(win_width // 2, win_height // 2 - 85)) 
    window.blit(modes_text, modes_text_rect)

    if button_back_rect.collidepoint(mouse.get_pos()):
        scaled_back_text = transform.scale(button_back_text, (int(button_back_text.get_width() * 1.25), int(button_back_text.get_height() * 1.25)))
        scaled_back_rect = scaled_back_text.get_rect(bottomleft=button_back_rect.bottomleft)
        window.blit(scaled_back_text, scaled_back_rect)
    else:
        window.blit(button_back_text, button_back_rect)

    for level, text_surface in mode_buttons_texts_surfaces.items():
        rect = mode_buttons_rects[level]
        if rect.collidepoint(mouse.get_pos()):
            scaled_text = transform.scale(text_surface, (int(text_surface.get_width() * 1.25), int(text_surface.get_height() * 1.25)))
            scaled_rect = scaled_text.get_rect(center=rect.center)
            window.blit(scaled_text, scaled_rect)
        else:
            window.blit(text_surface, rect)

    menu_rockets.update()
    menu_rockets.draw(window)

    display.update()

def draw_boss_mission_menu():
    window.blit(loading_screen, (0, 0))
    animated_logo.update()
    animated_logo.draw(window)
    animated_star3_left.update()
    animated_star3_left.draw(window)
    animated_star3_right.update()
    animated_star3_right.draw(window)
    animated_star4_left.update()
    animated_star4_left.draw(window)
    animated_star4_right.update()
    animated_star4_right.draw(window)
    animated_star4_down.update()
    animated_star4_down.draw(window)
    boss_mission_text = font2.render("Бос Місія:", True, text_color)
    boss_mission_text_rect = boss_mission_text.get_rect(center=(win_width // 2, win_height // 2 - 80))
    window.blit(boss_mission_text, boss_mission_text_rect)

    start_boss_text = font2.render("Почати бос місію", True, text_color)
    start_boss_rect = start_boss_text.get_rect(center=(win_width // 2, win_height // 2))
    if start_boss_rect.collidepoint(mouse.get_pos()):
        scaled_start_boss_text = transform.scale(start_boss_text, (int(start_boss_text.get_width() * 1.25), int(start_boss_text.get_height() * 1.25)))
        scaled_start_boss_rect = scaled_start_boss_text.get_rect(center=start_boss_rect.center)
        window.blit(scaled_start_boss_text, scaled_start_boss_rect)
    else:
        window.blit(start_boss_text, start_boss_rect)

    if button_back_rect.collidepoint(mouse.get_pos()):
        scaled_back_text = transform.scale(button_back_text, (int(button_back_text.get_width() * 1.25), int(button_back_text.get_height() * 1.25)))
        scaled_back_rect = scaled_back_text.get_rect(bottomleft=button_back_rect.bottomleft)
        window.blit(scaled_back_text, scaled_back_rect)
    else:
        window.blit(button_back_text, button_back_rect)

    menu_rockets.update()
    menu_rockets.draw(window)

    display.update()

def two_window(level):
    two_window_surface = display.set_mode((700, 500))
    two_window_surface.blit(twow_window, (0, 0))
    font_two = font.Font('pixel_font.ttf', 20)

    messages = []
    delay = 3
    if level == "easy":
        messages = ["Привіт, юний падаване!", "Твоя місія...", "...цілих 10 ворожих кораблів!", "Будь обережний ти можеш дозволити собі лише 6 помилок.", "За 9 секунд почнеться битва!"]
        delay = 5
    elif level == "medium":
        messages = ["Вітаю, лицарю Джедай!", "До тебе звертається сам Обі-Ван...", "...25ворожих кораблів!", "Сконцентруйся! Ти можеш дозволити собі лише 6 помилок.", "Приготуйся до гіперстрибка через 11 секунд!"]
        delay = 7
    elif level == "hard":
        messages = ["Слухай сюди, легендо!", "На тебе покладається остання надія галактики...", "...50 ворожих кораблів! Це не жарти!", "Ти можеш дозволити собі лише 6 помилок...", "До початку нещадної битви залишилось 9 секунд!"]
        delay = 5
    elif level == "demon":
        messages = ["Ти... ти справді на це наважився?", "Твоя місія? Вижити...", "...сотні ворожих кораблів! Це майже самогубство!", "Лише 6 кораблів можуть пройти.", "До пекла залишилося 13 секунд!"]
        delay = 9
    elif level == "open":
        messages = ["Вітаємо в безмежному космосі!", "Це режим вільного польоту.", "Живи скільки завгодно.", "Немає перемоги, немає поразки.", "Насолоджуйся грою через 10 секунд!"]
        delay = 6
    elif level == "without_mission":
        messages = ["Привіт, мисливцю на Сітхів!", "Сьогодні без офіційних завдань...", "Сітхів тут - як зірок на нічному небі...", "Твоя мета? Отримати задоволення...","Лише 6 кораблів можуть пройти, як і в звичайних місіях.", "Готуйся до безкінечної бійні через 11 секунд!"]
        delay = 7
    elif level == "boss_mission":
        messages = ["Увага! Ти наблизився до Зірки Смерті!", "Твоя ціль - знищити її сотнями пострілами!", "Будь обережний, його атаки нищівні і в тебе 10 життів!", "Знищи його, і галактика буде врятована!", "Приготуйся до вирішальної битви через 9 секунд!"]
        delay = 5

    y_offset = 50
    for msg in messages:
        text_two = font_two.render(msg, True, (255, 255, 255))
        text_rect = text_two.get_rect(centerx=two_window_surface.get_width() // 2, y=y_offset)
        two_window_surface.blit(text_two, text_rect)
        y_offset += 50
    display.update()
    time.sleep(delay)
    two_window_surface.fill((255, 255, 255))
    display.update()

    for i in range(3, 0, -1):
        window.fill((0, 0, 0))
        text_countdown = font3.render(str(i), True, (255, 255, 255))
        text_rect = text_countdown.get_rect(center=(win_width // 2, win_height // 2))
        window.blit(text_countdown, text_rect)
        display.update()
        time.sleep(1)

    window.fill((0, 0, 0))
    text_go = font3.render("Go!", True, (255, 255, 255))
    text_rect = text_go.get_rect(center=(win_width // 2, win_height // 2))
    window.blit(text_go, text_rect)
    display.update()
    time.sleep(1)
    return

button_continue_text = font_pause.render("Продовжити", True, text_color)
button_continue_rect = button_continue_text.get_rect(center=(win_width // 2, win_height // 2 - 60))

button_exit_to_menu_text = font_pause.render("Вийти в меню", True, text_color)
button_exit_to_menu_rect = button_exit_to_menu_text.get_rect(center=(win_width // 2, win_height // 2))

button_exit_text = font_pause.render("Вийти з гри", True, text_color)
button_exit_rect = button_exit_text.get_rect(center=(win_width // 2, win_height // 2 + 60))

def show_pause_menu():
    window.blit(pause_background, (0, 0))

    if button_continue_rect.collidepoint(mouse.get_pos()):
        scaled_continue_text = transform.scale(button_continue_text, (int(button_continue_text.get_width() * 1.25), int(button_continue_text.get_height() * 1.25)))
        scaled_continue_rect = scaled_continue_text.get_rect(center=button_continue_rect.center)
        window.blit(scaled_continue_text, scaled_continue_rect)
    else:
        window.blit(button_continue_text, button_continue_rect)

    if button_exit_to_menu_rect.collidepoint(mouse.get_pos()):
        scaled_exit_to_menu_text = transform.scale(button_exit_to_menu_text, (int(button_exit_to_menu_text.get_width() * 1.25), int(button_exit_to_menu_text.get_height() * 1.25)))
        scaled_exit_to_menu_rect = scaled_exit_to_menu_text.get_rect(center=button_exit_to_menu_rect.center)
        window.blit(scaled_exit_to_menu_text, scaled_exit_to_menu_rect)
    else:
        window.blit(button_exit_to_menu_text, button_exit_to_menu_rect)

    if button_exit_rect.collidepoint(mouse.get_pos()):
        scaled_exit_text = transform.scale(button_exit_text, (int(button_exit_text.get_width() * 1.25), int(button_exit_text.get_height() * 1.25)))
        scaled_exit_rect = scaled_exit_text.get_rect(center=button_exit_rect.center)
        window.blit(scaled_exit_text, scaled_exit_rect)
    else:
        window.blit(button_exit_text, button_exit_rect)

    display.update()

last_boss_laser_hit_time = 0

game = True
finish = False
game_started = False
end = None
boss_active = False
boss_instance = None
boss_health = 0
score = 0 
lost = 0

draw_main_menu()

while game:
    current_time = time.time()
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                mouse_pos = e.pos
                if current_menu == "main":
                    if button_missions_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        current_menu = "missions"
                        draw_missions_menu()
                    elif button_modes_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        current_menu = "modes"
                        draw_modes_menu()
                    elif button_exit_game_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        game = False
                    elif button_boss_rect.collidepoint(mouse_pos): 
                         natusk_sound.play()
                         current_menu = "boss_mission_menu"
                         draw_boss_mission_menu()
                elif current_menu == "missions":
                    if button_back_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        current_menu = "main"
                        draw_main_menu()
                    else:
                        if boss_mission_rect.collidepoint(mouse_pos):
                            natusk_sound.play()
                            goal = goal_list["boss_mission"]
                            mixer.music.load(music_list["boss_mission"])
                            mixer.music.play()
                            boss_active = True
                            boss_instance = Boss("boss.png", win_width // 2 - 125, 50, 250, 250, 3)
                            boss_group.add(boss_instance)
                            score = 0
                            lost = 0
                            monsters.empty()
                            meteors.empty()
                            bullets.empty()
                            boss_bullets.empty()
                            max_lost = 9999999999
                            two_window("boss_mission")
                            game_started = True
                            finish = False
                            window.blit(background, (0, 0))
                            display.update()
                            current_menu = "game"
                            break
                        for level, rect in mission_buttons_rects.items():
                            if rect.collidepoint(mouse_pos):
                                natusk_sound.play()
                                goal = goal_list[level]
                                mixer.music.load(music_list[level])
                                mixer.music.play()
                                max_lost = 6
                                two_window(level)
                                game_started = True
                                finish = False
                                boss_active = False
                                boss_instance = None
                                score = 0
                                lost = 0
                                monsters.empty()
                                meteors.empty()
                                for i in range(1, 6):
                                    monster = Enemy("monsters.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
                                    monsters.add(monster)
                                    meteor = Meteor("meteor.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
                                    meteors.add(meteor)
                                window.blit(background, (0, 0))
                                display.update()
                                current_menu = "game"
                                break
                elif current_menu == "modes":
                    if button_back_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        current_menu = "main"
                        draw_main_menu()
                    else:
                        for level, rect in mode_buttons_rects.items():
                            if rect.collidepoint(mouse_pos):
                                natusk_sound.play()
                                goal = goal_list[level]
                                mixer.music.load(music_list[level])
                                mixer.music.play()
                                boss_active = False
                                boss_instance = None
                                score = 0
                                lost = 0
                                monsters.empty()
                                meteors.empty()
                                for i in range(1, 6):
                                    monster = Enemy("monsters.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
                                    monsters.add(monster)
                                    meteor = Meteor("meteor.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
                                    meteors.add(meteor)
                                if level == "open":
                                    max_lost = 9999999999
                                else:
                                    max_lost = 7
                                two_window(level)
                                game_started = True
                                finish = False
                                window.blit(background, (0, 0))
                                display.update()
                                current_menu = "game"
                                break
                elif current_menu == "boss_mission_menu": 
                    if button_back_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        current_menu = "main"
                        draw_main_menu()
                    else:
                        start_boss_text = font2.render("Почати бос місію", True, text_color)
                        start_boss_rect = start_boss_text.get_rect(center=(win_width // 2, win_height // 2))
                        if start_boss_rect.collidepoint(mouse_pos):
                            natusk_sound.play()
                            goal = goal_list["boss_mission"]
                            mixer.music.load(music_list["boss_mission"])
                            mixer.music.play()
                            boss_active = True
                            boss_instance = Boss("boss.png", win_width // 2 - 125, 50, 250, 250, 3)
                            boss_group.add(boss_instance)
                            score = 0
                            lost = 0
                            monsters.empty()
                            meteors.empty()
                            bullets.empty()
                            boss_bullets.empty()
                            max_lost = 9999999999
                            two_window("boss_mission")
                            game_started = True
                            finish = False
                            window.blit(background, (0, 0))
                            display.update()
                            current_menu = "game"
                elif current_menu == "pause":
                    if button_continue_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        game_paused = False
                        current_menu = "game"
                    elif button_exit_to_menu_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        game_paused = False
                        current_menu = "main"
                        mixer.music.load("nachalo.mp3")
                        mixer.music.play()
                    elif button_exit_rect.collidepoint(mouse_pos):
                        natusk_sound.play()
                        game = False
        elif e.type == KEYDOWN:
            if current_menu == "game" and game_started and e.key == K_SPACE:
                fire_sound.play()
                player.fire()
                bullets.draw(window) 
            elif game_started and e.key == K_ESCAPE:
                game_paused = True
                current_menu = "pause"
                show_pause_menu()

    if current_menu == "main":
        spawn_menu_rocket(button_missions_rect)
        spawn_menu_rocket(button_modes_rect)
        spawn_menu_rocket(button_boss_rect) 
    elif current_menu == "missions":
        spawn_menu_rocket()
    elif current_menu == "modes":
        spawn_menu_rocket()
    elif current_menu == "boss_mission_menu":
        spawn_menu_rocket()
    elif current_menu == "game":
        menu_rockets.empty()

    if current_menu == "game":
        if game_started and not game_paused:
            window.blit(background, (0, 0))

            text = font2.render("Рахунок: " + str(score), 1, (255, 255, 255))
            window.blit(text, (10, 20))

            text_lost = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
            window.blit(text_lost, (10, 50))

            player.update()
            player.reset()

            if boss_active and boss_instance:
                boss_instance.update()
                boss_instance.reset()
                boss_bullets.update()
                boss_bullets.draw(window)
                bullets.update()
                bullets.draw(window)

                collisions = sprite.spritecollide(player, boss_bullets, False)
                if collisions:
                    if current_time - last_boss_laser_hit_time >= 0.2:
                        lost += 1 
                        last_boss_laser_hit_time = current_time
                    if lost >= 11:
                        finish = True
                        window.blit(lose_text, (win_width // 3 - 250, win_height // 2 - 50))
                        display.update()
                        time.sleep(3)
                        game = False
                    elif lost >= max_lost:
                        finish = True
                        window.blit(boss_lose_text, (win_width // 3 - 100, win_height // 2 - 50))
                        display.update()
                        time.sleep(3)
                        game = False

                bullet_hits = sprite.spritecollide(boss_instance, bullets, True)
                if bullet_hits:
                    score += 1 
                    boss_instance.health -= 1
                    if boss_instance.health <= 0:
                        finish = True
                        window.blit(boss_win_text, (win_width // 3 - 100, win_height // 2 - 50))
                        display.update()
                        time.sleep(3)
                        game = False

            elif not finish:
                monsters.update()
                meteors.update()
                bullets.update()

                collides = sprite.groupcollide(monsters, bullets, True, True)
                for c in collides:
                    score += 1
                    monster = Enemy("monsters.png", randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
                    monsters.add(monster)
                monsters.draw(window)
                meteors.draw(window)
                bullets.draw(window)

                if sprite.spritecollide(player, monsters, True) or sprite.spritecollide(player, meteors, True):
                    lost += 2

                if score >= goal and goal != goal_list["open"] and goal != goal_list["without_mission"]:
                    end = End("raketa.png", win_width // 2 - 50, 50, 100, 100, 5, 1)
                elif lost >= max_lost and max_lost != 9999999999 and not boss_active:
                    end = End("raketa_lose.png", win_width // 2 - 50, 50, 100, 100, 5, 1)

            if end:
                end.update()
                end.reset()
                if sprite.spritecollide(player, bullets, True):
                    lost += 1
                if lost >= max_lost and not boss_active:
                    finish = True
                    window.blit(lose_text, (win_width // 3 - 250, win_height // 2 - 50))
                    display.update()
                    time.sleep(3)
                    game = False
                elif score >= goal and not boss_active:
                    finish = True
                    window.blit(win_text, (win_width // 2 - 200, win_height // 2 - 50))
                    display.update()
                    time.sleep(3)
                    game = False

            display.update()
            time.sleep(0.05)
        elif game_paused and current_menu == "pause":
            show_pause_menu()

    elif current_menu == "main":
        draw_main_menu()
    elif current_menu == "missions":
        draw_missions_menu()
    elif current_menu == "modes":
        draw_modes_menu()
    elif current_menu == "boss_mission_menu":
        draw_boss_mission_menu()

quit()