import sys
import io
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PIL import Image, ImageDraw
import pygame

shapes = {
    "rect": pygame.draw.rect,
    "ellipse": pygame.draw.ellipse,
    "circle": pygame.draw.circle,
    "line": pygame.draw.line,
    "arc": pygame.draw.arc,
    "polygon": pygame.draw.polygon,
}


class GameBoardObject:
    def __init__(self, parent, initial_position, initial_dir=(10, 10), wh=(20, 20), color=(0, 0, 0), shape="rect"):
        """
        Initializes an object on the game board
        :param GameBoard parent: The game board to draw on
        :param initial_position: The initial position of the object
        :param wh: The width and height of the object, either a tuple of the width and height or a single size
        :param color: The color of the object
        :param shape: The shape of the object
        """
        self.pos = pygame.math.Vector2(initial_position)
        self.width, self.height = wh if type(wh) == tuple else (wh, wh)
        self.dir = pygame.math.Vector2(initial_dir)
        self.parent = parent
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        self.color = color
        self.shape = shape
        self.out_of_bounds = False

    def reflect(self, rand=False):
        start = 180 - 40
        end = 180 + 40
        rotation_angle = random.randint(start, end) if rand else 180
        self.dir.rotate_ip(rotation_angle)

    def go_somewhere(self):
        x, y = (0, 0)
        if self.rect.left <= 0:
            x = self.parent.width
        if self.rect.right >= self.parent.width:
            x = 0
        if self.rect.top <= 0:
            y = self.parent.height
        if self.rect.bottom >= self.parent.height:
            y = 0
        try:
            vector = pygame.Vector2(x, y).normalize()
        except:
            vector = pygame.Vector2(x, y)
        self.dir.x = round(self.dir.x * vector.x)
        self.dir.y = round(self.dir.y * vector.y)

    def draw(self):
        self.update()
        shapes.get(self.shape, pygame.draw.rect)(self.parent.surface, self.color, self.rect)

    def update(self):
        self.pos += self.dir
        self.rect.center = round(self.pos.x), round(self.pos.y)


class Obstacle(GameBoardObject):
    def __init__(self, parent, initial_position, wh=(20, 20), color=(0, 0, 0)):
        """
        Initializes an obstacle
        :param GameBoard parent: The game board to draw on
        :param initial_position: The initial position of the
        :param wh: The width and height of the obstacle
        :param color: The color of the obstacle
        """
        super().__init__(parent, initial_position, initial_dir=(0, 0), wh=wh, color=color, shape="rect")


class Meeple(GameBoardObject):
    def __init__(self, parent, initial_position, initial_dir=(10, 10), color=(0, 0, 255)):
        """
        Initializes a meeple
        :param GameBoard parent: The game board to draw on
        :param initial_position: The initial position of the meeple
        """
        super().__init__(parent, initial_position, initial_dir=initial_dir, wh=20, color=color, shape="ellipse")

    def update(self):
        super(Meeple, self).update()
        if self.rect.left < 0 or \
                self.rect.right > self.parent.width or \
                self.rect.top < 0 or \
                self.rect.top > self.parent.height:
            self.go_somewhere()

        for obstacle in self.parent.obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.reflect()


class GameBoard:
    def __init__(self):
        self.width = 700
        self.height = 700
        self.bg_color = (255, 255, 255)

        pygame.init()

        self.surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("My First Game")

        self.clock = pygame.time.Clock()
        self.meeples = []
        for _ in range(200):
            self.add_meeple(position=(350, 250))

        self.obstacles = []
        self.add_obstacle(position=(350, 350))
        self.carry_on = True
        self.run()

    def random_point(self, x=None, y=None):
        return random.randint(0 if x is None else x, self.width if x is None else x), \
               random.randint(0 if y is None else y, self.height if y is None else y)

    def add_meeple(self, position=None, color=None):
        if not color:
            color = (random.randint(0, 240), random.randint(0, 240), random.randint(0, 240))
        if not position:
            position = self.random_point()

        self.meeples.append(Meeple(self, initial_position=position, initial_dir=(-5, -5), color=color))

    def add_obstacle(self, position=None, wh=None, color=None):
        if not color:
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
        if not wh:
            wh = (random.randint(10, 100), random.randint(10, 100))
        if not position:
            position = self.random_point()

        self.obstacles.append(Obstacle(self, initial_position=position, wh=wh, color=color))

    def draw(self):
        for obstacle in self.obstacles:
            obstacle.draw()
        for meeple in self.meeples:
            meeple.draw()

    def update(self):
        self.surface.fill(self.bg_color)
        self.draw()
        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        while self.carry_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.carry_on = False
            self.update()

    # def pause(self):
    #     if self.timer.isActive():
    #         self.timer.stop()
    #     else:
    #         self.timer.start()
    #
    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Space:
    #         self.pause()
    #     if event.key() == Qt.Key_Escape:
    #         self.close()
    #     event.accept()


if __name__ == "__main__":
    GameBoard()
