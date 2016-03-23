from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QEvent
from PyQt5.QtWidgets import QSizePolicy, QScrollArea

from nefi2.controller.left_panel_controller import *


class MidPanelWidget(QWidget):
    def __init__(self, mid_panel, auto_fit):
        super(MidPanelWidget, self).__init__()

        self.auto_fit = auto_fit
        self.current_image_original = None
        self.current_image_size = 1.0
        self.mid_panel = mid_panel
        self.offset = 0
        self.pixels_x = None
        self.pixels_y = None

        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(False)

        self.scrollArea = QScrollAreaFiltered()
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.Layout = QVBoxLayout()
        self.Layout.addWidget(self.scrollArea, Qt.AlignCenter)
        self.setLayout(self.Layout)

        self.scrollArea.zoom_in.connect(self.zoom_in_)
        self.scrollArea.zoom_out.connect(self.zoom_out_)
        self.scrollArea.horizontalScrollBar().rangeChanged[int, int].connect(
            lambda min, max: self.handle_zoom_x(min, max, ))
        self.scrollArea.verticalScrollBar().rangeChanged[int, int].connect(
            lambda min, max: self.handle_zoom_y(min, max, ))

    def mousePressEvent(self, QMouseEvent):
        self.setCursor(Qt.ClosedHandCursor)
        self.offset = QMouseEvent.pos()

    def mouseReleaseEvent(self, QMouseEvent):
        self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.buttons() & Qt.LeftButton:
            self.move(QMouseEvent.pos() - self.offset)

    def move(self, offset):
        self.scrollArea.verticalScrollBar().setSliderPosition(
            self.scrollArea.verticalScrollBar().value() - offset.y() / 50)
        self.scrollArea.horizontalScrollBar().setSliderPosition(
            self.scrollArea.horizontalScrollBar().value() - offset.x() / 50)

    def setPixmap(self, pixmap, mid_panel):
        self.set_current_image(pixmap)
        if self.auto_fit:
            self.resize_default()
        else:
            self.resize_original()

    def reset_image_size(self):
        self.current_image_size = 1.0

    def set_current_image(self, pixmap):
        self.current_image_original = pixmap

    def get_current_image(self):
        return self.current_image_original

    @pyqtSlot()
    def handle_zoom_y(self, min, max):

        if self.pixels_y is None:
            return

        delta = self.scrollArea.verticalScrollBar().maximum() - self.pixels_y
        # print("y delta " + str(delta))

        value = self.scrollArea.verticalScrollBar().value() + delta / 2
        self.scrollArea.verticalScrollBar().setValue(value)

        self.pixels_y = self.scrollArea.verticalScrollBar().maximum()

    @pyqtSlot()
    def handle_zoom_x(self, min, max):

        if self.pixels_x is None:
            return

        delta = self.scrollArea.horizontalScrollBar().maximum() - self.pixels_x
        # print("x delta " + str(delta))

        value = self.scrollArea.horizontalScrollBar().value() + delta / 2
        self.scrollArea.horizontalScrollBar().setValue(value)

        self.pixels_x = self.scrollArea.horizontalScrollBar().maximum()

    def zoom_out_(self):
        if not self.current_image_original:
            return
        if self.current_image_size < 0.1:
            return

        self.pixels_x = self.scrollArea.horizontalScrollBar().maximum()
        self.pixels_y = self.scrollArea.verticalScrollBar().maximum()

        self.current_image_size *= 0.85
        pixmap = self.current_image_original.scaled(self.current_image_original.width() * self.current_image_size,
                                                    self.current_image_original.width() * self.current_image_size,
                                                    QtCore.Qt.KeepAspectRatio, Qt.FastTransformation)

        self.imageLabel.setGeometry(0, 0, pixmap.width() + 22, pixmap.height() + 22)
        self.imageLabel.setPixmap(pixmap)

    def zoom_in_(self):
        if not self.current_image_original:
            return
        if self.current_image_size > 3:
            return

        self.pixels_x = self.scrollArea.horizontalScrollBar().maximum()
        self.pixels_y = self.scrollArea.verticalScrollBar().maximum()

        self.current_image_size *= 1.25
        pixmap = self.current_image_original.scaled(self.current_image_original.width() * self.current_image_size,
                                                    self.current_image_original.width() * self.current_image_size,
                                                    QtCore.Qt.KeepAspectRatio, Qt.FastTransformation)
        self.imageLabel.setGeometry(0, 0, pixmap.width() + 22, pixmap.height() + 22)
        self.imageLabel.setPixmap(pixmap)

    def resize_original(self):
        if not self.current_image_original:
            return

        self.current_image_size = 1.0
        self.imageLabel.setGeometry(0, 0, self.current_image_original.width() + 22,
                                    self.current_image_original.height() + 22)
        self.imageLabel.setPixmap(self.current_image_original)

    def resize_default(self, force=None):
        if not self.current_image_original:
            return
        if not self.auto_fit and not force:
            return
        original_width = self.current_image_original.width()
        if original_width != 0:
            self.current_image_size = self.mid_panel.width() / original_width

        new_pixmap = self.current_image_original.scaled(self.mid_panel.width() - 85, self.mid_panel.height() - 85,
                                                        QtCore.Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.imageLabel.setGeometry(0, 0, new_pixmap.width() + 22, new_pixmap.height() + 22)
        self.imageLabel.setPixmap(new_pixmap)

    def toggleAutofit(self):
        self.auto_fit = not self.auto_fit
        if self.auto_fit:
            self.resize_default()
        else:
            self.resize_original()


class QScrollAreaFiltered(QScrollArea):
    def __init__(self):super(QScrollAreaFiltered, self).__init__()

    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            if event.modifiers() & Qt.ControlModifier:
                if event.angleDelta().y() < 0:
                    self.zoom_out.emit()
                else:
                    self.zoom_in.emit()

                return True
        return False