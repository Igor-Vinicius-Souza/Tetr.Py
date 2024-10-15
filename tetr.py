import pygame
import random

# Initialize pygame
pygame.init()

# Set up display
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetr.py')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

SHAPES = [
    # S-shape
    [[1, 1, 0],
     [0, 1, 1]],

    # Z-shape
    [[0, 1, 1],
     [1, 1, 0]],

    # L-shape
    [[1, 0, 0],
     [1, 1, 1]],

    # J-shape
    [[0, 0, 1],
     [1, 1, 1]],

    # I-shape
    [[1, 1, 1, 1]],

    # O-shape
    [[1, 1],
     [1, 1]],

    # T-shape
    [[0, 1, 0],
     [1, 1, 1]]
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = GRID_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    
    return grid

def draw_grid(screen, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    for y in range(GRID_HEIGHT):
        pygame.draw.line(screen, WHITE, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))
    for x in range(GRID_WIDTH):
        pygame.draw.line(screen, WHITE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))

def valid_space(piece, grid):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                if x + piece.x < 0 or x + piece.x >= GRID_WIDTH or y + piece.y >= GRID_HEIGHT:
                    return False
                if grid[y + piece.y][x + piece.x] != BLACK:
                    return False
    return True

def clear_rows(grid, locked):
    rows_cleared = 0
    rows_to_clear = []
    for y in range(GRID_HEIGHT - 1, -1, -1):
        if BLACK not in grid[y]:
            rows_to_clear.append(y)

    if rows_to_clear:
        for y in rows_to_clear:
            del grid[y]
            grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        # Move the locked positions down
        for y in rows_to_clear:
            for x in range(GRID_WIDTH):
                if (x, y) in locked:
                    del locked[(x, y)]
        
        # Shift the positions above the cleared rows down
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            if y < min(rows_to_clear):
                new_key = (x, y + len(rows_to_clear))
                locked[new_key] = locked.pop(key)

    return len(rows_to_clear)

def draw_window(screen, grid):
    screen.fill(BLACK)
    draw_grid(screen, grid)
    pygame.display.update()

def get_random_piece():
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    return Piece(shape, color)

def main():
    locked_positions = {}
    grid = create_grid()

    change_piece = False
    current_piece = get_random_piece()
    next_piece = get_random_piece()

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27

    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()

        shape_pos = [(current_piece.x + x, current_piece.y + y) for y, row in enumerate(current_piece.shape) for x, cell in enumerate(row) if cell]
        
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = get_random_piece()
            change_piece = False
            if not valid_space(current_piece, grid):
                running = False

        clear_rows(grid, locked_positions)
        draw_window(screen, grid)

    pygame.quit()

if __name__ == "__main__":
    main()
