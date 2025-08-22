import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sentry Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Game variables
health = 15
score = 0
reload_time = 3  # Starting reload time in seconds
bullet_speed = 5
last_shot_time = 0
sentry_radius = 30
sentry_pos = (WIDTH // 2, HEIGHT // 2)
crasher_radius = 20
crashers = []
bullets = []
max_crashers = 3  # Max number of crashers on screen at once
boss = None  # Boss starts as None

# Font for text
font = pygame.font.SysFont('Arial', 24)

# Load sentry image
sentry_img = pygame.image.load("sentry22.png")  # Make sure the file is in the same directory or specify the path
sentry_img = pygame.transform.scale(sentry_img, (sentry_radius * 2, sentry_radius * 2))  # Scale to match sentry size
sentry_img = pygame.transform.rotate(sentry_img, -90)

# Sentry class (using image instead of a circle)
class Sentry:
    def __init__(self, pos):
        self.pos = pos
        self.radius = sentry_radius

    def draw(self):
        # Calculate angle between sentry and mouse
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pos[0]
        dy = mouse_pos[1] - self.pos[1]
        angle = math.atan2(dy, dx)  # Angle in radians

        # Rotate image to face mouse
        rotated_img = pygame.transform.rotate(sentry_img, -math.degrees(angle))  # Rotate counter-clockwise
        rotated_rect = rotated_img.get_rect(center=self.pos)  # Keep the image centered on the sentry's position

        # Draw rotated image
        screen.blit(rotated_img, rotated_rect.topleft)

# Bullet class
class Bullet:
    def __init__(self, start_pos, direction):
        self.pos = list(start_pos)
        self.direction = direction

    def update(self):
        self.pos[0] += self.direction[0] * bullet_speed
        self.pos[1] += self.direction[1] * bullet_speed

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.pos[0]), int(self.pos[1])), 5)

# Crasher class (enemy)
class Crasher:
    def __init__(self):
        self.pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        self.target = sentry_pos
        self.radius = crasher_radius
        self.speed = 0.5  # Slow movement speed

    def move(self):
        direction_x = (self.target[0] - self.pos[0]) / 100
        direction_y = (self.target[1] - self.pos[1]) / 100
        self.pos[0] += direction_x * self.speed
        self.pos[1] += direction_y * self.speed

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.pos[0]), int(self.pos[1])), self.radius)

# Boss class
class Boss:
    def __init__(self):
        self.pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        self.radius = 50
        self.health = 10  # Boss takes 10 hits to kill
        self.speed = 0.2  # Very slow movement speed

    def move(self):
        direction_x = (sentry_pos[0] - self.pos[0]) / 100
        direction_y = (sentry_pos[1] - self.pos[1]) / 100
        self.pos[0] += direction_x * self.speed
        self.pos[1] += direction_y * self.speed

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.pos[0]), int(self.pos[1])), self.radius)

# Function to handle shooting
def shoot():
    global last_shot_time
    current_time = time.time()

    # Allow a max firing rate of 10 bullets per second if reload time is set to 0
    if reload_time == 0:
        if current_time - last_shot_time < 0.1:  # 0.1 seconds = 10 bullets/second
            return
    else:
        if current_time - last_shot_time < reload_time:
            return

    # Calculate direction to shoot
    mouse_pos = pygame.mouse.get_pos()
    direction = [mouse_pos[0] - sentry_pos[0], mouse_pos[1] - sentry_pos[1]]
    length = math.sqrt(direction[0]**2 + direction[1]**2)
    if length != 0:
        direction = [direction[0] / length, direction[1] / length]
    else:
        direction = [1, 0]  # Default direction

    # Add the bullet to the list
    bullets.append(Bullet(sentry_pos, direction))
    last_shot_time = current_time


# Function to check collisions
def check_collisions():
    global health, score, boss
    for bullet in bullets[:]:  # Iterate over a copy of the bullets list
        for crasher in crashers[:]:  # Iterate over a copy of the crashers list
            if (bullet.pos[0] - crasher.pos[0])**2 + (bullet.pos[1] - crasher.pos[1])**2 < (crasher.radius)**2:
                bullets.remove(bullet)
                crashers.remove(crasher)
                score += 1

    if boss is not None:  # Only check collisions with the boss if it exists
        for bullet in bullets[:]:
            if (bullet.pos[0] - boss.pos[0])**2 + (bullet.pos[1] - boss.pos[1])**2 < (boss.radius)**2:
                bullets.remove(bullet)
                boss.health -= 1  # Boss takes 1 hit per bullet
                if boss.health <= 0:
                    boss = None  # Boss is defeated
                    score += 5

        # Check for collision between boss and sentry
        if (boss.pos[0] - sentry_pos[0])**2 + (boss.pos[1] - sentry_pos[1])**2 < (boss.radius + sentry_radius)**2:
            health -= 10  # Boss deals 10 damage upon contact
            boss = None  # Boss dies if it touches the sentry

    for crasher in crashers[:]:
        if (crasher.pos[0] - sentry_pos[0])**2 + (crasher.pos[1] - sentry_pos[1])**2 < (crasher.radius + sentry_radius)**2:
            health -= 3
            crashers.remove(crasher)


# Main game loop
sentry = Sentry(sentry_pos)
running = True
while running:
    screen.fill(BLACK)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:  # Press 'K' to set reload time to 0
                reload_time = 0

    # Spawning enemies at intervals, but no more than 3 at once
    if len(crashers) < max_crashers and random.random() < 0.02:
        crashers.append(Crasher())

    # Occasionally spawn the boss
    if boss is None and random.random() < 0.001:
        boss = Boss()

    # Update
    shoot()
    check_collisions()

    # Draw everything
    sentry.draw()
    for bullet in bullets:
        bullet.update()
        bullet.draw()
    for crasher in crashers:
        crasher.move()
        crasher.draw()
    if boss:
        boss.move()
        boss.draw()

    # Display health and score
    health_text = font.render(f"Health: {health}", True, WHITE)
    screen.blit(health_text, (10, 10))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 10))

    # Check for game over
    if health <= 0:
        game_over_text = font.render(f"Game Over!", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    # Update the display
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
