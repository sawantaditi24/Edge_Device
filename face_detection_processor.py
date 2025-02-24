import time
import cv2
import face_recognition
import os
from picamera2 import Picamera2
import subprocess

class FaceDetectionProcessor:
    def __init__(self, known_faces_dir="known_face", output_dir="/home/aditi/Face_Recognition_Files/outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.stop_other_camera_processes()
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces(known_faces_dir)

        # Initialize camera
        self.camera = Picamera2()
        self.camera_config = self.camera.create_preview_configuration()

    def stop_other_camera_processes(self):
        subprocess.run(['sudo', 'killall', '-9', 'libcamera-hello'], check=False)

    def load_known_faces(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(directory, filename)
                face_image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(face_image)
                if face_encoding:
                    self.known_face_encodings.append(face_encoding[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])

    def detect_faces(self):
        try:
            self.camera.stop()
            self.camera.configure(self.camera_config)
            self.camera.start()

            frame = self.camera.capture_array()
            if frame is None:
                print("Captured frame is None")
                return []

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
detected_names = []
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]

                detected_names.append(name)

                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a rectangle around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Label the face with the name
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)

            if detected_names:
                timestamp = int(time.time())
                output_file = os.path.join(self.output_dir, f'facedetected{timestamp}.jpg')
                cv2.imwrite(output_file, frame)
                print(f"Detected faces: {detected_names}")

            return detected_names
        except Exception as e:
            print(f"Detection error: {e}")
            return []
        finally:
            self.camera.stop()

def main():
    processor = FaceDetectionProcessor()
    print("Starting Face Detection...")
    while True:
        processor.detect_faces()
        
        time.sleep(5)

if __name__ == "__main__":
    main()
