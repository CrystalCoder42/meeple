from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage
import sys
import io
from PIL import Image


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


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 image - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.run()

    def run(self):
        img = Image.new('RGB', (1000, 1000), color='black')
        self.setWindowTitle(self.title)

        # Create widget
        label = QLabel(self)
        label.setPixmap(pil2pixmap(img))
        self.resize(img.width, img.height)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
