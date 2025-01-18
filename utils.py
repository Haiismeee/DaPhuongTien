import cv2
import numpy as np

def adjust_brightness(image, brightness=50):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, brightness)
    v = np.clip(v, 0, 255)
    final_hsv = cv2.merge((h, s, v))
    bright_image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return bright_image

def blur_background(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
    blurred = cv2.GaussianBlur(image, (21, 21), 0)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    result = np.where(mask == 0, blurred, image)
    return result

def cartoon_effect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(image, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def oil_paint_effect(image):
    oil_painting = cv2.xphoto.oilPainting(image, 7, 1)
    return oil_painting
