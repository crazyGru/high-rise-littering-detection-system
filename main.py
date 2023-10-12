import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import threading
import numpy as np
import time

DEFAULT_WINDOW_WIDTH = 500
DEFAULT_WINDOW_HEIGHT = 300

labels = []
captures = []
buttons = []
fullscreen_flags = []
current_frames = []
saved_backgrounds = []
background_check_flags = [0, 0, 0, 0]
show_images = []
fullscreen_focus_part = []
test_thread = 0
val = 0
area_center_point = {"x": 100.0, "y": 100.0}
default_edge_length = 100.0
default_scale = 1.0
stream_width = 0
stream_height = 0
running_app = True

is_recording = False

recording_index = 1

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 10
frame_size = (640, 480)
output_filename = "output.mp4"
out = cv2.VideoWriter(output_filename, fourcc, fps, frame_size)


def mainThread():
    global test_thread
    global show_images
    global current_frames
    global is_recording
    global output_filename
    global frame_size
    global out
    global recording_index
    index = 0
    while running_app:
        if len(current_frames):
            current_gray = cv2.cvtColor(current_frames[index], cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(current_gray, saved_backgrounds[index])

            hist = cv2.calcHist([diff], [0], None, [256], [0, 256])

            min_value = 0
            for i in range(256):
                min_value+=hist[i]*i

            min_value = min_value / (sum(hist[10:])+0.0000001)
            _, threshold = cv2.threshold(diff, int(min_value), 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print(len(contours), is_recording, recording_index)

            if len(contours) <= 50:
                if is_recording:
                    out.release()
                    recording_index = recording_index + 1
                    is_recording = False
                continue
            elif len(contours) <= 200:
                if is_recording == False:
                    output_filename = str(recording_index) + ".mp4"
                    frame_size = (stream_width, stream_height)
                    out = cv2.VideoWriter(output_filename, fourcc, fps, frame_size)
                is_recording = True
                
            cv2.drawContours(show_images[index], contours, -1, (0, 255, 0), 3)
            temp = show_images[index][int((area_center_point["y"] - default_scale * default_edge_length) / DEFAULT_WINDOW_HEIGHT * stream_height):
                                      int((area_center_point["y"] + default_scale * default_edge_length) / DEFAULT_WINDOW_HEIGHT * stream_height),
                                      int((area_center_point["x"] - default_scale * default_edge_length) / DEFAULT_WINDOW_WIDTH * stream_width):
                                      int((area_center_point["x"] + default_scale * default_edge_length) / DEFAULT_WINDOW_WIDTH * stream_width)]
            fullscreen_focus_part[index] = cv2.resize(temp, (int(default_edge_length / DEFAULT_WINDOW_HEIGHT * stream_height),
                                                             int(default_edge_length / DEFAULT_WINDOW_HEIGHT * stream_height)))
            
            
            
            
            


main_thread = threading.Thread(target=mainThread)
main_thread.start()


def button_clicked(button_index):
    fullscreen_flags[button_index] = 1 - fullscreen_flags[button_index]

def read_video(camera_name, camera_url):
    reconnect_time = 30
    connection_flag = True
    total_tries = 10

    while(connection_flag == True or total_tries > 0):
        try:
            # read video
            cap = cv2.VideoCapture(camera_url)
            # check if connection failed
            if cap is None or not cap.isOpened():
                raise ConnectionError
            else:
                connection_flag = False
        # if connection failed, retry in 30 seconds
        except ConnectionError:
            print("Retrying connection to ", camera_name," in ", str(reconnect_time), " seconds...")
            time.sleep(reconnect_time)

        total_tries -= 1
    return cap

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

        for i in range(1):
            label = QLabel(f"Square {i + 1}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid purple; background-color: #f0f0f0;")
            label.setFixedSize(500, 300)
            labels.append(label)
            layout.addWidget(labels[i], 0, i)

            captures.append(cv2.VideoCapture("rtsp://admin:slowmonth49@192.168.1.100:554/Streaming/channels/101/"))
            # captures.append (cv2.VideoCapture(str(i)+".mp4"))
            # captures.append(read_video("Camera 1", str(i)+".mp4"))
            fullscreen_flags.append(0)

            button = QPushButton(f"Input {i + 1}")
            buttons.append(button)
            layout.addWidget(button, 1, i)
            button.clicked.connect(lambda _, index=i: button_clicked(index))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(100)
        self.show()

    def update_frames(self):
        for i in range(1):
            ret, frame = captures[i].read()
            if ret:
                mini_view = cv2.resize(frame, (500, 300))
                self.display_frame(labels[i], mini_view)
                if background_check_flags[i] == 0:
                    global stream_height, stream_width
                    stream_height, stream_width, _ = frame.shape
                    saved_backgrounds.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                    show_images.append(frame)
                    current_frames.append(frame)
                    fullscreen_focus_part.append(frame[int(area_center_point["y"] - default_scale * default_edge_length):
                                                       int(area_center_point["y"] + default_scale * default_edge_length),
                                                       int(area_center_point["x"] - default_scale * default_edge_length):
                                                       int(area_center_point["x"] + default_scale * default_edge_length)])
                    background_check_flags[i] = 1
                current_frames[i] = frame
                if is_recording:
                    out.write(show_images[i])
                # elif len(current_frames):
                #     out.release()
                if fullscreen_flags[i]:
                    cv2.imshow("Camera" + str(i), fullscreen_focus_part[i])
                else:
                    try:
                        cv2.destroyWindow("Camera" + str(i))
                    except cv2.error as e:
                        pass
                    continue

    def display_frame(self, label, frame):
        cv2.rectangle(frame, (int(area_center_point["x"] - default_scale * default_edge_length),
                              int(area_center_point["y"] - default_scale * default_edge_length)),
                      (int(area_center_point["x"] + default_scale * default_edge_length),
                       int(area_center_point["y"] + default_scale * default_edge_length)),
                      (0, 255, 0), 2)
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(q_pixmap)

    def keyPressEvent(self, event):
        key = event.key()
        global default_scale
        if key == Qt.Key_E:
            default_scale += 0.1
        elif key == Qt.Key_Q:
            default_scale -= 0.1
        elif key == Qt.Key_W:
            area_center_point["y"] -= 10
            if area_center_point["y"] < default_scale * default_edge_length:
                area_center_point["y"] = default_scale * default_edge_length
        elif key == Qt.Key_A:
            area_center_point["x"] -= 10
            if area_center_point["x"] < default_scale * default_edge_length:
                area_center_point["x"] = default_scale * default_edge_length
        elif key == Qt.Key_S:
            area_center_point["y"] += 10
            if area_center_point["y"] > DEFAULT_WINDOW_HEIGHT - default_scale * default_edge_length:
                area_center_point["y"] = DEFAULT_WINDOW_HEIGHT - default_scale * default_edge_length
        elif key == Qt.Key_D:
            area_center_point["x"] += 10
            if area_center_point["x"] > DEFAULT_WINDOW_WIDTH - default_scale * default_edge_length:
                area_center_point["x"] = DEFAULT_WINDOW_WIDTH - default_scale * default_edge_length





app = QApplication([])
window = VideoStreamWindow()
app.exec_()
cv2.destroyAllWindows()
running_app = False
out.release()