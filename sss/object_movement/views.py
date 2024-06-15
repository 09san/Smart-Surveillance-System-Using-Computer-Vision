
from django.shortcuts import render
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from django.http.response import StreamingHttpResponse

from django.contrib.auth import get_user
from admin_app.models import *

from .models import ObjectMovementLogs
from django.core.files.base import ContentFile

from django.views.decorators import gzip

# Function to process a frame for object monitoring
def object_monitoring_backend_processing(frame, reference_frame):
    # Perform motion detection
    motion_score = calculate_ssim(frame, reference_frame)

    # You can adjust this threshold based on your specific scenario
    if motion_score < 0.9:
        # Motion detected
        print("Motion Detected - SSIM:", motion_score)
        cv2.putText(frame, "Motion Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Save object movement log
        #save_object_movement_log(frame,request)
        
        # Find contours of the moving object
        cnts, _ = cv2.findContours(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    _, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

# Function to calculate Structural Similarity Index (SSIM)
def calculate_ssim(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score

def object_monitoring_feed_generator(request):
    cap = cv2.VideoCapture(0)
    ret, reference_frame = cap.read()
    
    while True:
        print(cap.read())
        ret, frame = cap.read()
        cv2.imshow("Object Monitoring", frame)
        print("Reading frame")
        if not ret:
            break
        processed_frame = object_monitoring_backend_processing(frame, reference_frame)
        cv2.imshow("Object Monitoring", frame)

        print("Yielding frame")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n\r\n')

    cap.release()


@gzip.gzip_page
def object_monitoring_feed(request):
    #print("Video feed request")
    return StreamingHttpResponse(object_monitoring_feed_generator(request), content_type='multipart/x-mixed-replace; boundary=frame')

def object_monitoring(request):
    return render(request, 'object_monitoring/objectmonitoring.html')



# def save_object_movement_log(frame):
#     # Get the logged-in user
#     #user = get_user(request)

#     # Create an instance of ObjectMovementLogs
#     object_movement_log = ObjectMovementLogs(user=user.username)
    
#     # Convert OpenCV frame to BytesIO object
#     _, buffer = cv2.imencode('.jpg', frame)
#     image = ContentFile(buffer.tobytes())
    
#     # Save the frame as movement_image
#     object_movement_log.movement_image.save(f"{user.username}_movement.jpg", image)
    
#     # Save the instance
#     object_movement_log.save()

