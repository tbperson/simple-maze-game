import pygame
import time
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Maze Game")

# Define colors
GREY = (169, 169, 169)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

placed_blocks = []

def generate_maze(width, height):
    maze = [['W' for _ in range(width)] for _ in range(height)]
    
    def carve_passages_from(cx, cy, maze):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        for direction in directions:
            nx, ny = cx + direction[0] * 2, cy + direction[1] * 2
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 'W':
                maze[cy + direction[1]][cx + direction[0]] = 'E'
                maze[ny][nx] = 'E'
                carve_passages_from(nx, ny, maze)
    
    maze[1][1] = 'E'
    carve_passages_from(1, 1, maze)
    maze[height-2][width-2] = 'E'
    
    return maze

def reset_game():
    global maze, player_pos, goal_pos, enemy_pos, player_first_move_time, last_ability_use_time, ability_active, last_block_ability_use_time, placed_blocks
    maze = generate_maze(40, 40)
    player_pos = [1, 1]
    goal_pos = [len(maze[0]) - 2, len(maze) - 2]
    enemy_pos = [1, 1]
    player_first_move_time = None
    last_ability_use_time = 0
    ability_active = False
    last_block_ability_use_time = 0
    placed_blocks = []

reset_game()

def bfs(start, goal, maze):
    queue = deque([start])
    visited = set()
    visited.add(tuple(start))
    parent = {tuple(start): None}
    
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent[tuple(current)]
            return path[::-1]
        
        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor = [current[0] + direction[0], current[1] + direction[1]]
            if (0 <= neighbor[0] < len(maze[0]) and 0 <= neighbor[1] < len(maze) and
                maze[neighbor[1]][neighbor[0]] == 'E' and tuple(neighbor) not in visited):
                queue.append(neighbor)
                visited.add(tuple(neighbor))
                parent[tuple(neighbor)] = current
    return []

# Main game loop
running = True
last_move_time = time.time()
move_delay = 1 / 20  # 5 moves per second

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()

    # Remove player blocks after 2.5 seconds
    placed_blocks = [(pos, t) for pos, t in placed_blocks if current_time - t < 2.5]
    for pos, t in placed_blocks:
        if current_time - t >= 2.5:
            maze[pos[1]][pos[0]] = 'E'

    current_time = time.time()
    if current_time - last_move_time >= move_delay:
        if keys[pygame.K_r] and current_time - last_ability_use_time >= 2.5:
            ability_active = True
            last_ability_use_time = current_time

        if keys[pygame.K_LEFT]:
            new_pos = [player_pos[0] - 1, player_pos[1]]
            if new_pos[0] >= 0 and (maze[new_pos[1]][new_pos[0]] == 'E' or ability_active):
                player_pos = new_pos
        if keys[pygame.K_RIGHT]:
            new_pos = [player_pos[0] + 1, player_pos[1]]
            if new_pos[0] < len(maze[0]) and (maze[new_pos[1]][new_pos[0]] == 'E' or ability_active):
                player_pos = new_pos
        if keys[pygame.K_UP]:
            new_pos = [player_pos[0], player_pos[1] - 1]
            if new_pos[1] >= 0 and (maze[new_pos[1]][new_pos[0]] == 'E' or ability_active):
                player_pos = new_pos
        if keys[pygame.K_DOWN]:
            new_pos = [player_pos[0], player_pos[1] + 1]
            if new_pos[1] < len(maze) and (maze[new_pos[1]][new_pos[0]] == 'E' or ability_active):
                player_pos = new_pos

        if player_first_move_time is None and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            player_first_move_time = current_time

        last_move_time = current_time

    # Handle block placing ability
    if keys[pygame.K_e] and current_time - last_block_ability_use_time >= 3:
        if keys[pygame.K_LEFT]:
            block_pos = [player_pos[0] - 1, player_pos[1]]
            if block_pos[0] >= 0 and maze[block_pos[1]][block_pos[0]] == 'E':
                maze[block_pos[1]][block_pos[0]] = 'W'
                placed_blocks.append((block_pos, current_time))
                last_block_ability_use_time = current_time
        if keys[pygame.K_RIGHT]:
            block_pos = [player_pos[0] + 1, player_pos[1]]
            if block_pos[0] < len(maze[0]) and maze[block_pos[1]][block_pos[0]] == 'E':
                maze[block_pos[1]][block_pos[0]] = 'W'
                placed_blocks.append((block_pos, current_time))
                placed_blocks.append((block_pos, current_time))
                last_block_ability_use_time = current_time
        if keys[pygame.K_UP]:
            block_pos = [player_pos[0], player_pos[1] - 1]
            if block_pos[1] >= 0 and maze[block_pos[1]][block_pos[0]] == 'E':
                maze[block_pos[1]][block_pos[0]] = 'W'
                placed_blocks.append((block_pos, current_time))
                placed_blocks.append((block_pos, current_time))
                last_block_ability_use_time = current_time
        if keys[pygame.K_DOWN]:
            block_pos = [player_pos[0], player_pos[1] + 1]
            if block_pos[1] < len(maze) and maze[block_pos[1]][block_pos[0]] == 'E':
                maze[block_pos[1]][block_pos[0]] = 'W'
                placed_blocks.append((block_pos, current_time))
                placed_blocks.append((block_pos, current_time))
                last_block_ability_use_time = current_time


    # Remove blocks after 2.5 seconds
    placed_blocks = [(pos, t) for pos, t in placed_blocks if current_time - t < 2.5]
    for pos, t in placed_blocks:
        maze[pos[1]][pos[0]] = 'W'
    for pos, t in placed_blocks:
        if current_time - t >= 2.5:
            maze[pos[1]][pos[0]] = 'E'

    # Move the enemy if 5 seconds have passed since the player's first move
    if player_first_move_time and current_time - player_first_move_time >= 5:
        path = bfs(enemy_pos, player_pos, maze)
        if len(path) > 1:
            enemy_pos = path[1]

    # Check if player reached the goal
    if player_pos == goal_pos:
        reset_game()

    # Check if enemy caught the player
    if player_pos == enemy_pos:
        reset_game()

    # Deactivate ability after 3 seconds
    if ability_active and current_time - last_ability_use_time >= 0.1:
        ability_active = False

    # Draw everything
    screen.fill(GREY)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'W':
                pygame.draw.rect(screen, BLACK, (x*20, y*20, 20, 20))
            elif cell == 'E':
                pygame.draw.rect(screen, GREY, (x*20, y*20, 20, 20))
    pygame.draw.rect(screen, GREEN, (goal_pos[0]*20, goal_pos[1]*20, 20, 20))
    pygame.draw.rect(screen, RED, (player_pos[0]*20, player_pos[1]*20, 20, 20))
    pygame.draw.rect(screen, BLUE, (enemy_pos[0]*20, enemy_pos[1]*20, 20, 20))
    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
