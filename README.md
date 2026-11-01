# SMAP — Smart Media Adaptive Processor

SMAP is a desktop application for processing and compressing video and image media. It combines a Qt interface with FFmpeg-based media processing.

## Features
- Video compression with configurable output parameters
- File selection and drag-and-drop workflow
- User-selected output directory
- Modular separation between processing logic and GUI
- Background processing to keep the interface responsive

## Tech stack
- Python 3.10+
- PySide6
- FFmpeg / ffprobe

## Setup
1. Clone the repository and enter its directory.
2. Create a virtual environment.
3. Install dependencies:
   ```bash
   python -m venv .venv
   # Windows
   .venv\\Scripts\\activate
   # macOS/Linux
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Install FFmpeg and ffprobe. Ensure both are available on your system PATH or configure paths according to the application.
5. Run `python main.py`.

## Project structure
- `core/`: media processing logic
- `gui/`: Qt interface
- `assets/`: application assets
- `main.py`: application entry point

## Notes
The repository does not distribute FFmpeg binaries. Verify FFmpeg installation and supported codecs on your system before processing media.

## Author
Gusty Faqikh
