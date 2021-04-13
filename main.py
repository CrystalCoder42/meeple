import sys
import io
import random
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PIL import Image, ImageDraw


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
        return range(int(center - self.angle / 2), int(center + self.angle / 2))


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
        # shape = [
        #     (self.x - self.sensor.radius, self.y - self.sensor.radius),
        #     (self.x + self.sensor.radius, self.y + self.sensor.radius)
        # ]
        # self.parent.drawer.arc(
        #     shape,
        #     int(self.vector.direction - self.sensor.angle / 2),
        #     int(self.vector.direction + self.sensor.angle / 2),
        #     "red"
        # )

    def update(self):
        self.sense()
        self.move(self.vector.new_position((self.x, self.y)))

    def move(self, new_position):
        self.x, self.y = new_position
        self.x = min(max(0, self.x), self.parent.image.width)
        self.y = min(max(0, self.y), self.parent.image.height)

    def sense(self):
        for radius in range(1, self.sensor.radius + 1):
            for angle in self.sensor.angle_range(self.vector.direction):
                try:
                    point_color = self.parent.background.get_pixel(get_arc_xy(angle, radius, (self.x, self.y)))
                except:
                    point_color = (0, 0, 0)
                if point_color == (0, 0, 0):
                    starting_angle = int(self.vector.direction - self.sensor.angle / 2)
                    while starting_angle < 0:
                        starting_angle += 360
                    min_turn = min(int(180 * ((radius + 2) / self.sensor.radius)), 180)
                    turn_range = (360 - starting_angle + min_turn, starting_angle + min_turn)
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
        self.drawer.ellipse(
            [(100, 100), (300, 300)],
            "black"
        )
        for _ in range(random.randint(10, 30)):
            x, y = self.random_point()
            size = random.randint(50, 100)
            self.drawer.ellipse(
                [x - size/2, y-size/2, x + size/2, y+size/2],
                (0, 0, 0)
            )

    def get_pixel(self, xy):
        return self.image.getpixel(xy)

    def random_point(self):
        return random.randint(0, self.image.width), random.randint(0, self.image.height)


class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 1000
        self.resize(self.width, self.height)

        self.background = Background((self.width, self.height))

        self.image = Image.new("RGB", (1000, 1000))
        self.drawer = ImageDraw.Draw(self.image)
        self.meeples = [
            Meeple(self, self.random_point()),
            # Meeple(self, self.random_point(), "yellow"),
            # Meeple(self, self.random_point(), "red"),
            Meeple(self, self.random_point(), "green"),
        ]
        self.label = QLabel(self)
        self.timer = QTimer()
        self.run()

    def random_point(self):
        return random.randint(0, self.width), random.randint(0, self.height)

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
        self.show()
        self.timer.start(100)
        self.timer.timeout.connect(self.update)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start()
        if event.key() == Qt.Key_Escape:
            self.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GameBoard()
    sys.exit(app.exec_())
