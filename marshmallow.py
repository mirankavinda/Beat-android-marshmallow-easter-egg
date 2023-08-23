import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 400
WIN_HEIGHT  = 700

GEN = 0

ANDROID_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "android1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "android2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "android3.png")))]
MALLOW_STICK = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "marshmallow_stick.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("Verdana", 30)

class Android:
    IMGS = ANDROID_IMGS
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img_count = 0  # Which image we are showing
        self.img = self.IMGS[0]  # first image by default
        self.tick_count = 0  # tick count for jumping
        self.vel = 0  # Initialize velocity
        self.height = self.y

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0  # Reset tick count for jumping
        self.height = self.y
    
    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2  # How many pixels we are moving up or down

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d  # Update the y position
    
    def draw(self, win):
        self.img_count += 1

        # Select the appropriate android image based on animation time
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        # Draw the selected android image
        win.blit(self.img, (self.x, self.y))
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200 # Space between pipes
    VEL = 5 # How fast the pipes are moving


    def __init__(self, x):
        self.x = x
        self.height = 0

        # Where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        # Images
        self.PIPE_TOP = pygame.transform.flip(MALLOW_STICK, False, True)
        self.PIPE_BOTTOM = MALLOW_STICK
    
        self.passed = False # If the android has passed the pipe
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # Draw top pipe
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # Draw bottom pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, android,) :
        # Get the masks
        android_mask = android.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        # Offset( how far away the masks are from each other)
        top_offset = (self.x - android.x, self.top - round(android.y))
        bottom_offset = (self.x - android.x, self.bottom - round(android.y))
        
        # Point of collision
        b_point = android_mask.overlap(bottom_mask, bottom_offset)
        t_point = android_mask.overlap(top_mask, top_offset)

        # If there is a collision
        if t_point or b_point:
            return True
        
        return False 

class Base:
    VEL = 5 # Same as the pipe
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y 
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # Move the base
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # If the base is off the screen
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Draw the base
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))    

def draw_window(win, android, pipes, base, score, gen):
    win.blit(BG_IMG, (0,0))

    for pair in pipes:
        pair.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))

    base.draw(win)

    for android in android:
        android.draw(win)

    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    androids = []

    for _, g in genomes:
        # Neural network
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        androids.append(Android(230, 350))
        # Fitness
        g.fitness = 0
        ge.append(g)

    base = Base(630)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0 # Which pipe we are looking at
        if len(androids) > 0:
            # If there is more than one pipe and the android is past the first pipe
            if len(pipes) > 1 and androids[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): 
                pipe_ind = 1
        else:
            run = False
            break

        for x, android in enumerate(androids):
            android.move()
            ge[x].fitness += 0.1

            # Output of the neural network
            output = nets[x].activate((android.y, abs(android.y - pipes[pipe_ind].height), abs(android.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                android.jump()
        
        #android.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, android in enumerate(androids):
                if pipe.collide(android):
                    ge[x].fitness -= 1 # If the android hits a pipe it loses fitness
                    androids.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < android.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(500))

        for r in rem:
            pipes.remove(r)

        for x, android in enumerate(androids):
            if android.y + android.img.get_height() >= 630 or android.y < 0:
                androids.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, androids, pipes, base, score, GEN)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                    neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    p = neat.Population(config)

    # Output stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat_config.txt")
    run(config_path)