import cv2
import numpy as np
import cvzone
from cvzone.HandTrackingModule import HandDetector
from time import sleep

# Khởi tạo webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
# Khởi tạo HandDetector
detector = HandDetector(detectionCon=0.8)

# Danh sách phím
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["Space"]]

finalText = ""

# Class phím
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Tạo danh sách các Button
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "Space":
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key, size=[500, 85]))
        else:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

# Hàm vẽ tất cả các phím
def drawAll(img, buttonList):
    imgNew = np.zeros_like(img, np.uint8)

    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Viền bo góc
        cvzone.cornerRect(imgNew, (x, y, w, h), 20, rt=0)

        # Nền phím
        cv2.rectangle(imgNew, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)

        # Căn giữa chữ
        displayText = "Space" if button.text == "Space" else button.text
        (text_width, _), _ = cv2.getTextSize(displayText, cv2.FONT_HERSHEY_PLAIN, 2, 3)
        text_x = x + (w - text_width) // 2
        cv2.putText(imgNew, displayText, (text_x, y + 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

    # Làm trong suốt bàn phím
    out = img.copy()
    alpha = 0.5
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, 1 - alpha, imgNew, alpha, 0)[mask]

    return out

# Vòng lặp chính
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    img = drawAll(img, buttonList)

    if hands:
        lmList = hands[0]['lmList']
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    # Highlight khi chạm
                    cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                    displayText = "Space" if button.text == "Space" else button.text
                    (text_width, _), _ = cv2.getTextSize(displayText, cv2.FONT_HERSHEY_PLAIN, 4, 4)
                    text_x = x + (w - text_width) // 2
                    cv2.putText(img, displayText, (text_x, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    # Đo khoảng cách giữa ngón trỏ và ngón giữa
                    l, _, _ = detector.findDistance(lmList[8][:2], lmList[12][:2])
                    if l < 30:
                        # Highlight khi click
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, displayText, (text_x, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                        # Thêm ký tự vào văn bản
                        if button.text == "Space":
                            finalText += " "
                        else:
                            finalText += button.text
                        sleep(0.25)

    # Hiển thị văn bản đã nhập
    cv2.rectangle(img, (50, 550), (1180, 670), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 640), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)
    cv2.waitKey(1)