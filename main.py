import sys
import io
import random
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PIL import Image, ImageDraw
import threading


def pil2pixmap(image):
    """
    src: https://stackoverflow.com/questions/28086613/pillow-pil-to-qimage-conversion-python-exe-has-stopped-working
    :param image: The pillow image object
    :return: The QPixmap object
    """
    bytes_img = io.BytesIO()
    image.save(bytes_img, format='JPEG')

    qimg = QImage()
    qimg.loadFromData(bytes_img.getvalue())

    return QPixmap.fromImage(qimg)


def get_arc_xy(angle, radius, center=(0, 0)):
    return np.cos(np.deg2rad(angle)) * radius + center[0], np.sin(np.deg2rad(angle)) * radius + center[1]


class Vector:
    def __init__(self, direction, magnitude):
        self.direction = direction  # Degrees
        self.magnitude = magnitude

    def new_position(self, initial_position):
        x, y = initial_position
        x += np.cos(np.deg2rad(self.direction)) * self.magnitude
        y += np.sin(np.deg2rad(self.direction)) * self.magnitude
        return x, y


class Sensor:
    def __init__(self, angle_range, radius_range):
        self.angle = angle_range
        self.radius = radius_range

    def angle_range(self, center):
        return int(center - self.angle / 2), int(center + self.angle / 2)

    def check_sense_area(self, position, center, image):
        start, end = self.angle_range(center)
        x, y = position
        im2 = Image.new("RGB", image.size, "white")
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice(
            (x - self.radius, y - self.radius,
             x + self.radius, y + self.radius),
            start, end, fill=255)
        im = Image.composite(image, im2, mask)
        for pixel in im.getdata():
            if pixel in [(0, 0, 0)]:
                return True
        return False


class Meeple:
    def __init__(self, parent, initial_position, color="blue"):
        """
        Initializes a meeple
        :param GameBoard parent: The game board to draw on
        :param initial_position: The initial position of the meeple
        """
        self.x, self.y = initial_position

        self.size = 20
        self.color = color
        self.parent = parent
        self.vector = Vector(random.randint(0, 360), random.randint(10, 30))
        self.sensor = Sensor(90, self.size * 2)

    def draw(self):
        top_left = (self.x - self.size / 2, self.y - self.size / 2)
        bottom_right = (self.x + self.size / 2, self.y + self.size / 2)
        shape = [top_left, bottom_right]
        self.parent.drawer.ellipse(shape, fill=self.color)

    def update(self):
        self.sense()
        self.move(self.vector.new_position((self.x, self.y)))

    def move(self, new_position):
        self.x, self.y = new_position
        self.x = min(max(0, self.x), self.parent.image.width)
        self.y = min(max(0, self.y), self.parent.image.height)

    def sense(self):
        if self.sensor.check_sense_area((self.x, self.y), self.vector.direction, self.parent.background.image):
            starting_angle = int(self.vector.direction - self.sensor.angle / 2)
            while starting_angle < 0:
                starting_angle += 360
            turn_range = (360 - starting_angle + 10, starting_angle + 10)
            change_by = random.randint(min(*turn_range), max(*turn_range))
            self.vector.direction += change_by
            while self.vector.direction > 360 or self.vector.direction < 0:
                if self.vector.direction > 360:
                    self.vector.direction -= 360
                if self.vector.direction < 0:
                    self.vector.direction += 360
            return


class Background:
    def __init__(self, wh, color="white", stroke="black"):
        self.image = Image.new("RGB", wh, color)
        self.drawer = ImageDraw.Draw(self.image)
        self.drawer.rectangle([(0, 0), wh], color, stroke, 10)

    def get_pixel(self, xy):
        return self.image.getpixel(xy)

    def random_point(self):
        return random.randint(0, self.image.width), random.randint(0, self.image.height)

    def add_circle(self, position=None, radius=None):
        if not position:
            position = self.random_point()

        if not radius:
            radius = random.randint(25, 50)

        x, y = position
        self.drawer.ellipse([x - radius, y - radius, x + radius, y + radius], (0, 0, 0))


class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 1000
        self.resize(self.width, self.height)

        self.background = Background((self.width, self.height))

        self.scan_threads = []

        self.image = Image.new("RGB", (1000, 1000))
        self.drawer = ImageDraw.Draw(self.image)
        self.meeples = []
        self.label = QLabel(self)
        self.timer = QTimer()
        self.run()

    def random_point(self):
        return random.randint(0, self.width), random.randint(0, self.height)

    def add_meeple(self, position=None, color=None):
        if not color:
            color = random.choice(["green", "blue", "yellow", "red"])
        if not position:
            position = self.random_point()

        self.meeples.append(Meeple(self, position, color))

    def draw(self):
        self.image.paste(self.background.image)
        for meeple in self.meeples:
            meeple.draw()
        self.label.setPixmap(pil2pixmap(self.image))

    def update(self):
        for meeple in self.meeples:
            meeple.update()
        self.draw()

    def run(self):
        self.draw()
        self.timer.start(100)
        self.timer.timeout.connect(self.update)

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.pause()
        if event.key() == Qt.Key_Escape:
            self.close()
        event.accept()


class MeepleSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.game_board = GameBoard()
        self.resize(self.game_board.width + 500, self.game_board.height + 100)

        main_layout = QHBoxLayout()

        options = QWidget()
        options_layout = QVBoxLayout()

        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(self.game_board.pause)
        options_layout.addWidget(pause_button)

        additions = QWidget()
        addition_layout = QHBoxLayout()

        circle_button = QPushButton("Circle")
        circle_button.clicked.connect(self.game_board.background.add_circle)
        addition_layout.addWidget(circle_button)

        meeple_button = QPushButton("Meeple")
        meeple_button.clicked.connect(self.game_board.add_meeple)
        addition_layout.addWidget(meeple_button)
        additions.setLayout(addition_layout)

        options_layout.addWidget(additions)
        options.setLayout(options_layout)

        main_layout.addWidget(self.game_board, 4)
        main_layout.addWidget(options, 1)

        self.setLayout(main_layout)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MeepleSimulation()
    sys.exit(app.exec_())
