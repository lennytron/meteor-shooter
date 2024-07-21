import pygame
import pygame.freetype
import math
import random


# Give access to keyboard and interactive stuff
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE
)

# Determine screen width and height
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

# Background colour
BACKGROUND_COLOUR = [0, 0, 0]

# Player size, speed and image/ colour
PLAYER_SIZE = [int(SCREEN_HEIGHT/15),int(SCREEN_HEIGHT/15)]
PLAYER_SPEED = 5

# Bullet size, speed and image
BULLET_SIZE = [int(SCREEN_HEIGHT/20),int(SCREEN_HEIGHT/30)]
BULLET_SPEED = PLAYER_SPEED*1.5

# Enemy size, image and spawn time
ENEMY_SIZE = [int(SCREEN_HEIGHT/10),int(SCREEN_HEIGHT/10)]
ENEMY_COLOUR = [180, 0, 0]
ENEMY_SPAWN_TIME = 60


# Define Player class
class Player(pygame.sprite.Sprite):
    # Initial stuff
    def __init__(self):
    # Inherit methods from pygame.sprite.Sprite object
        super(Player, self).__init__()
        self.surf = PLAYER_IMAGE
        # Initiate on left side of screen     
        self.rect = self.surf.get_rect()                           

    # Move player based on key presses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, - PLAYER_SPEED)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, PLAYER_SPEED)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYER_SPEED, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYER_SPEED, 0)
     
# Define Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, shooter):
        super(Bullet, self).__init__()
        self.surf = BULLET_IMAGE1
        # Initiate at player's right side
        self.rect = self.surf.get_rect(
                                center=(shooter.rect.right,
                                (shooter.rect.top+shooter.rect.bottom)/2)
                                      )
        self.counter = 0
        self.hit = False
        self.dead = False
    # Move right until offscreen
    def update(self):
        if self.dead:
            self.kill()
        if not self.hit:
            self.rect.move_ip(BULLET_SPEED,0)
            if self.counter <2:
                self.surf = BULLET_IMAGE2
            else:
                self.surf = BULLET_IMAGE1              
            if self.rect.left > SCREEN_WIDTH:
                self.kill()
            self.counter = (self.counter + 1) % 4
        else:
            self.surf = BULLETEXPLODED
            self.dead = True
# Define Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = STONE
        self.rect = self.surf.get_rect(
        center=(random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
        random.randint(0, SCREEN_HEIGHT),)
        )
        self.speed = random.randint(
                                    int(PLAYER_SPEED*0.5),
                                    int(PLAYER_SPEED*1.3)
                                    )
        self.hitpoints = 2
        self.hit = False
    def update(self):
        if (self.rect.right < 0) or (self.hitpoints == 0):
            self.kill()
        elif self.hitpoints == 2 and self.hit:
            self.surf = HURTSTONE
            self.rect.move_ip(-self.speed, 0)
            self.hitpoints -=  1
            self.hit = False
        elif self.hitpoints == 1 and self.hit:
            self.surf = DEADSTONE
            self.hitpoints = 0        
        else:
            self.rect.move_ip(-self.speed, 0)   
            
            
# Initialize pygame, create screen 
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

# Load player picture
PLAYER_IMAGE = pygame.image.load("sprites/spaceship.png").convert()
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, PLAYER_SIZE)
PLAYER_IMAGE.set_colorkey(0, RLEACCEL)

# Load bullet pictures
BULLET_IMAGE1 = pygame.image.load("sprites/bullet1.png").convert()
BULLET_IMAGE1 = pygame.transform.scale(BULLET_IMAGE1, BULLET_SIZE)
BULLET_IMAGE1.set_colorkey(0, RLEACCEL)
BULLET_IMAGE2 = pygame.image.load("sprites/bullet2.png").convert()
BULLET_IMAGE2 = pygame.transform.scale(BULLET_IMAGE2, BULLET_SIZE)
BULLET_IMAGE2.set_colorkey(0, RLEACCEL)
BULLETEXPLODED = pygame.image.load("sprites/bulletexploded.png").convert()
BULLETEXPLODED = pygame.transform.scale(BULLETEXPLODED, [BULLET_SIZE[0],BULLET_SIZE[0]])
BULLETEXPLODED.set_colorkey(0, RLEACCEL)

# Load enemy pictures
STONE = pygame.image.load("sprites/stone.png").convert()
STONE = pygame.transform.scale(STONE, ENEMY_SIZE)
STONE.set_colorkey(0, RLEACCEL)
HURTSTONE = pygame.image.load("sprites/hurtstone.png").convert()
HURTSTONE = pygame.transform.scale(HURTSTONE, ENEMY_SIZE)
HURTSTONE.set_colorkey(0, RLEACCEL)
DEADSTONE = pygame.image.load("sprites/deadstone.png").convert()
DEADSTONE = pygame.transform.scale(DEADSTONE, ENEMY_SIZE)
DEADSTONE.set_colorkey(0, RLEACCEL)


# Create player and group for all sprites
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Create bullet and enemy groups
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Create event for spawning enemies
ADD_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_ENEMY, ENEMY_SPAWN_TIME)

# Keep running game?
running = True
game_over = False

# Keep track of time
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
last_time = start_time
play_time = 0.0
text_playtime = "0.0"
 
# Add event for updating time
UPDATE_TIME = pygame.USEREVENT + 3
pygame.time.set_timer(UPDATE_TIME, 90)

# Initialise time display on screen
GAME_FONT = pygame.freetype.Font(None, size=24)
		
# Main Loop
while running:
    # Colour background
    screen.fill(BACKGROUND_COLOUR)
    
    # Record current time, if 
    current_time = pygame.time.get_ticks()
    
    # Chance for new enemy to be prevented from spawning, goes to 0
    # as current_time becomes large
    chance = (1/math.log(3000+current_time, 3000))

    # Cycle through events in event queue
    for event in pygame.event.get():
        # Was a key pressed?
        if event.type == KEYDOWN:
            # If escape key pressed, stop the game
            if event.key == K_ESCAPE:
                running = False
            # If space key pressed, spawn bullet    
            if event.key == K_SPACE:
                new_bullet = Bullet(player)
                bullets.add(new_bullet)
                all_sprites.add(new_bullet)
        # If ADD_ENEMY has occured, there is 1-chance probability of new enemy        
        elif event.type == ADD_ENEMY and random.random() > chance:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
        # If UPDATE_TIME has occured, update time to appear on screen    
        elif event.type == UPDATE_TIME:
            text_playtime = str(round(current_time/1000,2))
        # Was the window close button pressed?
        elif event.type == QUIT:
            running = False
            
    # Write playtime to screen    
    GAME_FONT.render_to(
    screen, (50, 50), 
    text_playtime, 
    (255, 255, 255)
    )
            
    # Get currently pressed keys
    pressed_keys = pygame.key.get_pressed()

    # Update player location, making sure player remains on screen
    player.update(pressed_keys)
    player.rect.clamp_ip(screen.get_rect())
    
    # Update bullet locations
    for bullet in bullets:
        bullet.update()
        
    for enemy in enemies:
        enemy.update()

    # Draw sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)	
     
    # Check if any bullets collide with any enemies, if so, remove those    
    for bullet in bullets:
        if not bullet.hit:
            hits = pygame.sprite.spritecollide(bullet, enemies, False)
            if hits != []:
                for enemy in hits:
                    enemy.hit = True
                bullet.hit = True
    
    # If player collides with enemy, end
    if pygame.sprite.spritecollideany(player, enemies):
        running = False
    
    # Draw everything to screen
    pygame.display.flip()
    clock.tick(50)
    
running = True

# Game over screen
while running:
    screen.fill(BACKGROUND_COLOUR)
    
    text_end = "You lasted for " + text_playtime + " seconds."
    
    GAME_FONT.render_to(
    screen, (int(SCREEN_WIDTH/2.8)-60, int(SCREEN_HEIGHT/2)), 
    text_end, 
    (255, 255, 255)
    )
    
    GAME_FONT.render_to(
    screen, (int(SCREEN_WIDTH/2.8)+20, int(SCREEN_HEIGHT/2)-50), 
    "GAME OVER!", 
    (255, 255, 255)
    )
    
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
            
			
    pygame.display.flip()






