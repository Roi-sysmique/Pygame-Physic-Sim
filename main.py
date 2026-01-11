import random
import sys
import pygame
from pygame import Vector2

pygame.init()

WIDTH, HEIGHT = 800, 700
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
        self.border_width = 2
        self.total_radius = self.radius + self.border_width
        self.diameter = self.total_radius * 2
        self.image = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.position)
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.gravity = Vector2(0, 0.3)
        self.color = color
        self.restitution = 0.8
        self.friction = 0.2

    def wall_collisions(self, wall_start_pos:Vector2, wall_end_pos:Vector2):
            wall = wall_end_pos - wall_start_pos
            length = wall.length()
            wall_dir = wall.normalize()
            ball_dist = self.position - wall_start_pos
            proj = ball_dist.dot(wall.normalize())
            if 0 <= proj <= length +self.total_radius:
                normal = wall_dir.rotate(90)
                dist = ball_dist.dot(normal)
                if abs(ball_dist.dot(normal)) <= self.radius:
                    penetration = self.radius - abs(dist)
                    self.position += normal * penetration * (1 if dist > 0 else -1)
                    self.velocity.reflect_ip(normal)

    def ball_collisions(self, b: object):
        dist_vec = self.position - b.position
        dist  = dist_vec.length()
        radius_sum = b.radius + self.total_radius
        if dist <= radius_sum:
            penetration = radius_sum - dist
            normal = dist_vec.normalize()
            self.position += normal * (penetration / 2)
            b.position -= normal * (penetration / 2)
            rel_vel = self.velocity - b.velocity
            vn = rel_vel.dot(normal)

            if vn > 0:
                return

            impulse = -vn * normal * self.restitution
            self.velocity += impulse
            b.velocity -= impulse

    def circle_collisions(self, circle: object):
        rel_pos = self.position - circle.pos
        dist = rel_pos.length()
        border_dist = circle.radius - self.total_radius
        normal = rel_pos.normalize()
        radius_sum = circle.radius + self.total_radius
        if dist == radius_sum:
            penetration = radius_sum - dist
            self.position += normal * (penetration / 2)
            vn = self.velocity.dot(normal)

            if vn > 0:
                return

            impulse = -vn * normal * self.restitution
            self.velocity += impulse
        if dist > border_dist and dist < radius_sum:
            self.velocity.reflect_ip(normal)
            penetration = dist - border_dist
            self.position -= normal * penetration

    def update(self):
        self.velocity += self.gravity
        self.velocity += self.acceleration
        self.position += self.velocity * self.friction
        self.rect.center = self.position
        pygame.draw.circle(self.image, (10, 10, 10), (self.radius + self.border_width, self.radius + self.border_width), self.radius + self.border_width, width=self.border_width)
        pygame.draw.circle(self.image, self.color, (self.radius + self.border_width, self.radius + self.border_width), self.radius)

class Obstacle:
    def __init__(self, vertices:list, color, walls):
        self.vertices = vertices
        self.color = color
        self.vertices.append(vertices[0])
        for point_index, points in enumerate(vertices):
            if point_index % 2 != 0:
                self.vertices.insert(point_index, points)
        count = 0
        line = []
        for ver in self.vertices:
            line.append(ver)
            count += 1
            if count == 2:
                count = 0
                walls.append(line)
                line = []
    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.vertices)
        pygame.draw.lines(surface, self.color, False, self.vertices, 2)

class Circle:
    def __init__(self, center:Vector2,radius:int, color):
        self.pos = center
        self.radius = radius
        self.color = color
        self.width = 2
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius, 2)

class Spring:
    def __init__(self, node1: object, node2: object, length: int, force: int):
        self.node1 = node1
        self.node2 = node2
        self.length = length
        self.force = force
    def attach(self):
        dist_vec = (self.node1.position + 5*self.node1.velocity) - (self.node2.position + 5*self.node2.velocity)
        dist = dist_vec.length()
        self.node1.velocity += (-dist_vec * (1 - self.length/dist)/2 * self.force)
        self.node2.velocity += (dist_vec * (1 - self.length / dist) / 2 * self.force)
        pygame.draw.line(SCREEN, (255, 255, 255), self.node1.position, self.node2.position, 1)


def main():
    fps = 60
    balls = pygame.sprite.Group()
    colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255))
    walls = []
    obstacles = []
    circles = []
    springs = []

    circles.append(Circle(Vector2(100, HEIGHT / 2), 100, colors[0]))
    # Sol incliné
    obstacles.append(
        Obstacle(
            [
                Vector2(50, HEIGHT - 50),
                Vector2(WIDTH - 50, HEIGHT - 80),
                Vector2(WIDTH - 100, HEIGHT - 30),
                Vector2(80, HEIGHT - 20)
            ],
            colors[0],
            walls
        )
    )

    # Rectangle gauche
    obstacles.append(
        Obstacle(
            [
                Vector2(80, HEIGHT / 2 + 100),
                Vector2(250, HEIGHT / 2 + 100),
                Vector2(250, HEIGHT / 2 + 200),
                Vector2(80, HEIGHT / 2 + 200)
            ],
            colors[2],
            walls
        )
    )

    # Obstacle incliné droit
    obstacles.append(
        Obstacle(
            [
                Vector2(WIDTH - 300, HEIGHT / 2 + 50),
                Vector2(WIDTH - 150, HEIGHT / 2 + 100),
                Vector2(WIDTH - 200, HEIGHT / 2 + 200),
                Vector2(WIDTH - 350, HEIGHT / 2 + 150)
            ],
            colors[3],
            walls
        )
    )

    for i in range(2):
        for j in range(2):
            balls.add(
                Ball(
                    Vector2(200 + i * 100, 50 + j * 100),
                    Vector2(random.randint(-3, 3), random.randint(-1, 1)),
                    Vector2(0, 0),
                    random.randint(10, 30),
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
                pygame.draw.line(SCREEN, (255, 255, 255), wall[0], wall[1], 2)
                ball.wall_collisions(Vector2(wall[0]), Vector2(wall[1]))
            for b in balls:
                # A ball can't collide with itself
                if ball == b:
                    pass
                else:
                    ball.ball_collisions(b)
                for circle in circles:
                    circle.draw(SCREEN)
                    ball.circle_collisions(circle)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
        balls.update()
        for spring in springs:
            spring.attach()
        pygame.display.update()
        clock.tick(fps)

if __name__ == '__main__':
    main()
