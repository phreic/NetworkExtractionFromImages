from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout


class ImmediateResultWidget(QWidget):
    """
    this widget is used in the left panel of the GUI. All intermediate
    result images are packed into a LeftCustomWidget and appended to the
    according vbox_layout of the Mainview.ui
    """

    select_image = pyqtSignal()

    def __init__(self, image_path, MidCustomWidget, mid_panel, left_scroll_results, slot, pipeline, settings_widget, left_slider, cat=None):
        super(ImmediateResultWidget, self).__init__()

        self.setStyleSheet("font:Candara; font-size: 8pt;")
        self.MidCustomWidget = MidCustomWidget
        self.mid_panel = mid_panel
        self.left_scroll_results = left_scroll_results
        self.cat = cat
        self.pipeline = pipeline
        self.settings_widget = settings_widget
        self.left_slider = left_slider
        self.step = 0

        self.image_label = QLabel()

        if cat is None:
            self.image_name = "Input - Image"
        else:
            self.setToolTip("Click here while holding 'CTRL' button to see used settings .")
            index = self.pipeline.get_index(self.cat)
            if index is not (len(self.pipeline.executed_cats) - 1):
                self.image_name = str(cat.get_name() + " - " + cat.active_algorithm.name)
            else:
                self.image_label.setStyleSheet("background-color: green; font:Candara; font-size: 8pt;")
                self.image_name = "Result image - " + str(cat.get_name() + " - " + cat.active_algorithm.name)
            self.step = self.pipeline.get_index(cat) + 1
        self.slot = slot
        # self.setGeometry(0, 0, 300, 100)

        self.LeftCustomWidgetLayout = QVBoxLayout()
        self.setLayout(self.LeftCustomWidgetLayout)
        self.LeftCustomWidgetLayout.setAlignment(Qt.AlignTop)

        self.image_label.setText(self.image_name)
        self.image_label.setGeometry(0, 0, 150, 30)

        self.pixmap = QPixmap(image_path)
        self.pixmap_scaled_keeping_aspec = self.pixmap.scaledToWidth(280, Qt.SmoothTransformation)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setGeometry(0, 0, 330, self.pixmap_scaled_keeping_aspec.height())
        self.image.setPixmap(self.pixmap_scaled_keeping_aspec)

        self.LeftCustomWidgetLayout.addWidget(self.image_label)
        self.LeftCustomWidgetLayout.addWidget(self.image)
        if cat:
            self.createSettings()
            self.settings_widget.hide()
            self.LeftCustomWidgetLayout.addWidget(self.settings_widget)

        self.setGeometry(0, 0, 330, self.image_label.height() + self.image.height())

        self.select_image.connect(lambda: self.slot(self.MidCustomWidget.getCurrentImage(), self.cat))

    def mousePressEvent(self, QMouseEvent):
        """
        this events sets the self.pixmap from this custom widget
        into the middle panel of the GUI. Or more general: by clicking
        on this widget the users wants to see this picture in the big display
        area of the middle.

        Args:
            | *event*: the mouse press event
        """
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            try:
                if self.step == 0 or self.cat is None:
                    self.mid_panel.setTitle(self.image_name)
                else:
                    index = self.pipeline.get_index(self.cat)
                    if index is not (len(self.pipeline.executed_cats) - 1):
                        self.mid_panel.setTitle(self.image_name + " - Pipeline Position " + str(index + 1))
                    else:
                        self.setStyleSheet("font:Candara; font-size: 8pt;")
                        self.mid_panel.setTitle("Result image - " + self.image_name + " - Pipeline Position " + str(index + 1))
            except (ValueError):
                self.mid_panel.setTitle(self.image_name + " - Already Removed From Pipeline")

            self.MidCustomWidget.setCurrentImage(self.pixmap)

            # Connect the trigger signal to a slot.
            # Emit the signal.
            self.select_image.emit()

            if (QMouseEvent.modifiers() & Qt.ControlModifier):

                if self.settings_widget:
                    if self.settings_widget.isVisible():
                        self.settings_widget.hide()
                    else:
                        self.settings_widget.show()

    def createSettings(self):
        self.settings_widget.setDisabled(True)
        self.settings_widget.setStyleSheet("color:silver;")