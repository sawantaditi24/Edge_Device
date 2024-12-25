from flask_cors import CORS
from flask import Flask, jsonify, send_from_directory, request
import os
import time

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = "/home/aditi/Object_Detection_Files/outputs"
# Define a freshness threshold in seconds (e.g., 60 seconds)
FRESHNESS_THRESHOLD = 60



@app.route('/status', methods=['GET'])
def status():
    object_type = request.args.get('object', 'cup')
    print(f"Selected object for detection: {object_type}")

    # Get the latest image file
    latest_image = max(
        (os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)),
        key=os.path.getctime,
        default=None
    )

    default_image_url = "http://192.168.4.182:5000/image/default_image.jpg"  # Default image URL

    if latest_image:
        file_age = time.time() - os.path.getctime(latest_image)
        
        # Check for freshness
        if file_age < FRESHNESS_THRESHOLD:  # File is fresh
            # Here, we need to add logic to check the actual detection of the object
            detection_status = "Object is present"  # Default assumption

            # Here you will need to extract object count from the latest image
            # You can use object detection to get this count
            # For this, you will need to add logic to extract the object count from the image
            
            # Let's assume you have a function `get_object_count` that returns a count of detected objects
            # Update with actual logic from your object detection code
            objectCount = 0
            objectNames = set()
            try:
                # Load the image using OpenCV or another method
                image = cv2.imread(latest_image)
                _, objectCount, _ = getObjects(image, 0.45, 0.2, objects=[object_type])
            except Exception as e:
                print(f"Error processing the latest image: {e}")

            # If the object is not found, update the status
            if object_type not in objectNames:  
                detection_status = f"{object_type.capitalize()} is missing"
            
            image_url = f"http://192.168.4.182:5000/image/{os.path.basename(latest_image)}"
            return jsonify({
                "message": detection_status,
                "imageUrl": image_url,
                "count": objectCount  # Add the object count here
            })

        else:
            return jsonify({
                "message": "Object is present",
                "imageUrl": default_image_url,
                "count": 0  # Default count if the image is not fresh
            })

    return jsonify({
        "message": "Object is Present",
        "imageUrl": default_image_url,
        "count": 0  # Default count when no image is available
    })
    
@app.route('/image/<filename>', methods=['GET'])
def image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
