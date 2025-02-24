                                                                                   
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import os
import time
from picamera2 import Picamera2
from datetime import datetime

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = "/home/aditi/Object_Detection_Files/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Constants for motion detection
MOTION_THRESHOLD = 25
MOTION_MIN_AREA = 500

class SceneMonitor:
    def __init__(self):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_still_configuration())
        self.camera.start()
        self.previous_frame = None
        self.change_history = []
        self.last_save_time = 0
        self.MIN_SAVE_INTERVAL = 2  # Minimum seconds between saved frames

    def detect_motion(self, frame):
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Initialize previous frame if None
        if self.previous_frame is None:
            self.previous_frame = gray
            return False, []

        # Compute difference between current and previous frame
        frame_delta = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_delta, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours of changed regions
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Update previous frame
        self.previous_frame = gray

        # Check for significant motion
        significant_changes = []
        for contour in contours:
            if cv2.contourArea(contour) < MOTION_MIN_AREA:
                continue
                
            (x, y, w, h) = cv2.boundingRect(contour)
            significant_changes.append((x, y, w, h))

        return len(significant_changes) > 0, significant_changes

    def analyze_scene(self):
        frame = self.camera.capture_array()
        current_time = time.time()
        
        # Detect motion
        motion_detected, motion_regions = self.detect_motion(frame)
        
        status_message = "Monitoring scene..."
        changes = []

        if motion_detected:
            status_message = "Change detected in scene!"
            changes.append(f"Motion detected in {len(motion_regions)} regions")

            # Draw rectangles around motion regions
            for (x, y, w, h) in motion_regions:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Save frame if enough time has passed since last save
            if current_time - self.last_save_time >= self.MIN_SAVE_INTERVAL:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(OUTPUT_DIR, f"change_detected_{timestamp}.jpg")
                cv2.imwrite(output_file, frame)
                self.last_save_time = current_time
                latest_image = output_file
            else:
                # Get the most recent image from the directory
                image_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith('change_detected_')]
                latest_image = max([os.path.join(OUTPUT_DIR, f) for f in image_files], key=os.path.getctime) if image_files else None

        self.change_history = (changes + self.change_history)[:5]  # Keep last 5 changes

        return {
            "status": status_message,
            "changes": self.change_history,
            "imageUrl": f"http://192.168.4.229:5000/image/{os.path.basename(latest_image)}" if motion_detected and latest_image else None
        }
scene_monitor = SceneMonitor()

@app.route('/scene-status')
def get_scene_status():
    return jsonify(scene_monitor.analyze_scene())

@app.route('/image/<filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
