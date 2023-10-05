import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QPushButton
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np

labels = []
captures = []
buttons = []
current_frames = [0, 0, 0, 0]
saved_backgrounds = [0, 0, 0, 0]
background_check_flags = [0, 0, 0, 0]
show_images = [0, 0, 0, 0]

class VideoThread(QThread):
    frame_update = pyqtSignal(int, np.ndarray)

    def __init__(self, index):
        super().__init__()
        self.index = index
        print("Thread", index, " Created")

    def run(self):
        print("Thread", self.index, " starts running")
        cap = cv2.VideoCapture(str(self.index) + ".mp4")
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # if background_check_flags[self.index] == 0:
                #     saved_backgrounds[self.index] = frame
                #     show_images[self.index] = frame
                #     background_check_flags[self.index] = 1
                # gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # gray2 = cv2.cvtColor(saved_backgrounds[self.index], cv2.COLOR_BGR2GRAY)
                # diff = cv2.absdiff(gray1, gray2)
                # _, threshold = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                # saved_backgrounds[self.index] = frame
                # kernel = np.ones((1, 1), np.uint8)
                # opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
                # closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
                # _, threshold = cv2.threshold(closing, 127, 255, cv2.THRESH_BINARY)
                # contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # contour_image = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)
                # cv2.drawContours(show_images[self.index], contours, -1, (0, 255, 0), 2)
                # similarity = ssim(gray1, gray2)
                # saved_backgrounds[self.index] = frame
                # if similarity < 0.75:
                #     background_check_flags[self.index] = 0
                #     print("!!!!!!!!!!!!Background Has Changed!!!!!!!!!!!!!!")
                # self.frame_update.emit(self.index, show_images[self.index])
                # cv2.imshow(str(self.index), frame)
                print(ret, self.index)

class SimpleDialog(QDialog):
    def __init__(self, message, index):
        super().__init__()
        self.setWindowTitle("Camera " + str(index + 1))
        self.setStyleSheet("background-color: pink;")
        self.index = index
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_height = int(screen_geometry.height() * 0.9)
        height, width, channel = show_images[self.index].shape
        screen_width = int(screen_height * width / height)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        self.label.setStyleSheet("border: 2px solid purple; background-color: #f0f0f0;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        timer = QTimer(self)
        timer.timeout.connect(self.display_frame)
        timer.start(100)
        self.show()

    def display_frame(self):
        height, width, channel = show_images[self.index].shape
        bytes_per_line = channel * width
        q_image = QImage(show_images[self.index].data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = q_pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)

def button_clicked(button_index):
    print(f"Button {button_index+1} clicked")
    dialog = SimpleDialog("This is a simple dlg.", button_index)
    dialog.exec_()

class VideoStreamWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("High Rise Littering Detection System")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setStyleSheet("background-color: pink;")
        self.showMaximized()
        self.is_focus = False
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        screen = app.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        label_width_percentage = 0.3
        label_height_percentage = 0.45
        for i in range(4):
            label = QLabel(f"Square {i+1}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid purple; background-color: #f0f0f0;")
            labels.append(label)
            layout.addWidget(labels[i], 0, i)
            captures.append(cv2.VideoCapture(str(i) + ".mp4"))
            button = QPushButton(f"Input {i+1}")
            buttons.append(button)
            layout.addWidget(button, 1, i)
            button.clicked.connect(lambda _, index=i: button_clicked(index))
            thread = VideoThread(i)
            thread.frame_update.connect(self.display_frame)
            thread.start()
        self.show()

    def display_frame(self, index, frame):
        labels[index].setPixmap(QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)))

app = QApplication([])
window = VideoStreamWindow()
app.exec_()