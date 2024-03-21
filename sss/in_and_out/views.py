from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators import gzip
import cv2
import numpy as np
from django.shortcuts import render

# Load YOLO
net = cv2.dnn.readNet("static\in_and_out\yolov3-tiny.weights", 
                      "static\in_and_out\yolov3-tiny.cfg")
classes = []
with open("static\in_and_out\coco.names", "r") as f:
    classes = [line.strip() for line in f]

layer_names = net.getUnconnectedOutLayersNames()


left_count = 0
right_count = 0

# Dictionary to store information about tracked persons
tracked_persons = {}

# Counter to assign unique IDs to individuals
person_id_counter = 1


# Function to process frames and perform object detection
def process_frame(frame):
    global person_id_counter, left_count, right_count
    print("Processing frame")
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(layer_names)
    
    # Add your object detection logic here
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.6 and classes[class_id] == 'person':
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.1)

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]

            # Check if the person is moving towards the left or right
            if x < width // 2:
                side = "IN"
            else:
                side = "OUT"

            # Check if this person is already tracked
            person_id = -1
            for pid, (prev_x, prev_y, _) in tracked_persons.items():
                distance = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                if distance < 50:  # Adjust the threshold based on your scenario
                    person_id = pid
                    break

            if person_id == -1:
                # New person, assign a unique ID
                person_id = person_id_counter
                person_id_counter += 1
                tracked_persons[person_id] = (x, y, side)
                # Increment count based on side
                if side == "IN":
                    left_count += 1
                else:
                    right_count += 1

            # Update the position of the tracked person
            tracked_persons[person_id] = (x, y, side)

            color = (0, 255, 0)  # Green color for the bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f'{label} {confidence:.2f} {side}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.putText(frame, f'IN: {left_count}  OUT: {right_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Convert frame to JPEG format
    _, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

# Generator function to stream video frames
def video_feed_generator():
    cap = cv2.VideoCapture(0)
    while True:
        print(cap.read())
        ret, frame = cap.read()
        cv2.imshow("Object Detection", frame)
        print("Reading frame")
        if not ret:
            break
        processed_frame = process_frame(frame)
        cv2.imshow("Object Detection", frame)

        print("Yielding frame")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n\r\n')

    cap.release()

# Decorator to compress the video feed
@gzip.gzip_page
def in_and_out_feed(request):
    #print("Video feed request")
    return StreamingHttpResponse(video_feed_generator(), content_type='multipart/x-mixed-replace; boundary=frame')

def in_and_out(request):
    return render(request, 'in_and_out_count/in_and_out.html')