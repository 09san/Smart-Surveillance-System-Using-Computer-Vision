from django.http import StreamingHttpResponse, HttpResponseServerError
import cv2
import numpy as np

def object_detection(request):

    print("Object Detection")
    # Path to the files

    weights_path = "C:/Users/jayan/OneDrive/Documents/4th Year Project/sss/static/Inout_Detection/yolov3-tiny.weights"
    config_path = "C:/Users/jayan/OneDrive/Documents/4th Year Project/sss/static/Inout_Detection/yolov3-tiny.cfg"
    coco_names_path = "C:/Users/jayan/OneDrive/Documents/4th Year Project/sss/static/Inout_Detection/coco.names"

    net = cv2.dnn.readNet(weights_path, config_path)
    classes = []
    with open(coco_names_path, "r") as f:
        classes = [line.strip() for line in f]

    layer_names = net.getUnconnectedOutLayersNames()

    cap = cv2.VideoCapture(0)

    left_count = 0
    right_count = 0

    # Dictionary to store information about tracked persons
    tracked_persons = {}

    # Counter to assign unique IDs to individuals
    person_id_counter = 1

    def generate():
        nonlocal left_count, right_count, tracked_persons, person_id_counter

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            height, width, _ = frame.shape

            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            outs = net.forward(layer_names)

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
                        distance = np.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
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
                    cv2.putText(frame, f'{label} {confidence:.2f} {side}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                color, 2)

            cv2.putText(frame, f'IN: {left_count}  OUT: {right_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

            _, jpeg = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    response = StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

    def cleanup():
        cap.release()
        cv2.destroyAllWindows()

    response.on_close(cleanup)
    return response
