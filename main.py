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


def get_arc_positions(degrees, radius, center, current_pos=(0, 0)):
    return [
        (np.cos(np.deg2rad(angle)) * radius + current_pos[0], np.sin(np.deg2rad(angle)) * radius + current_pos[1])
        for angle in range(int(center - degrees / 2), int(center + degrees / 2))
    ]


def get_pos_in_arc(degree, radius, current_pos=(0, 0)):
    return np.cos(np.deg2rad(degree)) * radius + current_pos[0], np.sin(np.deg2rad(degree)) * radius + current_pos[1]


def get_radius_positions(degree, max_radius, current_pos=(0, 0)):
    return [
        (np.cos(np.deg2rad(degree)) * radius + current_pos[0], np.sin(np.deg2rad(degree)) * radius + current_pos[1])
        for radius in range(max_radius)
    ]


class Vector:
    def __init__(self, direction, magnitude):
        self.direction = direction
        self.magnitude = magnitude

    def get_new_position(self, current_position):
        x, y = current_position
        x += np.cos(np.deg2rad(self.direction)) * self.magnitude
        y += np.sin(np.deg2rad(self.direction)) * self.magnitude
        return x, y


class Meeple:
    def __init__(self, parent, initial_position, color="blue"):
        """
        Initializes a meeple
        :param GameBoard parent: The parent game board
        :param tuple initial_position: The initial position of the meeple
        """
        self.x, self.y = initial_position

        self.size = 20
        self.angle = 100
        self.sensor_radius = 30
        self.color = color
        self.parent = parent
        self.vector = Vector(-30, 20)

    def draw(self):
        shape = [(self.x - self.size / 2, self.y - self.size / 2), (self.x + self.size / 2, self.y + self.size / 2)]
        self.parent.drawer.ellipse(shape, fill=self.color)
        # shape = [
        #     (self.x - self.sensor_radius, self.y - self.sensor_radius),
        #     (self.x + self.sensor_radius, self.y + self.sensor_radius)
        # ]
        # self.parent.drawer.arc(
        #     shape,
        #     int(self.vector.direction - self.angle / 2),
        #     int(self.vector.direction + self.angle / 2),
        #     "red"
        # )

    def update(self):
        try:
            self.sense()
        except:
            print(sys.exc_info())
        self.move(self.vector.get_new_position((self.x, self.y)))

    def move(self, new_position):
        self.x, self.y = new_position
        self.x = min(max(0, self.x), self.parent.image.width)
        self.y = min(max(0, self.y), self.parent.image.height)

    def position(self):
        return self.x, self.y

    def sensor_arc_range(self):
        return range(int(self.vector.direction - self.angle / 2),
                     int(self.vector.direction + self.angle / 2))

    def sense(self):
        """
        Draws the pie shape of the meeples sensor
        """
        for radius in range(1, self.sensor_radius + 1):
            for angle in self.sensor_arc_range():
                try:
                    point_color = self.parent.background.get_pixel(
                        get_pos_in_arc(angle, self.sensor_radius, self.position())
                    )
                except:
                    point_color = (0, 0, 0)
                if point_color in self.parent.background.obstacle_colors.values():
                    starting_angle = int(self.vector.direction - self.angle / 2)
                    while starting_angle < 0:
                        starting_angle += 360
                    min_turn = min(int(180 * ((radius + 2)/self.sensor_radius)), 180)
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
        self.image = Image.new("RGB", wh)
        self.drawer = ImageDraw.Draw(self.image)
        self.drawer.rectangle([(0, 0), wh], color, stroke, width=10)
        self.drawer.ellipse(
            [(100, 100), (300, 300)],
            "black"
        )
        self.obstacle_colors = {
            "border": (0, 0, 0)
        }

    def get_pixel(self, position):
        return self.image.getpixel(position)


class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 1000
        self.resize(self.width, self.height)

        self.background = Background((1000, 1000))

        self.image = Image.new("RGB", (1000, 1000))
        self.drawer = ImageDraw.Draw(self.image)
        self.meeples = [
            Meeple(self, self.random_point(), "blue"),
            Meeple(self, self.random_point(), "red"),
            Meeple(self, self.random_point(), "green"),
        ]
        self.label = QLabel(self)
        self.timer = QTimer()
        self.run()

    def random_point(self):
        return random.randint(20, self.width - 20), random.randint(20, self.height - 20)

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
