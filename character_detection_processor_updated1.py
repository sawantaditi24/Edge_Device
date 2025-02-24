import time
import cv2
import os
from picamera2 import Picamera2
import subprocess
import pytesseract
import numpy as np

class CharacterRecognitionProcessor:
    def __init__(self, output_dir="/home/aditi/Character_Recognition_Files/outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.stop_other_camera_processes()

        # Initialize camera
        self.camera = Picamera2()
        self.camera_config = self.camera.create_preview_configuration()

    def stop_other_camera_processes(self):
        subprocess.run(['sudo', 'killall', '-9', 'libcamera-hello'], check=False)

    def preprocess_image(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        return dilated

    def detect_text(self):
        try:
            self.camera.stop()
            self.camera.configure(self.camera_config)
            self.camera.start()

            frame = self.camera.capture_array()
            if frame is None:
                print("Captured frame is None")
                return []

            # Preprocess the image
            processed_image = self.preprocess_image(frame)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_image)
            detected_text = text.strip()

            if detected_text:
                # Draw text detection results on the frame
                d = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
                n_boxes = len(d['text'])
                
                for i in range(n_boxes):
                    if int(d['conf'][i]) > 60:  # Filter by confidence
                        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, d['text'][i], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Save the annotated image
                timestamp = int(time.time())
                output_file = os.path.join(self.output_dir, f'text_detected_{timestamp}.jpg')
                cv2.imwrite(output_file, frame)
                print(f"Detected text: {detected_text}")

            return detected_text

        except Exception as e:
            print(f"Detection error: {e}")
            return []
        finally:
            self.camera.stop()

def main():
    processor = CharacterRecognitionProcessor()
    while True:
        processor.detect_text()
        time.sleep(5)

if __name__ == "__main__":
    main()
