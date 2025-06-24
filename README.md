# OCR Webcam Reader

A Python project that uses a USB webcam and Tesseract OCR to detect and read text from a defined region of the screen.

## Features

- Live webcam feed with overlay
- OCR triggered by spacebar
- Dynamic ROI selection with mouse
- On-screen display of detected text
- Auto-fade of text after 3 seconds

## Usage

### Controls
- `r` – Enter ROI selection mode (click and drag to select)
- `spacebar` – Perform OCR on selected ROI
- `q` – Quit the application

### Requirements

- Python 3.7+
- OpenCV
- Pytesseract
- Tesseract OCR (Included)

## Tesseract OCR Included

This project includes a portable version of Tesseract OCR (Windows only) under `Tesseract-OCR/`. No system installation is required.

### Setup

```bash
pip install opencv-python pytesseract
