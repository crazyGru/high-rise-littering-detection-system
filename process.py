import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np
import threading
# import matplotlib.pyplot as plt

labels = []
captures = []
buttons = []
fullscreen_flags = []
current_frames = []
saved_backgrounds = []
background_check_flags = [0,0,0,0]
show_images = []

test_thread = 0
val=0

def mainThread():
    global test_thread
    global show_images
    global current_frames
    index = 0
    while True:
        if len(current_frames):
            current_gray = cv2.cvtColor(current_frames[index], cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(current_gray, saved_backgrounds[index])      
            # hist = cv2.calcHist([diff], [0], None, [256], [0, 256])
            # hist = hist / hist.sum() * 100
            # hist_normalized = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
            _, threshold = cv2.threshold(diff, 120, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(show_images[index], contours, -1, (0, 255, 0), 2)


        # print(test_thread)


main_thread = threading.Thread(target = mainThread)
main_thread.start()

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
            label.setFixedSize(500,300)
            
            labels.append(label)
            layout.addWidget(labels[i], 0, i)  # Add the label to the layout
            # rtsp_link = "rtsp://admin:slowmonth49@192.168.1.100:554/Streaming/channels/101/"
            # captures.append(cv2.VideoCapture("rtsp://admin:slowmonth49@192.168.1.100:554/Streaming/channels/101/"))
            # captures.append(cap)
            # cap.set(cv2.CAP_PROP_USERNAME, username)
            # cap.set(cv2.CAP_PROP_PASSWORD, password)
            captures.append (cv2.VideoCapture(str(i)+".mp4"))
            fullscreen_flags.append(0)
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
                # print(test_thread)
                frame = cv2.resize(frame, (500, 300))
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_frame(labels[i], frame)
                
                if background_check_flags[i] == 0:
                    saved_backgrounds.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                    show_images.append(frame)
                    current_frames.append(frame)

                    background_check_flags[i] = 1
                
                current_frames[i]=frame

                if fullscreen_flags[i]:
                    cv2.imshow("Camera"+str(i), show_images[i])
                else:
                    try:
                        cv2.destroyWindow("Camera" + str(i))
                    except cv2.error as e:
                        a=0
                    continue



                
                    
                # gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # gray2 = cv2.cvtColor(saved_backgrounds[i], cv2.COLOR_BGR2GRAY)

                # _, binary1 = cv2.threshold(gray1, 150, 255, cv2.THRESH_BINARY)
                # _, binary2 = cv2.threshold(gray2, 150, 255, cv2.THRESH_BINARY)

                # diff = cv2.absdiff(gray_current, saved_backgrounds[i])      
                # gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                # hist = cv2.calcHist([diff], [0], None, [256], [0, 256])
                # hist = hist / hist.sum() * 100
                # hist_normalized = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)

                
                # if hist.max != 0:
                    # fig, ax = plt.subplots()
                    # ax.plot(hist_normalized)

                    # ax.set_xlabel('Pixel Value')
                    # ax.set_ylabel("Frequency")
                    # ax.set_title("Histogram")
                    # plt.show()

                    # sum=0
                    # for j, bin_val in enumerate(hist):
                    #     print(j, ':', bin_val[0])
                    #     sum+=bin_val[0]
                    # print(sum)
                    # total_sum = np.sum(hist_normalized)
                    # print(total_sum)

                # self.timer.stop()
                # # cv2.imshow(str(i), diff)          
                # _, threshold = cv2.threshold(diff, 120, 255, cv2.THRESH_BINARY)
                # cv2.imshow(str(i)+"threshold", threshold)          
                

                # saved_backgrounds[i] = frame               

                # cv2.imshow("temp", threshold)

                # kernel = np.ones((1, 1), np.uint8)
                # opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
                # closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
                
                # cv2.imshow("noise reduced", closing)
                # _, threshold = cv2.threshold(closing, 127, 255, cv2.THRESH_BINARY)
                # contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # contour_image = cv2.cvtColor(threshold, cv2.COLOR_GRAY2BGR)
                # contour_image = cv2.cvtColor(closing, cv2.COLOR_GRAY2BGR)
                # cv2.drawContours(show_images[i], contours, -1, (0, 255, 0), 2)

                # route = []
                # for contour in contours:
                #     for point in contour:
                #         x, y = point[0]
                #         route.append((x, y))
                #         cv2.circle(show_images[i], (x, y), 2, (0, 255, 0), -1)

                # if len(route) > 1:
                #     cv2.polylines(show_images[i], np.array([route], dtype=np.int32), False, (0, 255, 0), 1)

                # cv2.imshow("detection", show_images[i])

                # similarity = ssim(gray1, gray2)
                # saved_backgrounds[i] = frame
                # if similarity < 0.95:
                #     background_check_flags[i] = 0
                    # print("!!!!!!!!!!!!Background Has Changed!!!!!!!!!!!!!!")
                    # self.timer.stop()
                # print("Similarity:", similarity)              

                
                

    def display_frame(self, label, frame):
        height, width, channel = frame.shape
        # frame = cv2.resize(frame, (width//2, height//2))
        bytes_per_line = channel * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(q_pixmap)



app = QApplication([])
window = VideoStreamWindow()
app.exec_()