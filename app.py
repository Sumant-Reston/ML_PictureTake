from flask import Flask, Response, stream_with_context, jsonify, send_file, request, g
from flask_cors import CORS
from picamera2 import Picamera2
import cv2
import time
import os
import signal
from datetime import datetime
import io
import zipfile
import csv
import threading


# ==============================================================================
# CAMERA MANAGER
# ==============================================================================

class CameraManager:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()
        self.is_active = False

    def start(self, config=None):
        with self.lock:
            if not self.is_active:
                print("Starting camera...")
                self.camera = Picamera2()
                if config:
                    self.camera.configure(self.camera.create_preview_configuration(**config))
                else:
                    self.camera.configure(self.camera.create_preview_configuration())
                self.camera.start()
                self.is_active = True
                time.sleep(1) # Allow camera to warm up
                print("Camera started.")
                return True
        return False

    def stop(self):
        with self.lock:
            if self.is_active:
                print("Stopping camera...")
                self.camera.stop()
                self.camera.close()
                self.is_active = False
                self.camera = None
                print("Camera stopped.")
                return True
        return False

    def get_frame(self):
        with self.lock:
            if self.is_active:
                return self.camera.capture_array()
        return None

    def capture_file(self, filename):
        with self.lock:
            if self.is_active:
                self.camera.capture_file(filename)


# ==============================================================================
# FLASK APP SETUP
# ==============================================================================

app = Flask(__name__)
CORS(app)

# --- Globals ---
camera_manager = CameraManager()

# ==============================================================================
# VIDEO STREAMING & BASIC CAMERA CONTROL
# ==============================================================================

def generate_frames():
    """Generator for the simple video feed."""
    camera_manager.start()   
    while True:
        frame = camera_manager.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            # If camera is off, stop sending frames
            print("Camera is off. Stopping video stream.")
            break
        time.sleep(0.03) # ~30fps

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Flask server is running."})

@app.route('/start_camera')
def start_camera():
    camera_manager.start()
    return "Camera started"

@app.route('/stop_camera')
def stop_camera():
    camera_manager.stop()
    return "Camera stopped"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ==============================================================================
# IMAGE CAPTURE
# ==============================================================================

@app.route('/capture_photos')
def capture_photos():
    count = request.args.get('count', default=10, type=int)
    def generate():
        save_path = os.path.join("static", "captured_images")
        os.makedirs(save_path, exist_ok=True)

        # Ensure camera is on for this session
        camera_manager.start()

        for i in range(count):
            frame = camera_manager.get_frame()
            if frame is None:
                print("Capture stopped because camera was turned off.")
                break
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_path, f"image_{timestamp}_{i}.jpg")
            camera_manager.capture_file(filename)
            yield f"data: {i + 1}\n\n"
            time.sleep(1)

        yield "event: done\ndata: Capture complete\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')



# ==============================================================================
# FILE DOWNLOAD & DELETE
# ==============================================================================

@app.route('/download_breakdowns')
def download_breakdowns():
    path = os.path.join("static", "pallet_breakdowns.csv")
    if not os.path.isfile(path):
        return jsonify({"error": "No breakdowns recorded yet."}), 404
    return send_file(path, as_attachment=True)

@app.route('/download_photos')
def download_photos():
    path = os.path.join("static", "captured_images")
    if not os.path.isdir(path) or not os.listdir(path):
        return jsonify({"error": "No photos found to download."}), 404

    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                z.write(file_path, os.path.basename(file_path))
    data.seek(0)

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        download_name='captured_photos.zip'
    )

@app.route('/delete_photos', methods=['POST'])
def delete_photos():
    path = os.path.join("static", "captured_images")
    if not os.path.isdir(path):
        return jsonify({"message": "Directory not found, nothing to delete."}), 200

    try:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        return jsonify({"message": "All photos have been deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500





# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)
