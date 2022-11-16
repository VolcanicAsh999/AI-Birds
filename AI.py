#imports
import pygame
import random
import threading
import time

GENIUSMODE = False #if true, all the birds have perfect AI

#random seed
random.seed(17)

#setup pygame
pygame.init()
clock = pygame.time.Clock()

#setup variables
WIDTH = 1000
HEIGHT = 700
FPS = 60

score = 0

GOOD_MOVES = {}

pipes_pos = []

count = 0

is_first_generation = True

#setup colors
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GREEN = pygame.Color('green')
RED = pygame.Color('red')

#setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

#classes
class Pipe(pygame.sprite.Sprite):
    def __init__(self, height=None):
        super().__init__()
        self.y = 0
        self.x = WIDTH
        self.rect = pygame.Rect(self.x, self.y, 70, HEIGHT)
        if height == None: self.height = random.randrange(50, HEIGHT - 180, 10)
        else: self.height = height
        self.top = pygame.Rect(self.x, self.y, 70, self.height)
        self.bottom = pygame.Rect(self.x, self.y + self.height + 130, 70, HEIGHT - self.height - 130)
        self.speed = 5
        if height == None: pipes_pos.append(self.height)

    def update(self):
        global score
        pygame.draw.rect(screen, GREEN, self.top)
        pygame.draw.rect(screen, GREEN, self.bottom)
        self.x -= self.speed
        self.rect = self.rect.move(-self.speed, 0)
        self.top = self.top.move(-self.speed, 0)
        self.bottom = self.bottom.move(-self.speed, 0)
        if self.rect.x + self.rect.width < 0:
            pipes.remove(self)
            score += 1
            

class AIBird(pygame.sprite.Sprite):
    def __init__(self, which, path=[]):
        super().__init__()
        self.rect = pygame.Rect(100, HEIGHT // 2, 20, 20)
        self.speed = 10
        self.isalive = True
        self.should = True
        self.moves = []
        self.which = []
        self.path = iter(path)
        GOOD_MOVES[which] = []
        self.w = which

    def update(self):
        pygame.draw.rect(screen, RED, self.rect)
        for pipe in pipes.sprites():
            if self.rect.colliderect(pipe.top) or self.rect.colliderect(pipe.bottom):
                self.isalive = False
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.isalive = False
        if not self.isalive:
            birds.remove(self)
        if not GENIUSMODE:
            if list(self.path) == []: self.AImove(False)
            else: self.PATHmove()
        else: self.AImove(True)

    def AImove(self, smartest):
        if len(pipes.sprites()) == 0: return
        if smartest:
            pipe = pipes.sprites()[0]
            if pipe.bottom.x < self.rect.x - 70:
                pipe = pipes.sprites()[1]
            if pipe.bottom.y > self.rect.y + 80:
                self.should = True
            else:
                self.should = False
        else:
            pipe = pipes.sprites()[0]
            if pipe.bottom.y > self.rect.y + 80:
                pool = [False, False, True, True, True]
            else:
                pool = [False, False, False, True, True]
            pool += [self.should] * 2
            self.should = random.choice(pool)
        if pipe.bottom.y > self.rect.y + 300 or pipe.bottom.y < self.rect.y - 300:
            speed = self.speed * 2
        else:
            speed = self.speed
        if self.should:
            self.rect = self.rect.move(0, speed)
            self.moves.append(speed)
        else:
            self.rect = self.rect.move(0, -speed)
            self.moves.append(-speed)
        if pipe.rect.x < self.rect.x and self.isalive and self.moves != self.which:
            GOOD_MOVES[self.w].append(self.moves)
            self.moves.clear()
            self.which = self.moves

    def PATHmove(self):
        try:
            move = next(self.path)
        except:
            self.moves = list(self.path)
            self.path = iter([])
            return self.AImove(False)
        self.rect = self.rect.move(0, move)


#functions
def add_pipe(gen2=False, count=0):
    if not gen2:
        pipes.add(Pipe())
    else:
        pipes.add(Pipe(height=pipes_pos[count] if count + 1 <= len(pipes_pos) else None))

def start_pipes():
    while is_first_generation:
        if score in range(0, 3): time.sleep(2)
        elif score in range(3, 7): time.sleep(1.5)
        elif score in range(7, 12): time.sleep(1.3)
        else: time.sleep(1)
        add_pipe()
        if not running:
            break

def start_gen_2():
    global count
    while True:
        if score in range(0, 3): time.sleep(2)
        elif score in range(3, 7): time.sleep(1.5)
        elif score in range(7, 12): time.sleep(1.3)
        else: time.sleep(1)
        add_pipe(gen2=True, count=count)
        count += 1
        if not running:
            break

def reset():
    global is_first_generation, count
    pipes.empty()
    score = 0
    for i in range(10):
        birds.add(AIBird(i, path=GOOD_MOVES[i][0] if i + 1 <= len(GOOD_MOVES[i]) else []))
    if is_first_generation: threading.Thread(target=start_gen_2, daemon=True).start()
    else: count = 0
    is_first_generation = False
    random.seed(17)

#create pipes
pipes = pygame.sprite.Group()
add_pipe()

#create birds
birds = pygame.sprite.Group()
for i in range(10):
    birds.add(AIBird(i))

#main loop
running = True
threading.Thread(target=start_pipes, daemon=True).start()

while running:
    #clear the screen
    screen.fill(WHITE)

    #update sprites
    for sprite in pipes.sprites():
        sprite.update()
    for bird in birds.sprites():
        bird.update()
    
    #update screen
    pygame.display.update()
    
    #key bindings
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #quit
            running = False

    #move to next generation
    if len(birds.sprites()) == 0:
        reset()
    
    #limit fps
    clock.tick(FPS)

pygame.quit()
