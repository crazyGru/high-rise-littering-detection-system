import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np

labels = []
captures = []
buttons = []
fullscreen_flags = []
is_opened_flags = []
current_frames = [0,0,0,0]
saved_backgrounds = [0,0,0,0]
background_check_flags = [0,0,0,0]
show_images = [0,0,0,0]

class SimpleDialog(QDialog):
    def __init__(self, message, index):
        super().__init__()
        self.setWindowTitle("Camera " + str(index+1))
        self.setStyleSheet("background-color: pink;")
        self.index = index
        
        # Get the screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_height = int(screen_geometry.height() * 0.9)
        height, width, channel = show_images[self.index].shape
        screen_width = int(screen_height * width / height)
        
        # Set the dialog height to match the screen height
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        self.label.setStyleSheet("border: 2px solid purple; background-color: #f0f0f0;")  # Set border and background color
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
        
        # Scale the pixmap to fill the window
        scaled_pixmap = q_pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        self.label.setPixmap(scaled_pixmap)

def button_clicked(button_index):
    # Perform actions based on the button index
    # print(f"Button {button_index+1} clicked")
    # dialog = SimpleDialog ( "This is a simpel dlg.", button_index)
    # dialog.exec_()
    # Add your custom code here
    fullscreen_flags[button_index] = 1 - fullscreen_flags[button_index]

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
        layout.setContentsMargins(10, 10, 10, 10)  # Add some margins to the layout

        screen = app.primaryScreen()
        screen_geometry = screen.geometry()

        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        label_width_percentage = 0.3
        label_height_percentage = 0.45
        

        for i in range(1):
            label = QLabel(f"Square {i+1}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid purple; background-color: #f0f0f0;")  # Set border and background color
            label.setFixedSize(1000,800)
            
            labels.append(label)
            layout.addWidget(labels[i], 0, i)  # Add the label to the layout
            # rtsp_link = "rtsp://admin:slowmonth49@192.168.1.100:554/Streaming/channels/101/"
            captures.append(cv2.VideoCapture("rtsp://admin:slowmonth49@192.168.1.100:554/Streaming/channels/101/"))
            # captures.append(cap)
            # cap.set(cv2.CAP_PROP_USERNAME, username)
            # cap.set(cv2.CAP_PROP_PASSWORD, password)
            # captures.append (cv2.VideoCapture(str(i)+".mp4"))
            fullscreen_flags.append(0)
            is_opened_flags.append(0)
            # captures.append (cv2.VideoCapture(i))

            button = QPushButton(f"Input {i+1}")
            buttons.append(button)  # Add the button to the list
            layout.addWidget(button, 1, i)  # Add the button to the layout

            button.clicked.connect(lambda _, index=i: button_clicked(index))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(0)

        self.show()

    def update_frames(self):
        # len(captures)
        for i in range(1):
            ret, frame = captures[i].read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if background_check_flags[i] == 0:
                    saved_backgrounds[i] = frame
                    show_images[i] = frame

                    # background_check_flags[i] = 1
                    
                # gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # gray2 = cv2.cvtColor(saved_backgrounds[i], cv2.COLOR_BGR2GRAY)

                # _, binary1 = cv2.threshold(gray1, 150, 255, cv2.THRESH_BINARY)
                # _, binary2 = cv2.threshold(gray2, 150, 255, cv2.THRESH_BINARY)

                # diff = cv2.absdiff(gray1, gray2)      
                # # cv2.imshow(str(i), diff)          
                # _, threshold = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                # cv2.imshow(str(i)+"threshold", threshold)          
                

                # saved_backgrounds[i] = frame               

                # cv2.imshow("temp", threshold)

                # kernel = np.ones((1, 1), np.uint8)
                # opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
                # closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
                
                # cv2.imshow("noise reduced", closing)
                # _, threshold = cv2.threshold(closing, 127, 255, cv2.THRESH_BINARY)
                # contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # contour_image = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)
                # cv2.drawContours(show_images[i], contours, -1, (0, 255, 0), 2)

                # cv2.imshow("detection", show_images[i])

                # similarity = ssim(gray1, gray2)
                # saved_backgrounds[i] = frame
                # if similarity < 0.95:
                #     background_check_flags[i] = 0
                    # print("!!!!!!!!!!!!Background Has Changed!!!!!!!!!!!!!!")
                    # self.timer.stop()
                # print("Similarity:", similarity)

                if fullscreen_flags[i]:
                    cv2.imshow("Camera"+str(i), frame)
                    is_opened_flags[i] = 1
                elif is_opened_flags[i]:
                    try:
                        cv2.destroyWindow("Camera" + str(i))
                    except cv2.error as e:
                        print("An error occurred:", e)

                
                self.display_frame(labels[i], show_images[i])

    def display_frame(self, label, frame):
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(q_pixmap)

app = QApplication([])
window = VideoStreamWindow()
app.exec_()