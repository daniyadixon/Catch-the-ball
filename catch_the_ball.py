import pygame
import random
import sys
import cv2
import mediapipe as mp

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Ball - Hand Gesture Edition")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
RED = (255, 0, 0)
GREEN = (50, 200, 50)
YELLOW = (255, 220, 0)
GRAY = (220, 220, 220)

# Clock and fonts
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

# Load images
basket_img = pygame.image.load("basket.PNG").convert_alpha()
ball_img = pygame.image.load("ball.JPG").convert_alpha()
basket_img = pygame.transform.scale(basket_img, (120, 40))
ball_img = pygame.transform.scale(ball_img, (40, 40))

# Load sounds
catch_sound = pygame.mixer.Sound("catch.wav")
miss_sound = pygame.mixer.Sound("miss.wav")
level_up_sound = pygame.mixer.Sound("level_up.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")

catch_sound.set_volume(0.6)
miss_sound.set_volume(0.6)
level_up_sound.set_volume(0.7)
game_over_sound.set_volume(0.7)

# Game variables
basket_x = WIDTH // 2 - 60
basket_y = HEIGHT - 70
ball_x = random.randint(20, WIDTH - 60)
ball_y = 0
ball_speed = 5
score = 0
lives = 3
level = 1
next_level_score = 10
player_name = ""

# Initialize Mediapipe for hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)


def draw_text(text, size, color, x, y, center=True):
    font_obj = pygame.font.Font(None, size)
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


def get_player_name():
    """Ask the player to enter their name before starting"""
    global player_name
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)
    active = False
    player_name = ""

    while True:
        screen.fill(WHITE)
        draw_text("Enter Your Name", 60, BLUE, WIDTH // 2, HEIGHT // 2 - 100)

        pygame.draw.rect(screen, GRAY if not active else BLUE, input_box, 2)
        name_surface = font.render(player_name, True, BLACK)
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))

        draw_text("Press ENTER to continue", 30, BLACK, WIDTH // 2, HEIGHT // 2 + 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip() != "":
                            return
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

        pygame.display.flip()
        clock.tick(30)


def show_level_popup_message(level):
    """Show popup text in center for 2 seconds"""
    level_up_sound.play()
    screen.fill(WHITE)
    draw_text(f"LEVEL {level}!", 100, YELLOW, WIDTH // 2, HEIGHT // 2 - 50)
    draw_text("Get ready...", 50, BLUE, WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()
    pygame.time.delay(1500)


def start_screen():
    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
    while True:
        screen.fill(WHITE)
        draw_text("Catch the Ball", 80, BLUE, WIDTH // 2, HEIGHT // 2 - 150)
        pygame.draw.rect(screen, GREEN, start_button)
        draw_text("Start Game", 40, WHITE, WIDTH // 2, HEIGHT // 2 + 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                get_player_name()
                return
        pygame.display.flip()
        clock.tick(30)


def game_loop():
    global basket_x, ball_x, ball_y, ball_speed, score, lives, level, next_level_score

    score = 0
    lives = 3
    level = 1
    next_level_score = 10
    ball_speed = 5

    running = True
    while running:
        screen.fill(WHITE)

        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)  # mirror image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Track hand position
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                index_x = int(hand_landmarks.landmark[8].x * w)
                basket_x = int(index_x / w * WIDTH) - 60
                basket_x = max(0, min(basket_x, WIDTH - 120))
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Move ball
        ball_y += ball_speed

        # Rectangles for collision
        basket_rect = pygame.Rect(basket_x, HEIGHT - 70, 120, 40)
        ball_rect = pygame.Rect(ball_x, ball_y, 40, 40)

        # Catch ball
        if basket_rect.colliderect(ball_rect):
            catch_sound.play()
            score += 1
            ball_y = 0
            ball_x = random.randint(20, WIDTH - 60)

        # Miss ball
        if ball_y > HEIGHT:
            miss_sound.play()
            lives -= 1
            ball_y = 0
            ball_x = random.randint(20, WIDTH - 60)
            if lives == 0:
                game_over_sound.play()
                running = False

        # Level up
        if score >= next_level_score:
            level += 1
            next_level_score += 10
            ball_speed += 2
            show_level_popup_message(level)

        # Draw game objects
        screen.blit(basket_img, (basket_x, HEIGHT - 70))
        screen.blit(ball_img, (ball_x, ball_y))

        # Display info
        draw_text(f"Player: {player_name}", 30, BLACK, 10, 10, center=False)
        draw_text(f"Score: {score}", 30, BLACK, 10, 40, center=False)
        draw_text(f"Lives: {lives}", 30, BLACK, WIDTH - 150, 10, center=False)
        draw_text(f"Level: {level}", 30, BLACK, WIDTH // 2 - 50, 10, center=False)

        pygame.display.flip()
        clock.tick(60)

        # Optional webcam feed
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            running = False

    show_scoreboard()


def show_scoreboard():
    """Display scoreboard with player's name, score, and level"""
    while True:
        screen.fill(WHITE)
        draw_text("GAME OVER", 80, RED, WIDTH // 2, HEIGHT // 2 - 150)
        draw_text(f"Name: {player_name}", 50, BLUE, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Score: {score}", 50, BLACK, WIDTH // 2, HEIGHT // 2 + 20)
        draw_text(f"Level Reached: {level}", 50, BLACK, WIDTH // 2, HEIGHT // 2 + 90)
        draw_text("Click anywhere to play again", 36, GREEN, WIDTH // 2, HEIGHT // 2 + 180)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(30)


# --- MAIN LOOP ---
while True:
    start_screen()
    game_loop()


