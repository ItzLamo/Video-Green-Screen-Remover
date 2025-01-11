# Video Green Screen Remover

A simple Python application to remove a green screen from videos and replace it with a custom background using OpenCV and Tkinter.

---

## Features

- Remove green screen and replace it with an uploaded background image.
- Retain the original audio of the video.
- Easy-to-use graphical interface for video and background selection.
- Preview the processed video before saving.

---

## Requirements

- Python 3.x
- Libraries: `opencv-python`, `numpy`, `Pillow`, `moviepy`

### Installation
Install the required libraries:
```bash
pip install opencv-python numpy Pillow moviepy
```

---

## How to Use

1. Run the program:
   ```bash
   python green_screen_remover.py
   ```
2. Click "Upload Video" to select a video file (`.mp4`, `.avi`, `.mov`).
3. Click "Upload Picture" to select a background image (`.jpg`, `.jpeg`, `.png`).
4. View the preview of the processed video.
5. Click "Process and Save" to save the final video.

---

## Notes

- Works best with videos having a clear green screen.
- Supported video formats: `.mp4`, `.avi`, `.mov`.
- Supported background formats: `.jpg`, `.jpeg`, `.png`.

---

Enjoy creating videos! 🎥
