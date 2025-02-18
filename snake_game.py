import pygame
import random

# ----- Game Configuration -----
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY   = (100, 100, 100)

# ----- Snake Class -----
class Snake:
    def __init__(self, color):
        # Start with one segment placed randomly on the grid.
        self.segments = [(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))]
        # Pick a random initial direction (dx,dy)
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.color = color
        self.alive = True
        self.score = 0

    def get_head(self):
        return self.segments[0]

    def update_direction(self, food_pos):
        head_x, head_y = self.get_head()
        food_x, food_y = food_pos
        # Avoid reversing the current direction.
        reverse = (-self.direction[0], -self.direction[1])
        possible = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if reverse in possible:
            possible.remove(reverse)
        # Heuristic: choose the move that minimizes Manhattan distance to the food.
        best = self.direction
        best_dist = abs(head_x - food_x) + abs(head_y - food_y)
        for d in possible:
            new_head = (head_x + d[0], head_y + d[1])
            dist = abs(new_head[0] - food_x) + abs(new_head[1] - food_y)
            if dist < best_dist:
                best = d
                best_dist = dist
        self.direction = best

    def move(self, grow=False):
        if not self.alive:
            return
        head_x, head_y = self.get_head()
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.segments.insert(0, new_head)
        if not grow:
            self.segments.pop()

    def check_collision(self, snakes):
        head = self.get_head()
        x, y = head
        # Wall collisions:
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            self.alive = False
            return
        # Self collision:
        if head in self.segments[1:]:
            self.alive = False
            return
        # Collision with any other snake:
        for snake in snakes:
            if snake is self:
                continue
            if head in snake.segments:
                self.alive = False
                return

# ----- Food Class -----
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn([])

    def spawn(self, snakes):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            pos = (x, y)
            conflict = any(pos in snake.segments for snake in snakes)
            if not conflict:
                self.position = pos
                break

# ----- Button Class (for Restart) -----
class Button:
    def __init__(self, rect, text, color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 30)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ----- Game Reset Function -----
def reset_game():
    # Create several snakes (here we use 3 for a simple multi-agent competition)
    snakes = [
        Snake(GREEN),
        Snake(BLUE),
        Snake(YELLOW)
    ]
    food = Food()
    food.spawn(snakes)
    return snakes, food

# ----- Main Game Loop -----
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Autonomous Snake Competition")
    clock = pygame.time.Clock()

    # Place a Restart button at the bottom center.
    restart_button = Button((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 40, 100, 30), "Restart", RED, WHITE)
    snakes, food = reset_game()

    running = True
    while running:
        clock.tick(10)  # 10 frames per second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(event.pos):
                    snakes, food = reset_game()

        # Update each snake
        for snake in snakes:
            if snake.alive:
                snake.update_direction(food.position)
                # Predict next head position to check if food will be eaten.
                head_x, head_y = snake.get_head()
                dx, dy = snake.direction
                next_head = (head_x + dx, head_y + dy)
                if next_head == food.position:
                    snake.move(grow=True)
                    snake.score += 1
                    food.spawn(snakes)
                else:
                    snake.move()
                snake.check_collision(snakes)

        # Draw background and grid
        screen.fill(BLACK)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

        # Draw food
        food_rect = pygame.Rect(food.position[0] * GRID_SIZE, food.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, food_rect)

        # Draw snakes
        for snake in snakes:
            color = snake.color if snake.alive else GRAY
            for segment in snake.segments:
                seg_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, color, seg_rect)

        # Draw Restart Button
        restart_button.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
