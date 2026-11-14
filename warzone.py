import pygame
import random
import math
import array
import sys

# =========================================================
# WARZONE: OPERACION ESPECIAL
# =========================================================

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
    pygame.mixer.set_num_channels(12)
except pygame.error:
    SOUND_AVAILABLE = False

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("WARZONE - Operacion Especial")

clock = pygame.time.Clock()
FPS = 60

sound_on = True
running = True

# =========================================================
# COLORES
# =========================================================

WHITE = (240, 240, 230)
BLACK = (10, 12, 10)
RED = (210, 45, 40)
GREEN = (70, 190, 85)
YELLOW = (240, 195, 65)

TERRAIN = (65, 72, 54)
DARK_TERRAIN = (48, 54, 41)
GRASS = (79, 91, 55)
DIRT = (100, 86, 62)
WOOD = (93, 66, 42)

FONT = pygame.font.SysFont("arial", 23, bold=True)
SMALL = pygame.font.SysFont("arial", 16, bold=True)
TITLE = pygame.font.SysFont("arial", 75, bold=True)

# =========================================================
# SONIDOS
# =========================================================

def create_sound(frequency, duration, volume=0.3):
    if not SOUND_AVAILABLE:
        return None

    rate = 22050
    samples = array.array("h")

    for i in range(int(rate * duration)):
        t = i / rate
        envelope = math.exp(-t * 12)

        wave = math.sin(2 * math.pi * frequency * t)
        noise = random.uniform(-0.5, 0.5)

        value = (wave * 0.65 + noise * 0.35)
        value *= envelope * volume

        samples.append(int(value * 32767))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def create_war_music():
    if not SOUND_AVAILABLE:
        return None

    rate = 22050
    duration = 8
    samples = array.array("h")

    melody = [
        110, 110, 146, 130,
        110, 98, 110, 146,
        164, 146, 130, 110,
        98, 110, 130, 98
    ]

    for i in range(rate * duration):
        t = i / rate

        beat = int(t * 2)
        position = (t * 2) % 1

        bass_frequency = 55 if beat % 4 in (0, 2) else 65

        bass = math.sin(
            2 * math.pi * bass_frequency * t
        ) * 0.20

        note = melody[int(t * 2) % len(melody)]

        melody_wave = math.sin(
            2 * math.pi * note * t
        ) * 0.10

        drum = 0

        if position < 0.12 and beat % 2 == 0:
            envelope = math.exp(-position * 30)
            drum = math.sin(2 * math.pi * 65 * t)
            drum *= envelope * 0.42

        percussion = 0

        if 0.48 < position < 0.56:
            percussion = random.uniform(-0.16, 0.16)

        atmosphere = math.sin(
            2 * math.pi * 35 * t
        ) * 0.035

        value = bass + melody_wave + drum + percussion + atmosphere
        value = max(-0.95, min(0.95, value))

        samples.append(int(value * 32767))

    return pygame.mixer.Sound(buffer=samples.tobytes())


music = create_war_music()

shoot_sound = create_sound(100, 0.12, 0.35)
hit_sound = create_sound(65, 0.18, 0.3)
shield_sound = create_sound(300, 0.2, 0.25)
menu_sound = create_sound(500, 0.08, 0.15)

music_channel = None

if SOUND_AVAILABLE:
    music_channel = pygame.mixer.Channel(11)


def play_sound(sound):
    if sound_on and SOUND_AVAILABLE and sound is not None:
        sound.play()


def start_music():
    if (
        SOUND_AVAILABLE
        and music_channel
        and music is not None
        and sound_on
        and not music_channel.get_busy()
    ):
        music_channel.play(music, loops=-1)


def stop_music():
    if music_channel:
        music_channel.stop()


def toggle_sound():
    global sound_on

    sound_on = not sound_on

    if sound_on:
        start_music()
    else:
        stop_music()


# =========================================================
# FUNCIONES GENERALES
# =========================================================

def draw_text(surface, text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))

    surface.blit(image, rect)


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def normalize(dx, dy):
    length = math.hypot(dx, dy)

    if length == 0:
        return 0, 0

    return dx / length, dy / length


# =========================================================
# MAPA
# =========================================================

terrain_surface = pygame.Surface((WIDTH, HEIGHT))
terrain_surface.fill(TERRAIN)

random.seed(25)

for i in range(250):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)

    radius = random.randint(8, 35)

    color = random.choice([
        DARK_TERRAIN,
        DIRT,
        GRASS,
        (58, 66, 48)
    ])

    pygame.draw.circle(
        terrain_surface,
        color,
        (x, y),
        radius
    )

for i in range(700):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)

    color = random.choice([
        (66, 85, 47),
        (83, 100, 55),
        (45, 62, 39)
    ])

    pygame.draw.line(
        terrain_surface,
        color,
        (x, y),
        (x + random.randint(-3, 3), y - random.randint(2, 7)),
        2
    )

for i in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)

    pygame.draw.ellipse(
        terrain_surface,
        (95, 94, 78),
        (x, y, 8, 5)
    )

random.seed()


def draw_background():
    screen.blit(terrain_surface, (0, 0))


# =========================================================
# OBSTACULOS
# =========================================================

def create_obstacles():
    obstacles = []

    positions = [
        (0.23, 0.25),
        (0.50, 0.18),
        (0.76, 0.30),
        (0.30, 0.70),
        (0.65, 0.72),
        (0.85, 0.55)
    ]

    for px, py in positions:
        w = random.randint(75, 115)
        h = random.randint(45, 70)

        rect = pygame.Rect(
            int(WIDTH * px),
            int(HEIGHT * py),
            w,
            h
        )

        obstacles.append(rect)

    return obstacles


def blocked(x, y, obstacles, radius=18):
    rect = pygame.Rect(
        int(x - radius),
        int(y - radius),
        radius * 2,
        radius * 2
    )

    for obstacle in obstacles:
        if rect.colliderect(obstacle):
            return True

    return False


def draw_obstacles(obstacles):
    for rect in obstacles:

        pygame.draw.rect(
            screen,
            (25, 27, 23),
            rect.move(6, 8),
            border_radius=5
        )

        pygame.draw.rect(
            screen,
            WOOD,
            rect,
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            (135, 99, 61),
            rect,
            3,
            border_radius=4
        )

        for y in range(rect.top + 8, rect.bottom, 15):
            pygame.draw.line(
                screen,
                (50, 39, 27),
                (rect.left + 5, y),
                (rect.right - 5, y),
                3
            )


# =========================================================
# PARTICULAS
# =========================================================

particles = []


class Particle:

    def __init__(self, x, y, color=None):
        self.x = float(x)
        self.y = float(y)

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.life = random.randint(15, 35)
        self.max_life = self.life

        self.size = random.randint(2, 5)

        self.color = color or random.choice([
            (240, 125, 40),
            (240, 195, 65),
            (150, 145, 125),
            (90, 90, 85)
        ])

    def update(self):
        self.x += self.dx
        self.y += self.dy

        self.dx *= 0.94
        self.dy *= 0.94

        self.life -= 1

    def draw(self):
        if self.life <= 0:
            return

        alpha = self.life / self.max_life
        size = max(1, int(self.size * alpha))

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            size
        )


def create_particles(x, y, amount=12):
    for i in range(amount):
        particles.append(Particle(x, y))


def update_particles():
    for particle in particles[:]:
        particle.update()

        if particle.life <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        particle.draw()


# =========================================================
# PERSONAJES
# =========================================================

def create_soldier_sprite(enemy=False):
    sprite = pygame.Surface((100, 100), pygame.SRCALPHA)

    body = (83, 105, 58) if not enemy else (125, 62, 48)
    dark = (40, 53, 34) if not enemy else (68, 35, 29)

    # Mochila
    pygame.draw.rect(
        sprite,
        dark,
        (28, 36, 30, 33),
        border_radius=7
    )

    # Piernas
    pygame.draw.line(
        sprite,
        dark,
        (42, 59),
        (38, 78),
        11
    )

    pygame.draw.line(
        sprite,
        dark,
        (58, 59),
        (62, 78),
        11
    )

    # Botas
    pygame.draw.ellipse(
        sprite,
        (25, 25, 22),
        (27, 70, 20, 10)
    )

    pygame.draw.ellipse(
        sprite,
        (25, 25, 22),
        (55, 70, 20, 10)
    )

    # Brazos
    pygame.draw.line(
        sprite,
        body,
        (38, 42),
        (27, 56),
        11
    )

    pygame.draw.line(
        sprite,
        body,
        (61, 42),
        (70, 54),
        11
    )

    # Cuerpo
    pygame.draw.ellipse(
        sprite,
        body,
        (35, 31, 32, 37)
    )

    # Chaleco
    pygame.draw.rect(
        sprite,
        dark,
        (39, 35, 25, 29),
        border_radius=5
    )

    pygame.draw.rect(
        sprite,
        (110, 112, 75),
        (43, 39, 5, 8)
    )

    pygame.draw.rect(
        sprite,
        (110, 112, 75),
        (54, 39, 5, 8)
    )

    # Cabeza
    pygame.draw.circle(
        sprite,
        (170, 135, 105),
        (51, 28),
        11
    )

    # Casco
    pygame.draw.arc(
        sprite,
        (65, 85, 45),
        (39, 13, 24, 23),
        math.pi,
        2 * math.pi,
        9
    )

    pygame.draw.line(
        sprite,
        (40, 55, 30),
        (39, 27),
        (63, 27),
        4
    )

    # Visor
    pygame.draw.line(
        sprite,
        (25, 30, 25),
        (44, 27),
        (58, 27),
        3
    )

    # Rifle
    pygame.draw.line(
        sprite,
        (22, 23, 20),
        (56, 48),
        (88, 48),
        7
    )

    pygame.draw.line(
        sprite,
        (120, 125, 110),
        (59, 46),
        (85, 46),
        2
    )

    return sprite


player_sprite = create_soldier_sprite(False)
enemy_sprite = create_soldier_sprite(True)


class Soldier:

    def __init__(self, x, y, enemy=False):
        self.x = float(x)
        self.y = float(y)

        self.enemy = enemy

        self.speed = 3.0 if not enemy else 2.1

        self.health = 100
        self.max_health = 100

        self.angle = 0

        self.cooldown = 0
        self.shield_time = 0
        self.muzzle_flash = 0

        self.radius = 18
        self.dead = False

        self.sprite = enemy_sprite if enemy else player_sprite

    def move(self, dx, dy, obstacles):
        if self.dead:
            return

        dx, dy = normalize(dx, dy)

        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed

        if not blocked(nx, self.y, obstacles, self.radius):
            self.x = max(25, min(WIDTH - 25, nx))

        if not blocked(self.x, ny, obstacles, self.radius):
            self.y = max(25, min(HEIGHT - 25, ny))

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        if self.shield_time > 0:
            self.shield_time -= 1

        if self.muzzle_flash > 0:
            self.muzzle_flash -= 1

    def shoot(self, bullets):
        if self.dead or self.cooldown > 0:
            return

        self.cooldown = 22
        self.muzzle_flash = 5

        dx = math.cos(self.angle)
        dy = math.sin(self.angle)

        start_x = self.x + dx * 32
        start_y = self.y + dy * 32

        bullets.append(
            Bullet(start_x, start_y, dx, dy, self.enemy)
        )

        create_particles(start_x, start_y, 3)
        play_sound(shoot_sound)

    def shield(self):
        if self.shield_time <= 0:
            self.shield_time = 100
            play_sound(shield_sound)

    def damage(self, amount):
        if self.shield_time > 0:
            amount *= 0.25

        self.health -= amount

        create_particles(self.x, self.y, 8)
        play_sound(hit_sound)

        if self.health <= 0:
            self.health = 0
            self.dead = True
            create_particles(self.x, self.y, 30)

    def draw(self):
        if self.dead:
            return

        pygame.draw.ellipse(
            screen,
            (20, 22, 17),
            (self.x - 24, self.y - 13, 48, 38)
        )

        rotated = pygame.transform.rotate(
            self.sprite,
            -math.degrees(self.angle)
        )

        rect = rotated.get_rect(
            center=(int(self.x), int(self.y))
        )

        screen.blit(rotated, rect)

        if self.shield_time > 0:
            pygame.draw.circle(
                screen,
                (60, 165, 255),
                (int(self.x), int(self.y)),
                36,
                3
            )

        if self.muzzle_flash > 0:
            fx = self.x + math.cos(self.angle) * 43
            fy = self.y + math.sin(self.angle) * 43

            pygame.draw.circle(
                screen,
                (255, 190, 40),
                (int(fx), int(fy)),
                random.randint(5, 9)
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (int(fx), int(fy)),
                3
            )

        pygame.draw.rect(
            screen,
            BLACK,
            (self.x - 22, self.y - 43, 44, 7)
        )

        pygame.draw.rect(
            screen,
            RED,
            (self.x - 22, self.y - 43, 44, 7)
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x - 22,
                self.y - 43,
                44 * self.health / 100,
                7
            )
        )


# =========================================================
# BALAS
# =========================================================

class Bullet:

    def __init__(self, x, y, dx, dy, enemy):
        self.x = x
        self.y = y

        self.dx = dx
        self.dy = dy

        self.enemy = enemy

        self.speed = 12
        self.life = 70
        self.radius = 4

        self.old_x = x
        self.old_y = y

    def update(self):
        self.old_x = self.x
        self.old_y = self.y

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        self.life -= 1

    def draw(self):
        color = RED if self.enemy else YELLOW

        pygame.draw.line(
            screen,
            color,
            (int(self.old_x), int(self.old_y)),
            (int(self.x), int(self.y)),
            3
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.x), int(self.y)),
            2
        )


# =========================================================
# INTELIGENCIA ARTIFICIAL
# =========================================================

def enemy_ai(enemy, player, bullets, obstacles):
    if enemy.dead or player.dead:
        return

    dx = player.x - enemy.x
    dy = player.y - enemy.y

    dist = math.hypot(dx, dy)

    if dist == 0:
        return

    enemy.angle = math.atan2(dy, dx)

    if dist > 240:
        move_x = dx / dist
        move_y = dy / dist

    elif dist < 145:
        move_x = -dx / dist
        move_y = -dy / dist

    else:
        move_x = -dy / dist * 0.55
        move_y = dx / dist * 0.55

    directions = [
        (move_x, move_y),
        (move_x + 0.8, move_y),
        (move_x - 0.8, move_y),
        (move_x, move_y + 0.8),
        (move_x, move_y - 0.8),
        (-move_y, move_x),
        (move_y, -move_x)
    ]

    moved = False

    for mx, my in directions:
        nx, ny = normalize(mx, my)

        if not blocked(
            enemy.x + nx * enemy.speed * 3,
            enemy.y + ny * enemy.speed * 3,
            obstacles,
            enemy.radius
        ):
            enemy.move(nx, ny, obstacles)
            moved = True
            break

    if not moved:
        for _ in range(12):
            angle = random.uniform(0, math.pi * 2)

            mx = math.cos(angle)
            my = math.sin(angle)

            if not blocked(
                enemy.x + mx * 25,
                enemy.y + my * 25,
                obstacles
            ):
                enemy.move(mx, my, obstacles)
                break

    if dist < 700:
        enemy.shoot(bullets)


# =========================================================
# MINIMAPA
# =========================================================

def draw_minimap(player, enemy, obstacles):
    size = 155

    x = WIDTH - size - 22
    y = HEIGHT - size - 22

    panel = pygame.Rect(x, y, size, size)

    pygame.draw.rect(
        screen,
        (15, 20, 16),
        panel,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        (115, 130, 100),
        panel,
        2,
        border_radius=8
    )

    scale_x = size / WIDTH
    scale_y = size / HEIGHT

    for obstacle in obstacles:
        rect = pygame.Rect(
            int(x + obstacle.x * scale_x),
            int(y + obstacle.y * scale_y),
            max(2, int(obstacle.width * scale_x)),
            max(2, int(obstacle.height * scale_y))
        )

        pygame.draw.rect(screen, (145, 125, 88), rect)

    pygame.draw.circle(
        screen,
        GREEN,
        (
            int(x + player.x * scale_x),
            int(y + player.y * scale_y)
        ),
        5
    )

    pygame.draw.circle(
        screen,
        RED,
        (
            int(x + enemy.x * scale_x),
            int(y + enemy.y * scale_y)
        ),
        5
    )

    draw_text(
        screen,
        "RADAR",
        SMALL,
        WHITE,
        x + size // 2,
        y - 12
    )


# =========================================================
# HUD
# =========================================================

def draw_hud(player, enemy, obstacles):
    pygame.draw.rect(
        screen,
        (18, 24, 19),
        (18, 18, 255, 95),
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        (110, 130, 90),
        (18, 18, 255, 95),
        2,
        border_radius=8
    )

    draw_text(
        screen,
        "SOLDADO ALIADO",
        SMALL,
        WHITE,
        32,
        28,
        False
    )

    pygame.draw.rect(
        screen,
        RED,
        (32, 60, 220, 17)
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (32, 60, 220 * player.health / 100, 17)
    )

    draw_text(
        screen,
        f"VIDA: {player.health}/100",
        SMALL,
        WHITE,
        32,
        83,
        False
    )

    pygame.draw.rect(
        screen,
        (18, 24, 19),
        (WIDTH - 273, 18, 255, 95),
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        (130, 80, 70),
        (WIDTH - 273, 18, 255, 95),
        2,
        border_radius=8
    )

    draw_text(
        screen,
        "ENEMIGO",
        SMALL,
        WHITE,
        WIDTH - 257,
        28,
        False
    )

    pygame.draw.rect(
        screen,
        RED,
        (WIDTH - 257, 60, 220, 17)
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            WIDTH - 257,
            60,
            220 * enemy.health / 100,
            17
        )
    )

    draw_text(
        screen,
        f"VIDA: {enemy.health}/100",
        SMALL,
        WHITE,
        WIDTH - 257,
        83,
        False
    )

    pygame.draw.rect(
        screen,
        (18, 24, 19),
        (WIDTH // 2 - 250, HEIGHT - 43, 500, 28),
        border_radius=6
    )

    draw_text(
        screen,
        "WASD MOVER | F DISPARAR | G ESCUDO | ESC PAUSA",
        SMALL,
        WHITE,
        WIDTH // 2,
        HEIGHT - 29
    )

    draw_minimap(player, enemy, obstacles)


# =========================================================
# MIRA DEL RATON
# =========================================================

def draw_crosshair():
    mx, my = pygame.mouse.get_pos()

    pygame.draw.circle(
        screen,
        WHITE,
        (mx, my),
        12,
        1
    )

    pygame.draw.line(
        screen,
        WHITE,
        (mx - 18, my),
        (mx - 5, my),
        2
    )

    pygame.draw.line(
        screen,
        WHITE,
        (mx + 5, my),
        (mx + 18, my),
        2
    )

    pygame.draw.line(
        screen,
        WHITE,
        (mx, my - 18),
        (mx, my - 5),
        2
    )

    pygame.draw.line(
        screen,
        WHITE,
        (mx, my + 5),
        (mx, my + 18),
        2
    )


# =========================================================
# SISTEMA DE MENUS
# =========================================================

def draw_menu(title, options, selected, subtitle=None):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 9, 7, 215))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(
        WIDTH // 2 - 280,
        HEIGHT // 2 - 250,
        560,
        500
    )

    pygame.draw.rect(
        screen,
        (23, 31, 25),
        panel,
        border_radius=14
    )

    pygame.draw.rect(
        screen,
        (115, 140, 95),
        panel,
        2,
        border_radius=14
    )

    draw_text(
        screen,
        title,
        TITLE,
        (205, 220, 180),
        WIDTH // 2,
        HEIGHT // 2 - 175
    )

    if subtitle:
        draw_text(
            screen,
            subtitle,
            FONT,
            WHITE,
            WIDTH // 2,
            HEIGHT // 2 - 115
        )

    rects = []

    start_y = HEIGHT // 2 - 45

    for i, option in enumerate(options):
        y = start_y + i * 65

        rect = pygame.Rect(
            WIDTH // 2 - 190,
            y - 23,
            380,
            48
        )

        color = YELLOW if selected == i else WHITE

        if selected == i:
            pygame.draw.rect(
                screen,
                (70, 85, 60),
                rect,
                border_radius=7
            )

            pygame.draw.rect(
                screen,
                YELLOW,
                rect,
                2,
                border_radius=7
            )

        draw_text(
            screen,
            option,
            FONT,
            color,
            WIDTH // 2,
            y
        )

        rects.append(rect)

    draw_text(
        screen,
        "FLECHAS: MOVER | ENTER: SELECCIONAR",
        SMALL,
        WHITE,
        WIDTH // 2,
        HEIGHT // 2 + 210
    )

    return rects


def menu_loop(title, options, subtitle=None):
    selected = 0

    while True:
        clock.tick(FPS)

        draw_background()

        rects = draw_menu(
            title,
            options,
            selected,
            subtitle
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                stop_music()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    play_sound(menu_sound)

                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    play_sound(menu_sound)

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    play_sound(menu_sound)
                    return options[selected]

                elif event.key == pygame.K_ESCAPE:
                    return None

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        selected = i

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            play_sound(menu_sound)
                            return options[i]


# =========================================================
# PAUSA
# =========================================================

def pause_menu():
    stop_music()

    while True:
        choice = menu_loop(
            "PAUSA",
            [
                "CONTINUAR",
                "REINICIAR",
                "SONIDO ON/OFF",
                "MENU PRINCIPAL",
                "SALIR"
            ],
            "MISION SUSPENDIDA"
        )

        if choice == "CONTINUAR":
            start_music()
            return "continue"

        elif choice == "REINICIAR":
            return "restart"

        elif choice == "SONIDO ON/OFF":
            toggle_sound()

        elif choice == "MENU PRINCIPAL":
            return "menu"

        elif choice == "SALIR" or choice is None:
            return "quit"


# =========================================================
# GAME OVER Y VICTORIA
# =========================================================

def game_over():
    stop_music()

    choice = menu_loop(
        "MISION FALLIDA",
        [
            "REINTENTAR",
            "MENU PRINCIPAL",
            "SALIR"
        ],
        "HAS SIDO ELIMINADO"
    )

    if choice == "REINTENTAR":
        return "restart"

    if choice == "MENU PRINCIPAL":
        return "menu"

    return "quit"


def victory_screen():
    stop_music()

    choice = menu_loop(
        "VICTORIA",
        [
            "JUGAR OTRA VEZ",
            "MENU PRINCIPAL",
            "SALIR"
        ],
        "OBJETIVO ELIMINADO - MISION COMPLETADA"
    )

    if choice == "JUGAR OTRA VEZ":
        return "restart"

    if choice == "MENU PRINCIPAL":
        return "menu"

    return "quit"


# =========================================================
# ACTUALIZACION DE BALAS
# =========================================================

def update_bullets(bullets, player, enemy, obstacles):

    for bullet in bullets[:]:
        bullet.update()

        remove = False

        if bullet.life <= 0:
            remove = True

        if not (0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT):
            remove = True

        for obstacle in obstacles:
            if obstacle.collidepoint(bullet.x, bullet.y):
                create_particles(bullet.x, bullet.y, 5)
                remove = True
                break

        if not remove:

            if bullet.enemy:
                if distance(
                    bullet.x,
                    bullet.y,
                    player.x,
                    player.y
                ) < player.radius + bullet.radius:
                    player.damage(20)
                    remove = True

            else:
                if distance(
                    bullet.x,
                    bullet.y,
                    enemy.x,
                    enemy.y
                ) < enemy.radius + bullet.radius:
                    enemy.damage(20)
                    remove = True

        if remove and bullet in bullets:
            bullets.remove(bullet)


# =========================================================
# PARTIDA
# =========================================================

def game():
    global particles

    particles = []

    player = Soldier(
        WIDTH * 0.15,
        HEIGHT * 0.50,
        False
    )

    enemy = Soldier(
        WIDTH * 0.82,
        HEIGHT * 0.50,
        True
    )

    obstacles = create_obstacles()
    bullets = []

    start_music()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                stop_music()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()

                    if result in ("restart", "menu", "quit"):
                        return result

                elif event.key == pygame.K_g:
                    player.shield()

                elif event.key == pygame.K_f:
                    player.shoot(bullets)

                elif event.key == pygame.K_m:
                    toggle_sound()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.shoot(bullets)

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        player.move(dx, dy, obstacles)

        mx, my = pygame.mouse.get_pos()

        player.angle = math.atan2(
            my - player.y,
            mx - player.x
        )

        player.update()
        enemy.update()

        enemy_ai(
            enemy,
            player,
            bullets,
            obstacles
        )

        update_bullets(
            bullets,
            player,
            enemy,
            obstacles
        )

        update_particles()

        # DIBUJAR TODO
        draw_background()

        draw_obstacles(obstacles)

        for bullet in bullets:
            bullet.draw()

        player.draw()
        enemy.draw()

        draw_particles()

        draw_hud(
            player,
            enemy,
            obstacles
        )

        draw_crosshair()

        pygame.display.flip()

        if player.dead:
            return game_over()

        if enemy.dead:
            return victory_screen()


# =========================================================
# MENU PRINCIPAL
# =========================================================

def main_menu():

    while True:
        choice = menu_loop(
            "WARZONE",
            [
                "JUGAR",
                "SONIDO ON/OFF",
                "SALIR"
            ],
            "TACTICAL COMBAT - OPERACION ESPECIAL"
        )

        if choice == "JUGAR":
            return "play"

        elif choice == "SONIDO ON/OFF":
            toggle_sound()

        elif choice == "SALIR" or choice is None:
            return "quit"


# =========================================================
# BUCLE PRINCIPAL
# =========================================================

def main():

    while True:

        choice = main_menu()

        if choice == "quit":
            break

        if choice == "play":

            while True:
                result = game()

                if result == "restart":
                    continue

                elif result == "menu":
                    break

                elif result == "quit":
                    stop_music()
                    pygame.quit()
                    sys.exit()

                else:
                    break

    stop_music()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()