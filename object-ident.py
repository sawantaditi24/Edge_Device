import cv2
import os
import time
import numpy as np
from picamera2 import Picamera2

# Load class names
classNames = []
classFile = "/home/aditi/Object_Detection_Files/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

# Load model configuration and weights
configPath = "/home/aditi/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/aditi/Object_Detection_Files/frozen_inference_graph.pb"
# Initialize the object detection model
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Function to detect objects
def getObjects(img, thres, nms, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    objectNames = set()
    objectCount = {}  # To store the count of each object
    if len(classIds) != 0:
        for classId, box in zip(classIds.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects or not objects:
                objectNames.add(className)
                # Count the objects
                if className not in objectCount:
                    objectCount[className] = 1
                else:
                    objectCount[className] += 1
                # Draw a green bounding box if object is detected
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(
                    img, className.upper(), (box[0], box[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                )
    return objectNames, objectCount, img  # Return object count along with names

def main():
    output_dir = "/home/aditi/Object_Detection_Files/outputs"
    os.makedirs(output_dir, exist_ok=True)  # Create output directory

    # Clean up the output directory
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    camera = Picamera2()
    config = camera.create_still_configuration()
    camera.configure(config)
    camera.start()

    objects_to_detect = ["cup"]

    # Capture reference objects during initialization
    def capture_reference_objects(camera, net, classes, capture_duration=10, min_detection_frames=15):
        detection_count = {}
        start_time = time.time()

        while time.time() - start_time < capture_duration:
            frame = camera.capture_array()
            classIds, _, _ = net.detect(frame)
            for classId in np.array(classIds).flatten():
                className = classes[classId - 1]
                if className not in detection_count:
                    detection_count[className] = 0
                detection_count[className] += 1

        # Filter objects based on minimum detection threshold
        reference_objects = {
            obj for obj, count in detection_count.items()
            if count >= min_detection_frames
        }

        if not reference_objects:
            print("Error: No objects detected consistently in reference phase.")
            return set()

        print(f"Reference Objects: {reference_objects}")
        return reference_objects

    # Initialize reference objects
    referenceObjects = capture_reference_objects(camera, net, classNames, capture_duration=10, min_detection_frames=15)

    if not referenceObjects:
        print("Reference initialization failed. Exiting.")
        camera.stop()
        return

    # Track missing objects and process real-time detection
    objectMissingSince = {}  # Track when each object first goes missing
    try:
        while True:
            frame = camera.capture_array()
            currentObjects, objectCount, annotatedFrame = getObjects(frame, 0.45, 0.2, objects=objects_to_detect)
            print(f"Detected objects in current frame: {currentObjects}")
            print(f"Reference objects: {referenceObjects}")

            # Check for missing objects
            for obj in objects_to_detect:
                if obj in referenceObjects:
                    if obj in currentObjects:
                        # Object is present, reset the missing timer
                        if objectMissingSince.get(obj) is not None:
                            print(f"{obj.capitalize()} reappeared in the frame.")
                        objectMissingSince[obj] = None
                        cv2.putText(
                            annotatedFrame, f"{obj.capitalize()} is present!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3
                        )
                        
                        # Save frame for object present
                        output_file = os.path.join(output_dir, f"present_{obj}_frame_{int(time.time())}.jpg")
                        cv2.imwrite(output_file, annotatedFrame)
                        print(f"Saved frame to {output_file}")
                    else:
                        # Object is missing
                        if objectMissingSince.get(obj) is None:
                            objectMissingSince[obj] = time.time()
                        elif time.time() - objectMissingSince[obj] > 5:
                            # Object has been missing for over 5 seconds
                            cv2.putText(
                                annotatedFrame, f"{obj.capitalize()} is missing!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3
                            )
                            print(f"The {obj} is now missing from the scene for 5 seconds.")

                            output_file = os.path.join(output_dir, f"missing_{obj}_frame_{int(time.time())}.jpg")
                            cv2.imwrite(output_file, annotatedFrame)
                            print(f"Saved frame to {output_file}")
                else:
                    print(f"No recent detections for {obj.capitalize()}.")

            # Display the count of detected objects
            for obj, count in objectCount.items():
                cv2.putText(
                    annotatedFrame, f"{obj}: {count}", (50, 100 + list(objectCount.keys()).index(obj) * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
                 )

            # Show the annotated frame
            cv2.imshow("Output", annotatedFrame)
            if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'Esc' key
                break
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    main()
