import sys
import io
import time
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage
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
        Initialize a meeple
        :param Image image: The image to draw on
        :param initial_position: The initial position
        """
        self.image = image
        self.drawer = ImageDraw.Draw(self.image)
        self.x = initial_position[0]
        self.y = initial_position[1]
        self.color = "blue"
        self.size = 20
        self.vector = Vector(10.5, 10.5)

    def draw(self):
        top_left = (self.x - (self.size/2), self.y - (self.size/2))
        bottom_right = (self.x + (self.size/2), self.y + (self.size/2))
        shape = [top_left, bottom_right]
        self.drawer.rectangle(shape, self.color)

    def update(self):
        self.move((self.x + self.vector.x, self.y + self.vector.y))
        if self.x > self.image.width:
            self.move((0, self.y))
        if self.x < 0:
            self.move((self.image.width, self.y))
        if self.y > self.image.height:
            self.move((self.x, 0))
        if self.y < 0:
            self.move((self.x, self.image.height))

    def move(self, new_position):
        self.x, self.y = new_position


class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 1000

        self.resize(self.width, self.height)
        self.img = Image.new('RGB', (self.width, self.height), color='black')
        self.drawer = ImageDraw.Draw(self.img)
        self.meeple = Meeple(self.img, (self.width/2, self.height/2))

        self.label = QLabel(self)

        self.timer = QTimer()
        self.timer.start(100)
        self.timer.timeout.connect(self.update)

    def draw(self):
        self.drawer.rectangle([(0, 0), (self.width, self.height)], "black")
        self.meeple.draw()
        self.label.setPixmap(pil2pixmap(self.img))
        self.show()

    def update(self):
        self.meeple.update()
        self.meeple.vector.x += random.randint(-10, 10)
        self.meeple.vector.y += random.randint(-10, 10)
        self.draw()

    def get_image(self):
        return self.img

    def get_pixel(self, x, y):
        rgb_im = self.img.convert('RGB')
        return rgb_im.getpixel((x, y))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameBoard()
    sys.exit(app.exec_())
