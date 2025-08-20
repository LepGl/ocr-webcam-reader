# OCR Webcam Reader

A Python project that uses a USB webcam and Tesseract OCR to detect and read text from a defined region of the screen.

## Features

- Live webcam feed with overlay
- OCR triggered by spacebar
- Dynamic ROI selection with mouse
- On-screen display of detected text
- Auto-fade of text after 3 seconds
- ROI persists between runs via roi.json

## Usage

```bash
python main.py
```

By default, camera index 0 is used. Update `CAMERA_INDEX` in `main.py` to select a different camera. Set `OCR_LANGUAGE` to change Tesseract's language (default: `eng`).

### Language Codes

The project bundles the following language data files under `Tesseract-OCR/tessdata/`. Use the appropriate code when configuring `OCR_LANGUAGE`:

```
afr amh ara asm aze aze_cyrl bel ben bod bos bre bul cat ceb ces chi_sim
chi_sim_vert chi_tra chi_tra_vert chr cos cym dan deu deu_latf div dzo ell
eng enm epo equ est eus fao fas fil fin fra frm fry gla gle glg grc guj
hat heb hin hrv hun hye iku ind isl ita ita_old jav jpn jpn_vert kan kat
kat_old kaz khm kir kmr kor lao lat lav lit ltz mal mar mkd mlt mon mri msa
mya nep nld nor oci ori osd pan pol por pus que ron rus san sin slk slv snd
spa spa_old sqi srp srp_latn sun swa swe syr tam tat tel tgk tha tir ton
tur uig ukr urd uzb uzb_cyrl vie yid yor
```

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
```
