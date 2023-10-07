import cv2
import numpy as np
import threading

# Define a function to be executed in the thread

def convert_to_gray(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Perform further operations with the gray image if needed

# Load the image
image = cv2.imread('1.jpg')

# Create a thread for converting to gray
gray_thread = threading.Thread(target=convert_to_gray, args=(image,))
gray_thread.start()

# Continue with the rest of the code here

# Wait for the thread to finish
gray_thread.join()

# Continue with the rest of the code
# You can access the converted gray image within the thread function if needed