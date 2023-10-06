import cv2
import numpy as np

# Load the image
image = cv2.imread('test.png')

# Convert the image to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Split the HSV image into separate channels
h, s, v = cv2.split(hsv_image)

# Calculate the histogram of the hue channel
hist = cv2.calcHist([h], [0], None, [180], [0, 180])

# Normalize the histogram to get the frequency percent for each color
hist = hist / hist.sum() * 100

# Print the frequency percent of each color
for i, percent in enumerate(hist):
    print(f"Color {i}: {percent}%")