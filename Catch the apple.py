import pygame
import random
import time

pygame.init()

# Ekran o'lchami
display_info = pygame.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Catch the Apple")

# Ranglar
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (160, 160, 160)

# Fontlar
FONT = pygame.font.SysFont("Arial", 36)
BIG_FONT = pygame.font.SysFont("Arial", 72)

# Rasm o'rnini bosuvchi obyektlar
basket_img = pygame.Surface((100, 60))
basket_img.fill((200, 200, 0))

apple_img = pygame.Surface((40, 40))
apple_img.fill((255, 0, 0))

golden_apple_img = pygame.Surface((40, 40))
golden_apple_img.fill((255, 215, 0))

tnt_img = pygame.Surface((40, 40))
tnt_img.fill((100, 0, 0))

apple_logo_img = pygame.Surface((40, 40))
apple_logo_img.fill((128, 128, 128))

# Basket
basket = basket_img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
basket_speed = 10

# Obyektlar ro'yxati
objects = []
spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_event, 1500)

score = 0
lives = 3
high_score = 0
shop_points = 0

# Effektlar
effects = {
    "never_died": 0,
    "slow_walk": 0,
    "speed": 1,
    "shield": False,
    "shield_time": 0
}

# Shop
shop_open = False
skins = {
    "ugly": {"cost": 10},
    "normal": {"cost": 15},
    "cool": {"cost": 20}
}
selected_skin = None

def reset():
    global score, lives, effects, objects, basket_speed
    score = 0
    lives = 3
    objects.clear()
    effects = {"never_died": 0, "slow_walk": 0, "speed": 1, "shield": False, "shield_time": 0}
    basket_speed = 10

def spawn_object():
    obj_type = "apple"
    chance = random.randint(1, 100)
    if score >= 10 and chance <= 34:
        obj_type = "tnt"
    elif chance <= 18:
        obj_type = "golden_apple"
    elif (score < 10 and chance <= 8) or (score >= 10 and chance <= 23):
        obj_type = "apple_logo"
    x = random.randint(20, WIDTH - 60)
    rect = pygame.Rect(x, -40, 40, 40)
    objects.append({"type": obj_type, "rect": rect})

def draw_text(text, x, y, font=FONT, color=WHITE):
    label = font.render(text, True, color)
    SCREEN.blit(label, (x, y))

def update_effects():
    current_time = time.time()
    for key in ["never_died", "slow_walk"]:
        if effects[key] > 0 and effects[key] < current_time:
            effects[key] = 0
    if effects["shield"] and effects["shield_time"] < current_time:
        effects["shield"] = False

def apply_effect(obj_type):
    global lives, score, shop_points, effects
    if obj_type == "apple":
        score += 1
    elif obj_type == "golden_apple":
        score += 5
        if effects["never_died"] > time.time():
            effects["never_died"] += 15
        else:
            effects["never_died"] = time.time() + 15
    elif obj_type == "apple_logo":
        effects["slow_walk"] = time.time() + 15
    elif obj_type == "tnt":
        if not effects["never_died"] and not effects["shield"]:
            lives -= 1

def draw_objects():
    for obj in objects:
        img = apple_img
        if obj["type"] == "golden_apple":
            img = golden_apple_img
        elif obj["type"] == "tnt":
            img = tnt_img
        elif obj["type"] == "apple_logo":
            img = apple_logo_img
        SCREEN.blit(img, obj["rect"])

def draw_shop():
    pygame.draw.rect(SCREEN, BLACK, (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
    draw_text("Shop", WIDTH // 2 - 50, HEIGHT // 4 + 20, BIG_FONT)
    y = HEIGHT // 4 + 100
    for i, (name, item) in enumerate(skins.items()):
        color = WHITE if shop_points >= item["cost"] else GRAY
        draw_text(f"{name.capitalize()} skin - {item['cost']}p", WIDTH // 2 - 150, y + i * 50, FONT, color)

    effect_y = y + len(skins) * 50 + 40
    draw_text("Speed Boost (S) - 10p", WIDTH // 2 - 150, effect_y, FONT, WHITE)
    draw_text("Shield (D) - 15p", WIDTH // 2 - 150, effect_y + 40, FONT, WHITE)

    draw_text("Press 1/2/3/S/D to buy", WIDTH // 2 - 150, effect_y + 100, FONT)

def game_loop():
    global basket_speed, shop_open, shop_points, high_score, selected_skin, effects, score, lives
    clock = pygame.time.Clock()
    running = True
    while running:
        SCREEN.fill(BLACK)
        update_effects()
        speed = basket_speed * effects["speed"]
        if effects["slow_walk"]:
            speed = max(3, speed // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == spawn_event:
                spawn_object()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s and shop_open and shop_points >= 10:
                    effects["speed"] = 2
                    pygame.time.set_timer(pygame.USEREVENT + 2, 15000, True)
                    shop_points -= 10
                elif event.key == pygame.K_d and shop_open and shop_points >= 15:
                    effects["shield"] = True
                    effects["shield_time"] = time.time() + 10
                    shop_points -= 15
                elif event.key == pygame.K_s:
                    shop_open = not shop_open
                elif event.key == pygame.K_SPACE and effects["shield_time"] <= time.time():
                    if "shield" in effects:
                        effects["shield"] = True
                        effects["shield_time"] = time.time() + 10
                elif shop_open:
                    if event.key == pygame.K_1 and shop_points >= skins["ugly"]["cost"]:
                        selected_skin = "ugly"
                        shop_points -= skins["ugly"]["cost"]
                    elif event.key == pygame.K_2 and shop_points >= skins["normal"]["cost"]:
                        selected_skin = "normal"
                        shop_points -= skins["normal"]["cost"]
                    elif event.key == pygame.K_3 and shop_points >= skins["cool"]["cost"]:
                        selected_skin = "cool"
                        shop_points -= skins["cool"]["cost"]

            elif event.type == pygame.USEREVENT + 2:
                effects["speed"] = 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            basket.x -= speed
        if keys[pygame.K_RIGHT]:
            basket.x += speed
        basket.x = max(0, min(WIDTH - basket.width, basket.x))

        for obj in objects[:]:
            obj["rect"].y += 5
            if obj["rect"].colliderect(basket):
                apply_effect(obj["type"])
                objects.remove(obj)
            elif obj["rect"].top > HEIGHT:
                if obj["type"] == "apple" and not effects["never_died"] and not effects["shield"]:
                    lives -= 1
                objects.remove(obj)

        if score > high_score:
            high_score = score
        shop_points = score // 10

        SCREEN.blit(basket_img, basket)
        draw_objects()
        draw_text(f"Score: {score}", 20, 20)
        draw_text(f"Lives: {lives}", 20, 60)
        draw_text(f"High Score: {high_score}", 20, 100)
        draw_text(f"Shop Points: {shop_points}", 20, 140)
        if effects["never_died"] > time.time():
            remaining = int(effects["never_died"] - time.time())
            draw_text(f"Never Died: {remaining}s", WIDTH - 300, 20)
        if effects["shield"]:
            draw_text("Shield Active", WIDTH - 300, 60)
        if effects["slow_walk"] > time.time():
            draw_text("Slow Walk", WIDTH - 300, 100)
        if shop_open:
            draw_shop()

        if lives <= 0:
            draw_text("Game Over", WIDTH // 2 - 150, HEIGHT // 2 - 60, BIG_FONT)
            draw_text("Try Again (R) or Quit (ESC)", WIDTH // 2 - 250, HEIGHT // 2 + 20)
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            reset()
                            waiting = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return

        pygame.display.flip()
        clock.tick(60)

game_loop()
pygame.quit()