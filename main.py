# main.py

import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time
import threading

detector = HandDetector(detectionCon=0.8, maxHands=1)

time.sleep(2.0)

video = cv2.VideoCapture(0)

space_key_down = False
down_arrow_key_down = False
key_press_interval = 1.0  # Set the interval for key presses in seconds
last_key_press_time = time.time()

def handle_key_press():
    global space_key_down, down_arrow_key_down, last_key_press_time

    current_time = time.time()

    if space_key_down and current_time - last_key_press_time >= key_press_interval:
        pyautogui.keyUp('space')
        space_key_down = False
    elif down_arrow_key_down and current_time - last_key_press_time >= key_press_interval:
        pyautogui.keyUp('down')
        down_arrow_key_down = False

def process_frames():
    global space_key_down, down_arrow_key_down, last_key_press_time

    while True:
        ret, frame = video.read()
        hands, img = detector.findHands(frame)
        cv2.rectangle(img, (0, 480), (300, 425), (50, 50, 255), -2)
        cv2.rectangle(img, (640, 480), (400, 425), (50, 50, 255), -2)

        if hands:
            lmList = hands[0]
            fingerUp = detector.fingersUp(lmList)
            print(fingerUp)

            current_time = time.time()

            if fingerUp == [0, 1, 1, 1, 1] and not down_arrow_key_down:
                cv2.putText(frame, 'Finger Count: 1', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1,
                            cv2.LINE_AA)
                cv2.putText(frame, 'Crouching', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                if not space_key_down:
                    pyautogui.keyDown('down')
                    down_arrow_key_down = True
                    last_key_press_time = current_time
            elif fingerUp == [0, 0, 0, 0, 0] and not space_key_down:
                cv2.putText(frame, 'Finger Count: 0', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1,
                            cv2.LINE_AA)
                cv2.putText(frame, 'Jumping', (440, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                pyautogui.keyDown('space')
                space_key_down = True
                last_key_press_time = current_time
            else:
                cv2.putText(frame, 'Finger Count: 0', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1,
                            cv2.LINE_AA)
                cv2.putText(frame, 'Not Crouching', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1,
                            cv2.LINE_AA)
                if space_key_down:
                    pyautogui.keyUp('space')
                if down_arrow_key_down:
                    pyautogui.keyUp('down')
                space_key_down = False
                down_arrow_key_down = False

        cv2.imshow("Frame", frame)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

# Create threads
threading.Thread(target=handle_key_press).start()
threading.Thread(target=process_frames).start()
  
