import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

color_search = np.zeros((200, 200, 3), np.uint8)
color_selected = np.zeros((200, 200, 3), np.uint8)

hue = 0


def select_color(event, x, y, flags, param):
    global hue

    B = frame[y, x][0]
    G = frame[y, x][1]
    R = frame[y, x][2]
    color_search[:] = (B, G, R)

    if event == cv2.EVENT_LBUTTONDOWN:
        color_selected[:] = (B, G, R)
        hue = hsv[y, x][0]


def search_contours(mask):
    contours_count = 0
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if 200 < area < 10000:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            contours_count += 1

            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            cv2.circle(frame, (cX, cY), 3, (255, 255, 255), -1)
            cv2.putText(frame, f"{contours_count}", (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255),
                        2)

    return contours_count


def nothing(x):
    pass


cv2.namedWindow('image')
cv2.setMouseCallback('image', select_color)

cv2.namedWindow('Trackbars')
cv2.resizeWindow('Trackbars', 400, 80)

cv2.createTrackbar('Lower-Hue', 'Trackbars', 14, 179, nothing)
cv2.createTrackbar('Upper-Hue', 'Trackbars', 18, 179, nothing)

while True:

    _, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    diff_lower_hue = cv2.getTrackbarPos('Lower-Hue', 'Trackbars')
    diff_upper_hue = cv2.getTrackbarPos('Upper-Hue', 'Trackbars')

    lower_hue = 0 if hue - diff_lower_hue < 0 else hue - diff_lower_hue
    upper_hue = hue + diff_upper_hue if hue + diff_upper_hue < 179 else 179

    lower_hsv = np.array([lower_hue, 50, 20])
    upper_hsv = np.array([upper_hue, 255, 255])

    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    count = search_contours(mask)

    cv2.putText(frame, f'Total: {count}', (5, 30), font, 1, (255, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('mask', mask)
    cv2.imshow('image', frame)
    cv2.imshow('color_search', color_search)
    cv2.imshow('color_selected', color_selected)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
