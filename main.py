import os
import json
import cv2
import pytesseract
import time

project_root = os.path.dirname(__file__)
if os.name == "nt":
    tesseract_cmd = os.path.join(project_root, "Tesseract-OCR", "tesseract.exe")
else:
    tesseract_cmd = "tesseract"
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
tessdata_dir = os.path.join(project_root, "Tesseract-OCR", "tessdata")
ROI_FILE = os.path.join(project_root, 'roi.json')
DEFAULT_ROI = [100, 200, 300, 100]

def load_roi():
    try:
        with open(ROI_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if (
            isinstance(data, list)
            and len(data) == 4
            and all(isinstance(n, int) and n >= 0 for n in data)
        ):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return DEFAULT_ROI.copy()

def save_roi(roi):
    try:
        with open(ROI_FILE, 'w', encoding='utf-8') as file:
            json.dump(roi, file)
    except OSError as error:
        print(f"Failed to save ROI: {error}")

ROI = load_roi()
CAMERA_INDEX = 0
OCR_LANGUAGE = "eng"
USE_7SEGMENT_OCR = False
last_text = ""
last_text_time = 0
text_display_duration = 3
AUTO_SCAN_ENABLED = False
AUTO_SCAN_INTERVAL = 5
last_scan_time = 0

roi_selection_mode = False
selecting_roi = False
roi_start = (0, 0)
roi_end = (0, 0)

def preprocess_image(roi_frame):
    gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
    if USE_7SEGMENT_OCR:
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        return closed
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh


def ocr_7segment(frame):
    """Preprocess and run OCR optimized for seven-segment digits."""
    processed = preprocess_image(frame)
    config = (
        f"--psm 6 -c tessedit_char_whitelist=0123456789 "
        f"--tessdata-dir \"{tessdata_dir}\" digits"
    )
    return pytesseract.image_to_string(
        processed,
        config=config,
        lang=OCR_LANGUAGE,
    ).strip()

def mouse_callback(event, x, y, flags, param):
    global selecting_roi, roi_start, roi_end, ROI, roi_selection_mode

    if not roi_selection_mode:
        return 
    
    if event == cv2.EVENT_LBUTTONDOWN:
        selecting_roi = True
        roi_start = (x, y)
        roi_end = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and selecting_roi:
        roi_end = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        selecting_roi = False
        roi_end = (x, y)
        x1, y1 = roi_start
        x2, y2 = roi_end
        x_new, y_new = min(x1, x2), min(y1, y2)
        w_new, h_new = abs(x2 - x1), abs(y2 - y1)
        if w_new > 0 and h_new > 0:
            ROI = [x_new, y_new, w_new, h_new]
            print(f"New ROI set to: {ROI}")
            save_roi(ROI)
        roi_selection_mode = False

def scan(frame):
    x, y, w, h = ROI
    roi_frame = frame[y:y + h, x:x + w]
    if USE_7SEGMENT_OCR:
        return ocr_7segment(roi_frame)
    processed = preprocess_image(roi_frame)
    return pytesseract.image_to_string(
        processed,
        config="--psm 6",
        lang=OCR_LANGUAGE,
    ).strip()

def main():
    global last_text, last_text_time, ROI, roi_selection_mode, last_scan_time

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    last_scan_time = time.time()

    cv2.namedWindow('Webcam Feed with ROI')
    cv2.setMouseCallback('Webcam Feed with ROI', mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to grab frame")
            continue

        display_frame = frame.copy()
        x, y, w, h = ROI
        if x + w <= frame.shape[1] and y + h <= frame.shape[0]:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if last_text and (time.time() - last_text_time <= text_display_duration):
                cv2.putText(display_frame,
                            f"Detected: {last_text}",
                            (11, 31),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 0),
                            3,
                            cv2.LINE_AA)
                cv2.putText(display_frame,
                            f"Detected: {last_text}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA)

        if roi_selection_mode and selecting_roi:
            cv2.rectangle(display_frame, roi_start, roi_end, (255, 0, 0), 2)

        if AUTO_SCAN_ENABLED:
            time_left = int(max(0, AUTO_SCAN_INTERVAL - (time.time() - last_scan_time)))
            cv2.putText(display_frame,
                        f"Next scan in: {time_left}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA)
            if time_left == 0:
                text = scan(frame)
                print("Detected text:", text)
                last_text = text
                last_text_time = time.time()
                last_scan_time = last_text_time

        cv2.imshow('Webcam Feed with ROI', display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            text = scan(frame)
            print("Detected text:", text)
            last_text = text
            last_text_time = time.time()
            last_scan_time = last_text_time
        elif key == ord('r'):
            print("ROI selection mode activated. Click and drag to set new ROI.")
            roi_selection_mode = True
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
