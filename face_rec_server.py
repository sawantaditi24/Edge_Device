from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

# Directory where the backend saves detection results
OUTPUT_DIR = "/home/aditi/Face_Recognition_Files/outputs"

@app.route('/face-status', methods=['GET'])
def face_status():
    try:
        # Fetch files saved by the backend
        files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith('facedetected')]
        if not files:
            return jsonify({"message": "No faces detected", "imageUrl": "", "timestamp": None})

        # Find the latest detection result
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(OUTPUT_DIR, x)))
        latest_path = os.path.join(OUTPUT_DIR, latest_file)

        # Check if the detection was recent
        if time.time() - os.path.getctime(latest_path) < 5:
            return jsonify({
                "message": "Face detected!",
                "imageUrl": f"http://192.168.4.229:5000/face-image/{latest_file}",
                "timestamp": os.path.getctime(latest_path)
            })
        else:
            return jsonify({"message": "No recent detections", "imageUrl": "", "timestamp": None})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "imageUrl": "", "timestamp": None})

@app.route('/face-image/<filename>', methods=['GET'])
def face_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)


