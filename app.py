from flask import Flask, render_template, Response, stream_with_context
from picamera2 import Picamera2
import cv2
import time
import os
import signal
from datetime import datetime

app = Flask(__name__)
camera = None

def generate_frames():
    global camera
    while True:
        if camera:
            frame = camera.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_camera')
def start_camera():
    global camera
    if camera is None:
        camera = Picamera2()
        camera.configure(camera.create_preview_configuration())
        camera.start()
        time.sleep(1)
    return "Camera started"

@app.route('/stop_camera')
def stop_camera():
    global camera
    if camera:
        camera.stop()
        camera.close()
        camera = None
    return "Camera stopped"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_photos')
def capture_photos():
    def generate():
        global camera
        save_path = os.path.join("static", "captured_images")
        os.makedirs(save_path, exist_ok=True)

        if camera is None:
            camera = Picamera2()
            camera.configure(camera.create_preview_configuration())
            camera.start()
            time.sleep(1)

        for i in range(1000):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_path, f"image_{timestamp}_{i}.jpg")
            camera.capture_file(filename)
            yield f"data: {i + 1}\n\n"
            time.sleep(1)

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/shutdown')
def shutdown():
    global camera
    if camera:
        camera.stop()
        camera.close()
        camera = None
    os.kill(os.getpid(), signal.SIGTERM)
    return "Shutting down..."
    
if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000)
