import random
import sys
import pygame
from pygame import Vector2

pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Physics Sim')
clock = pygame.time.Clock()

class Ball(pygame.sprite.Sprite):
    def __init__(self, position:Vector2, velocity:Vector2, acceleration:Vector2, radius:int, color):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.radius = radius
        self.diameter = self.radius * 2
        self.image = pygame.Surface((self.diameter, self.diameter)).convert_alpha()
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=self.position)
        self.gravity = Vector2(0, 0.1)
        self.color = color

    def wall_collisions(self, wall_start_pos:Vector2, wall_end_pos:Vector2):
            wall = wall_end_pos - wall_start_pos
            length = wall.length()
            wall_dir = wall.normalize()
            ball_dist = self.position - wall_start_pos
            proj = ball_dist.dot(wall.normalize())
            if 0 <= proj <= length:
                normal = wall_dir.rotate(90)
                dist = ball_dist.dot(normal)
                if abs(ball_dist.dot(normal)) <= self.radius:
                    penetration = self.radius - abs(dist)
                    self.position += normal * penetration * (1 if dist > 0 else -1)
                    normal_part = self.velocity.project(normal)
                    self.velocity.reflect_ip(normal_part)

    def ball_collisions(self, b: object):
        dist_vec = self.position - b.position
        dist  = dist_vec.length()
        radius_sum = b.radius + self.radius
        if dist <= radius_sum:
            penetration = radius_sum - dist
            normal = dist_vec.normalize()
            self.position += normal * penetration
            self.velocity.reflect_ip(normal)

    def update(self):
        self.velocity += self.gravity
        self.velocity += self.acceleration
        self.position += self.velocity
        self.rect.center = self.position
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)



def main():
    fps = 60
    balls = pygame.sprite.Group()
    colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255))
    walls = [
        # sol
        (Vector2(50, 500), Vector2(750, 500)),
        (Vector2(0, 0), Vector2(0, HEIGHT)),
        (Vector2(WIDTH, 0), Vector2(WIDTH, HEIGHT)),
        (Vector2(0, HEIGHT), Vector2(WIDTH, HEIGHT)),
        (Vector2(0, 0), Vector2(WIDTH, 0)),
    ]
    for i in range(5):
        for j in range(3):
            balls.add(
                Ball(
                    Vector2(200 + i * 100, 100 + j * 100),
                    Vector2(random.randint(-3, 3), random.randint(-1, 1)),
                    Vector2(0, 0),
                    25,
                    random.choice(colors))
            )
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill('lightblue')
        balls.draw(SCREEN)
        for ball in balls:
            for wall in walls:
                pygame.draw.line(SCREEN, (255, 255, 255), wall[0], wall[1], 5)
                ball.wall_collisions(Vector2(wall[0]), Vector2(wall[1]))
            for b in balls:
                if ball == b:
                    pass
                else:
                    ball.ball_collisions(b)
        balls.update()
        pygame.display.update()
        clock.tick(fps)

if __name__ == '__main__':
    main()
