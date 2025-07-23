# ML_PictureTake

**WARNING: This script is intended to be used ONLY on a Raspberry Pi 5. Do NOT attempt to run it on any other device or platform.**

## Description
This project contains a script designed specifically for the Raspberry Pi 5. It may utilize hardware features, drivers, or optimizations unique to this device. Running it elsewhere may result in errors, hardware incompatibility, or unexpected behavior.

## Usage
- Ensure you are using a Raspberry Pi 5.
- Follow any additional setup instructions provided in the code or accompanying documentation.

## Installation

1. **Ensure you are using a Raspberry Pi 5 running Raspberry Pi OS.**
2. Install Python 3 and pip if not already installed.
3. Install required dependencies:
   ```bash
   pip install flask opencv-python picamera2
   ```
   You may also need to enable the camera interface via `raspi-config` and ensure all system dependencies for `picamera2` and `opencv-python` are installed.

## Running the App

1. Connect the Raspberry Pi Camera Module to your Raspberry Pi 5.
2. In the project directory, start the Flask server:
   ```bash
   python3 app.py
   ```
3. On your Raspberry Pi, open a web browser and go to:
   ```
   http://localhost:5000
   ```
   Or, from another device on the same network, use the Pi's IP address:
   ```
   http://<raspberry-pi-ip>:5000
   ```

## Using the Web Interface

- **Start Camera:** Click the "Start Camera" button to begin the live video stream.
- **Stop Camera:** Click the "Stop Camera" button to stop the video stream and release the camera.
- **Capture 1000 Photos:** Click the "Capture 1000 Photos" button to automatically capture 1000 images, one per second. The number of photos captured will be displayed on the page. Images are saved in the `static/captured_images` directory.
- **Kill Server:** Click the "Kill Server" button to safely shut down the Flask server.

## Notes
- Make sure the camera is properly connected and enabled.
- All images will be saved in the `static/captured_images` folder.
- Only use this app on a Raspberry Pi 5. Running it elsewhere is unsupported and may cause errors.

## Disclaimer
The authors are not responsible for any issues arising from running this script on unsupported hardware.
