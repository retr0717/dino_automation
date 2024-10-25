import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time
import threading
import numpy as np

# Initialize the hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Initialize video capture
video = cv2.VideoCapture(0)

# Global variables with thread lock
space_key_down = False
down_arrow_key_down = False
key_press_interval = 1.0
last_key_press_time = time.time()
lock = threading.Lock()

def handle_key_press():
    """Function to release keys based on timing."""
    global space_key_down, down_arrow_key_down, last_key_press_time

    while True:
        with lock:
            current_time = time.time()

            if space_key_down and current_time - last_key_press_time >= key_press_interval:
                pyautogui.keyUp('space')
                space_key_down = False
            elif down_arrow_key_down and current_time - last_key_press_time >= key_press_interval:
                pyautogui.keyUp('down')
                down_arrow_key_down = False

        time.sleep(0.01)  # Prevent busy-waiting

def process_frames():
    """Function to process frames and detect gestures."""
    global space_key_down, down_arrow_key_down, last_key_press_time

    if not video.isOpened():
        print("Error: Could not open video.")
        exit(1)

    while True:
        ret, frame = video.read()
        if not ret:
            print("Failed to grab frame.")
            break

        hands, img = detector.findHands(frame)
        img = np.asarray(img, dtype=np.uint8)

        cv2.rectangle(img, (0, 480), (300, 425), (50, 50, 255), -2)
        cv2.rectangle(img, (640, 480), (400, 425), (50, 50, 255), -2)

        if hands:
            lmList = hands[0]
            fingerUp = detector.fingersUp(lmList)
            print(fingerUp)  # Debugging output

            current_time = time.time()

            if fingerUp == [0, 1, 1, 1, 1] and not down_arrow_key_down:
                cv2.putText(img, 'Crouching', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                with lock:
                    pyautogui.keyDown('down')
                    down_arrow_key_down = True
                    last_key_press_time = current_time

            elif fingerUp == [0, 0, 0, 0, 0] and not space_key_down:
                cv2.putText(img, 'Jumping', (440, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                with lock:
                    pyautogui.keyDown('space')
                    space_key_down = True
                    last_key_press_time = current_time

            else:
                with lock:
                    if space_key_down:
                        pyautogui.keyUp('space')
                    if down_arrow_key_down:
                        pyautogui.keyUp('down')
                    space_key_down = False
                    down_arrow_key_down = False

        cv2.imshow("Frame", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

def main():
    """Main function to start the threads."""
    threading.Thread(target=handle_key_press, daemon=True).start()
    threading.Thread(target=process_frames, daemon=True).start()

    # Keep the main thread alive to allow threads to run
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()