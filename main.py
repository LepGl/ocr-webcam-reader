import cv2
import pytesseract
import time

# Optional: Set path to Tesseract if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Default ROI (x, y, w, h)
ROI = [100, 200, 300, 100]

# On-screen text overlay
last_text = ""
last_text_time = 0
text_display_duration = 3  # seconds

# ROI selection state
roi_selection_mode = False
selecting_roi = False
roi_start = (0, 0)
roi_end = (0, 0)

def preprocess_image(roi_frame):
    gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def mouse_callback(event, x, y, flags, param):
    global selecting_roi, roi_start, roi_end, ROI, roi_selection_mode

    if not roi_selection_mode:
        return  # Ignore mouse actions unless in ROI selection mode

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
        roi_selection_mode = False  # Exit ROI mode

def main():
    global last_text, last_text_time, ROI, roi_selection_mode

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    cv2.namedWindow('Webcam Feed with ROI')
    cv2.setMouseCallback('Webcam Feed with ROI', mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to grab frame")
            continue

        display_frame = frame.copy()

        # Draw current ROI
        x, y, w, h = ROI
        if x + w <= frame.shape[1] and y + h <= frame.shape[0]:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Show OCR text if still within time window
            if last_text and (time.time() - last_text_time <= text_display_duration):
                cv2.putText(display_frame,
                            f"Detected: {last_text}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA)

        # Draw temporary ROI during selection
        if roi_selection_mode and selecting_roi:
            cv2.rectangle(display_frame, roi_start, roi_end, (255, 0, 0), 2)

        cv2.imshow('Webcam Feed with ROI', display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  # Spacebar = OCR
            roi_frame = frame[y:y+h, x:x+w]
            processed = preprocess_image(roi_frame)
            text = pytesseract.image_to_string(processed, config='--psm 6').strip()
            print("Detected text:", text)
            last_text = text
            last_text_time = time.time()

        elif key == ord('r'):  # Enable ROI drawing mode
            print("ROI selection mode activated. Click and drag to set new ROI.")
            roi_selection_mode = True

        elif key == ord('q'):  # Quit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
