# Edge Device - Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Installation & Setup](#installation--setup)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Development Guidelines](#development-guidelines)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

The Edge Device project is a comprehensive computer vision solution designed for Raspberry Pi, providing real-time object detection, face recognition, and character recognition capabilities. The system leverages edge computing to process visual data locally, minimizing latency and enabling offline operation.

### Key Features
- **Multi-Modal Detection**: Supports object detection, face recognition, and OCR
- **Real-Time Processing**: Live camera feed analysis with low latency
- **Flexible Detection Modes**: Both general and specific object detection
- **Web-Based Interface**: React frontend for easy interaction
- **RESTful API**: Flask-based backend for seamless integration

### Technology Stack
- **Backend**: Python 3.x, Flask, OpenCV, face_recognition, pytesseract
- **Frontend**: React.js, React Router
- **Hardware**: Raspberry Pi with PiCamera2
- **ML Models**: SSD MobileNet v3, face_recognition library, Tesseract OCR

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend Layer                      │
│  (React.js - User Interface)                           │
│  - HomePage.js                                         │
│  - DetectionStatus-UI.js                               │
│  - FaceRecognition.js                                  │
│  - FeatureRecognition.js                               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────┴────────────────────────────────────┐
│                     Backend Layer                       │
│  (Flask - API Server)                                   │
│  - flask-backend.py                                     │
│  - face_rec_server.py                                   │
│  - char_rec_server_updated_1.py                         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  Processing Layer                       │
│  - face_detection_processor.py                          │
│  - character_detection_processor_updated1.py            │
│  - object-ident.py                                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                   Hardware Layer                        │
│  - Raspberry Pi + PiCamera2                            │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Camera Capture**: PiCamera2 captures frames from the camera module
2. **Processing**: Captured frames are processed by specialized processors
3. **Detection**: ML models analyze frames for objects/faces/text
4. **Storage**: Annotated images saved to output directories
5. **API Response**: Flask server serves detection results and images
6. **UI Display**: React frontend displays results to users

---

## Components

### 1. Object Detection Module

**File**: `object-ident.py`

#### Purpose
Detects and tracks objects in real-time using SSD MobileNet v3 model trained on COCO dataset.

#### Features
- **Reference Object Capture**: Initializes by capturing reference objects for 10 seconds
- **Object Tracking**: Monitors specific objects (e.g., "cup") and alerts when missing
- **Dual Detection Modes**:
  - General mode: Detects any object in COCO dataset
  - Specific mode: Detects only user-specified objects
- **Missing Object Detection**: Alerts when tracked objects are missing for >5 seconds
- **Object Counting**: Counts instances of each detected object type

#### Key Functions
```python
getObjects(img, thres, nms, objects=[])
```
- **Parameters**:
  - `img`: Input image frame
  - `thres`: Confidence threshold (default: 0.45)
  - `nms`: Non-maximum suppression threshold (default: 0.2)
  - `objects`: List of specific objects to detect (empty = all objects)
- **Returns**: `(objectNames, objectCount, annotatedImage)`

```python
capture_reference_objects(camera, net, classes, capture_duration=10, min_detection_frames=15)
```
- **Purpose**: Captures baseline objects present in scene during initialization
- **Returns**: Set of reference objects

#### Configuration
- **Model Files**:
  - Class names: `/home/aditi/Object_Detection_Files/coco.names`
  - Config: `/home/aditi/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt`
  - Weights: `/home/aditi/Object_Detection_Files/frozen_inference_graph.pb`
- **Output Directory**: `/home/aditi/Object_Detection_Files/outputs`
- **Input Size**: 320x320 pixels
- **Detection Thresholds**:
  - Confidence: 0.45
  - NMS: 0.2

---

### 2. Face Recognition Module

**File**: `face_detection_processor.py`

#### Purpose
Identifies known faces in camera feed using facial recognition algorithms.

#### Class: `FaceDetectionProcessor`

##### Initialization
```python
FaceDetectionProcessor(known_faces_dir="known_face", output_dir="/home/aditi/Face_Recognition_Files/outputs")
```
- Loads known face encodings from directory
- Initializes PiCamera2
- Creates output directory for detected faces

##### Key Methods

**`load_known_faces(directory)`**
- Loads face encodings from image files
- Supports JPG, JPEG, PNG formats
- Stores face encodings and names

**`detect_faces()`**
- Captures frame from camera
- Detects face locations using HOG algorithm
- Compares detected faces with known encodings
- Returns list of detected names
- Saves annotated images with bounding boxes

##### Processing Pipeline
1. Capture frame from camera
2. Resize frame to 1/4 size for faster processing
3. Convert BGR to RGB color space
4. Detect face locations
5. Generate face encodings
6. Compare with known faces
7. Draw bounding boxes and labels
8. Save annotated image if faces detected

##### Configuration
- **Frame Scale**: 0.25 (1/4 original size for processing)
- **Detection Interval**: 5 seconds
- **Output Format**: JPG with timestamp

---

### 3. Character Recognition Module

**File**: `character_detection_processor_updated1.py`

#### Purpose
Performs Optical Character Recognition (OCR) on camera feed using Tesseract.

#### Class: `CharacterRecognitionProcessor`

##### Initialization
```python
CharacterRecognitionProcessor(output_dir="/home/aditi/Character_Recognition_Files/outputs")
```

##### Key Methods

**`preprocess_image(image)`**
- Converts to grayscale
- Applies OTSU thresholding
- Performs dilation to connect text components
- Returns preprocessed image optimized for OCR

**`detect_text()`**
- Captures frame from camera
- Preprocesses image
- Performs OCR using pytesseract
- Draws bounding boxes around detected text
- Returns detected text string

##### OCR Configuration
- **Confidence Threshold**: 60
- **Preprocessing**:
  - Grayscale conversion
  - Binary thresholding (OTSU method)
  - Morphological dilation (3x3 kernel)
- **Detection Interval**: 5 seconds

---

### 4. Backend API Server

**File**: `flask-backend.py`

#### Purpose
Provides RESTful API for accessing detection results and images.

#### Endpoints

##### `GET /status`
Returns current detection status and latest image.

**Query Parameters**:
- `object` (optional): Object type to detect (default: "cup")

**Response**:
```json
{
  "message": "Object is present" | "Object is missing",
  "imageUrl": "http://192.168.4.182:5000/image/<filename>",
  "count": 0
}
```

**Logic**:
- Finds latest image in output directory
- Checks if image is fresh (< 60 seconds old)
- Returns detection status and image URL

##### `GET /image/<filename>`
Serves images from output directory.

**Parameters**:
- `filename`: Name of image file

**Returns**: Image file

#### Configuration
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5000
- **CORS**: Enabled for all origins
- **Freshness Threshold**: 60 seconds

---

### 5. Frontend Application

**File**: `App.js`

#### Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | HomePage | Main landing page |
| `/detection-status` | DetectionStatus | Object detection interface |
| `/face-recognition` | FaceRecognition | Face recognition interface |
| `/feature-recognition` | FeatureRecognition | Character recognition interface |

#### Components

**HomePage.js**
- Landing page with navigation to different detection modes

**DetectionStatus-UI.js**
- Displays real-time object detection results
- Shows annotated images
- Object count display
- Missing object alerts

**FaceRecognition.js**
- Face recognition interface
- Displays detected faces with names

**FeatureRecognition.js** (CharacterRecognitionUpdated1.js)
- Text recognition interface
- Displays detected text

---

## Installation & Setup

### Hardware Requirements
- Raspberry Pi (3B+ or later recommended)
- Raspberry Pi Camera Module (v2 or HQ)
- MicroSD card (16GB+ recommended)
- Power supply (5V 2.5A minimum)

### Software Prerequisites

#### System Packages
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-opencv
sudo apt-get install -y tesseract-ocr libtesseract-dev
sudo apt-get install -y libatlas-base-dev libhdf5-dev
```

#### Python Dependencies
```bash
pip3 install flask flask-cors
pip3 install picamera2
pip3 install opencv-python
pip3 install face-recognition
pip3 install pytesseract
pip3 install numpy
```

#### Frontend Dependencies
```bash
cd frontend
npm install react react-router-dom
npm install
```

### Model Files Setup

1. **Download COCO dataset files**:
   ```bash
   mkdir -p /home/aditi/Object_Detection_Files
   cd /home/aditi/Object_Detection_Files
   wget https://raw.githubusercontent.com/opencv/opencv/master/samples/data/dnn/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt
   wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v3_large_coco_2020_01_14.tar.gz
   tar -xvf ssd_mobilenet_v3_large_coco_2020_01_14.tar.gz
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
   ```

2. **Create known faces directory**:
   ```bash
   mkdir -p known_face
   # Add images of known faces (format: name.jpg)
   ```

3. **Create output directories**:
   ```bash
   mkdir -p /home/aditi/Object_Detection_Files/outputs
   mkdir -p /home/aditi/Face_Recognition_Files/outputs
   mkdir -p /home/aditi/Character_Recognition_Files/outputs
   ```

### Configuration

#### Update File Paths
Edit the following files to match your directory structure:
- `object-ident.py`: Update paths on lines 9, 14, 15, 47
- `face_detection_processor.py`: Update path on line 9
- `character_detection_processor_updated1.py`: Update path on line 10
- `flask-backend.py`: Update path on line 9

#### Network Configuration
Update IP addresses in:
- `flask-backend.py`: Lines 27, 56 (set to Raspberry Pi IP)
- Frontend API calls: Update to match backend IP

### Running the Application

#### Start Backend Servers

**Object Detection**:
```bash
python3 object-ident.py
```

**Face Recognition**:
```bash
python3 face_rec_server.py
```

**Character Recognition**:
```bash
python3 char_rec_server_updated_1.py
```

**Main API Server**:
```bash
python3 flask-backend.py
```

#### Start Frontend
```bash
cd frontend
npm start
```

Access the application at: `http://localhost:3000`

---

## API Reference

### Object Detection API

#### GET /status
Retrieves current object detection status.

**Request**:
```http
GET /status?object=cup HTTP/1.1
Host: 192.168.4.182:5000
```

**Response**:
```json
{
  "message": "Object is present",
  "imageUrl": "http://192.168.4.182:5000/image/present_cup_frame_1637012345.jpg",
  "count": 2
}
```

**Status Codes**:
- 200 OK: Successful request
- 500 Internal Server Error: Processing error

#### GET /image/:filename
Retrieves annotated detection image.

**Request**:
```http
GET /image/present_cup_frame_1637012345.jpg HTTP/1.1
Host: 192.168.4.182:5000
```

**Response**: Image file (JPEG)

---

## Configuration

### Environment Variables

Create `.env` file:
```bash
# Backend Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
FRESHNESS_THRESHOLD=60

# Directory Paths
OBJECT_DETECTION_DIR=/home/aditi/Object_Detection_Files
FACE_RECOGNITION_DIR=/home/aditi/Face_Recognition_Files
CHARACTER_RECOGNITION_DIR=/home/aditi/Character_Recognition_Files

# Model Configuration
CONFIDENCE_THRESHOLD=0.45
NMS_THRESHOLD=0.2
OCR_CONFIDENCE=60

# Camera Configuration
FRAME_SCALE=0.25
DETECTION_INTERVAL=5
```

### Detection Parameters

**Object Detection**:
- `CONFIDENCE_THRESHOLD`: Minimum confidence for object detection (0.0-1.0)
- `NMS_THRESHOLD`: Non-maximum suppression threshold (0.0-1.0)
- `REFERENCE_CAPTURE_DURATION`: Time to capture reference objects (seconds)
- `MIN_DETECTION_FRAMES`: Minimum frames to consider object as reference
- `MISSING_OBJECT_TIMEOUT`: Time before object considered missing (seconds)

**Face Recognition**:
- `FRAME_SCALE`: Scale factor for face detection (0.0-1.0)
- `DETECTION_INTERVAL`: Time between detections (seconds)

**Character Recognition**:
- `OCR_CONFIDENCE`: Minimum OCR confidence (0-100)
- `KERNEL_SIZE`: Morphological kernel size for preprocessing
- `DILATION_ITERATIONS`: Number of dilation iterations

---

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Add docstrings to all functions and classes
- Include type hints where applicable

### Adding New Detection Modes

1. **Create Processor Class**:
   ```python
   class NewDetectionProcessor:
       def __init__(self, output_dir):
           self.output_dir = output_dir
           self.camera = Picamera2()

       def detect(self):
           # Implementation
           pass
   ```

2. **Create Flask Server**:
   ```python
   from flask import Flask, jsonify
   from new_detection_processor import NewDetectionProcessor

   app = Flask(__name__)
   processor = NewDetectionProcessor()

   @app.route('/detect', methods=['GET'])
   def detect():
       results = processor.detect()
       return jsonify(results)
   ```

3. **Add Frontend Route**:
   ```javascript
   <Route path="/new-detection" element={<NewDetection />} />
   ```

### Testing

#### Unit Tests
```bash
python3 -m pytest tests/
```

#### Integration Tests
```bash
python3 -m pytest tests/integration/
```

#### Camera Tests
```bash
python3 tests/test_camera.py
```

### Performance Optimization

1. **Frame Rate**: Adjust detection interval based on use case
2. **Image Size**: Scale down frames for faster processing
3. **Model Selection**: Use lighter models for faster inference
4. **Parallel Processing**: Run multiple detection modes concurrently
5. **Caching**: Cache model weights in memory

---

## Troubleshooting

### Camera Issues

**Problem**: Camera not detected
```bash
# Check camera connection
vcgencmd get_camera

# Expected output: supported=1 detected=1
```

**Solution**:
- Enable camera interface: `sudo raspi-config` > Interface Options > Camera
- Reboot: `sudo reboot`

**Problem**: "Camera is already in use"
```bash
# Kill existing camera processes
sudo killall -9 libcamera-hello
```

### Model Loading Issues

**Problem**: Model files not found
- Verify file paths in configuration
- Check file permissions: `ls -l /home/aditi/Object_Detection_Files/`
- Re-download model files

**Problem**: Out of memory errors
- Reduce input size: `net.setInputSize(320, 320)` → `net.setInputSize(256, 256)`
- Increase swap space: `sudo dphys-swapfile swapoff && sudo nano /etc/dphys-swapfile`

### Network Issues

**Problem**: Cannot access API from frontend
- Check Flask server is running: `ps aux | grep flask`
- Verify firewall settings: `sudo ufw status`
- Test API manually: `curl http://192.168.4.182:5000/status`

**Problem**: CORS errors
- Ensure `flask-cors` is installed
- Verify CORS(app) is called in Flask app

### Performance Issues

**Problem**: Slow detection speed
- Reduce frame size
- Increase detection interval
- Use lighter model (MobileNet v2 instead of v3)
- Optimize image preprocessing

**Problem**: High CPU usage
- Limit frame rate
- Disable unnecessary detection modes
- Use hardware acceleration if available

### Face Recognition Issues

**Problem**: No faces detected
- Check lighting conditions
- Verify camera focus
- Increase frame scale: `fx=0.5, fy=0.5`
- Check known_face directory has valid images

**Problem**: Unknown faces not recognized
- Add more images to known_face directory
- Use multiple angles of the same person
- Ensure high-quality images (>200x200 pixels)

### OCR Issues

**Problem**: Text not detected
- Improve lighting
- Ensure text is in focus
- Adjust preprocessing parameters
- Check Tesseract installation: `tesseract --version`

**Problem**: Low accuracy
- Increase image resolution
- Adjust confidence threshold
- Use better preprocessing (denoising, contrast enhancement)

---

## Appendix

### File Structure
```
Edge_Device/
├── App.js                                    # React main app
├── CharacterRecognitionUpdated1.js          # Character recognition UI
├── DetectionStatus-UI.js                    # Object detection UI
├── FaceRecognition.py                       # Face recognition script
├── FeatureRecognition.js                    # Feature recognition UI
├── HomePage.js                              # Landing page
├── README.md                                # Project overview
├── back.py                                  # Backend utility
├── char_rec_server_updated_1.py            # Character recognition server
├── character_detection_processor_updated1.py # Character processor
├── face_detection_processor.py              # Face detection processor
├── face_rec_server.py                       # Face recognition server
├── face_recognition.js                      # Face recognition UI
├── flask-backend.py                         # Main Flask server
├── front.js                                 # Frontend utility
├── object-ident.py                          # Object detection script
└── styles.css                               # Application styles
```

### Supported Object Classes (COCO Dataset)
person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

### References
- [OpenCV Documentation](https://docs.opencv.org/)
- [Face Recognition Library](https://github.com/ageitgey/face_recognition)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [PiCamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)

### Version History
- v1.0.0: Initial release with object detection, face recognition, and OCR capabilities

---

**Last Updated**: November 2025
**Maintainer**: Edge Device Team
