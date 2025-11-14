
import pygame, sys, os, threading, urllib.request, time
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elsa - Sad Girl Game")
clock = pygame.time.Clock()

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
MUSIC_URL = "https://dl.musicdel.ir/tag/music/1400/08/14/%20-%20Tarsnak%2012%20(320).mp3"
MUSIC_PATH = os.path.join(os.path.dirname(__file__), "sad.mp3")

# Try to download music in background if not present
def download_music():
    if not os.path.exists(MUSIC_PATH):
        try:
            urllib.request.urlretrieve(MUSIC_URL, MUSIC_PATH)
            print("Music downloaded.")
        except Exception as e:
            print("Could not download music:", e)

t = threading.Thread(target=download_music, daemon=True)
t.start()

# load images
def load_image(name, fallback_rect=None):
    path = os.path.join(ASSETS, name)
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        if fallback_rect:
            surf = pygame.Surface(fallback_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surf, (200,0,0), (0,0,fallback_rect.width, fallback_rect.height))
            return surf
        raise

bg = load_image("background.png")
elsa_idle = load_image("elsa_idle.png")
elsa_walk1 = load_image("elsa_walk1.png")
elsa_walk2 = load_image("elsa_walk2.png")
elsa_jump = load_image("elsa_jump.png")
shadow_img = load_image("shadow.png")

# music (play if available)
def play_music():
    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Music not available yet or failed to load:", e)

# call play_music after a short delay to allow download
pygame.time.set_timer(pygame.USEREVENT+1, 2000)

# game variables
x, y = 50, 260
vel_y = 0
gravity = 0.9
on_ground = True
speed = 4
frame = 0
alive = True
shadow_strength = 0.0
shadow_visible = False
shadow_far_x = WIDTH + 200
finish_x = 700

# obstacles
obstacles = [pygame.Rect(320, 300, 40, 30), pygame.Rect(520, 300, 40, 30), pygame.Rect(600, 270, 40, 60)]
ground_rect = pygame.Rect(0,330,WIDTH,70)
font = pygame.font.Font(None, 36)
message_shown = False

def game_over_sequence():
    global alive, shadow_visible
    alive = False
    # shadow approaches quickly
    for i in range(30):
        screen.fill((0,0,0))
        screen.blit(bg, (0,0))
        screen.blit(shadow_img, (x-80, 50))
        pygame.display.flip()
        pygame.time.delay(30)
    # fade out
    for a in range(0,255,15):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(a)
        s.fill((0,0,0))
        screen.blit(s, (0,0))
        pygame.display.flip()
        pygame.time.delay(30)
    pygame.time.delay(800)
    show_final_message()

def show_final_message():
    text = font.render("رکب خوردی کیومرث... بازم مردودی!", True, (255,255,255))
    screen.fill((0,0,0))
    screen.blit(text, (120, 180))
    pygame.display.flip()
    pygame.time.delay(3500)
    pygame.quit()
    sys.exit()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.USEREVENT+1:
            play_music()

    keys = pygame.key.get_pressed()
    if alive:
        if keys[pygame.K_LEFT]:
            x -= speed
        if keys[pygame.K_RIGHT]:
            x += speed
        if keys[pygame.K_SPACE] and on_ground:
            vel_y = -12
            on_ground = False

    # physics
    vel_y += gravity
    y += vel_y
    if y >= 260:
        y = 260
        vel_y = 0
        on_ground = True

    player_rect = pygame.Rect(x, y, 64, 96)

    # shadow logic: shadow is visible from far away and moves slowly when player reaches certain x
    if x > 300:
        shadow_far_x -= 0.4
        shadow_visible = True
        shadow_strength = min(1.0, shadow_strength + 0.003)
    if shadow_far_x < 400:
        # increase tension (music handled externally)
        shadow_strength = min(1.0, shadow_strength + 0.01)

    # collision
    for obs in obstacles:
        if player_rect.colliderect(obs) and alive:
            # start death sequence with shadow approaching
            game_over_sequence()

    # finish line
    if player_rect.x >= finish_x and alive:
        show_final_message()

    # draw
    screen.fill((10,10,12))
    screen.blit(bg, (0,0))
    # shadow in distance
    if shadow_visible:
        sx = int(shadow_far_x - (shadow_strength*200))
        screen.blit(shadow_img, (sx, 40))
    # obstacles
    for obs in obstacles:
        pygame.draw.rect(screen, (120,120,120), obs)
    # elsa sprite selection
    if not on_ground:
        spr = elsa_jump
    else:
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            frame = (frame + 1) % 20
            spr = elsa_walk1 if frame < 10 else elsa_walk2
        else:
            spr = elsa_idle
    screen.blit(spr, (x, y-40))
    # draw ground
    pygame.draw.rect(screen, (25,25,30), ground_rect)
    # finish line
    pygame.draw.rect(screen, (200,200,200), (finish_x,0,6,HEIGHT))
    pygame.display.flip()
    clock.tick(60)
