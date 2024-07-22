from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPixmap, QPainter, QBrush
from PySide2.QtWidgets import QLabel


class SignalLight(QLabel):
    def __init__(self, parent=None):
        super(SignalLight, self).__init__(parent)
        self.setFixedSize(20, 20)  # Increase size to give more space for drawing
        self.set_status(True)  # Initialize to disconnected status

    def set_status(self, connected):
        diameter = min(self.width(), self.height()) - 10  # Subtract some margin
        pixmap = QPixmap(self.width(), self.height())
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        if connected:
            painter.setBrush(QBrush(QColor('green')))
        else:
            painter.setBrush(QBrush(QColor('red')))

        painter.drawEllipse(5, 5, diameter, diameter)  # Draw with some margin
        painter.end()

        self.setPixmap(pixmap)
