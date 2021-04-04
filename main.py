import sys
import io
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
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


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Meeple:
    def __init__(self, image, initial_position):
        """
        Initializes a meeple
        :param Image image: The image to draw on
        :param initial_position: The initial position of the meeple
        """
        self.x, self.y = initial_position

        self.size = 20
        self.color = "blue"
        self.image = image
        self.drawer = ImageDraw.Draw(image)
        self.vector = Vector(10, 10)

    def draw(self):
        top_left = (self.x - self.size/2, self.y - self.size/2)
        bottom_right = (self.x + self.size/2, self.y + self.size/2)
        shape = [top_left, bottom_right]
        self.drawer.rectangle(shape, fill=self.color)

    def update(self):
        self.move((self.x + self.vector.x, self.y + self.vector.y))
        if self.x > self.image.width:
            self.x = 0
        if self.x < 0:
            self.x = self.image.width
        if self.y > self.image.height:
            self.y = 0
        if self.y < 0:
            self.y = self.image.height

        self.vector.x += random.randint(-10, 10)
        self.vector.y += random.randint(-10, 10)

    def move(self, new_position):
        self.x, self.y = new_position


class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 1000
        self.resize(self.width, self.height)

        self.background = "black"

        self.img = Image.new("RGB", (1000, 1000), self.background)
        self.drawer = ImageDraw.Draw(self.img)
        self.meeple = Meeple(self.img, (self.img.width / 2, self.img.height / 2))
        self.label = QLabel(self)
        self.timer = QTimer()
        self.run()

    def draw(self):
        self.drawer.rectangle([(0, 0), (self.width, self.height)], self.background)
        self.meeple.draw()
        self.label.setPixmap(pil2pixmap(self.img))

    def update(self):
        self.meeple.update()
        self.draw()

    def run(self):
        self.draw()
        self.show()
        self.timer.start(100)
        self.timer.timeout.connect(self.update)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GameBoard()
    sys.exit(app.exec_())
