from django.shortcuts import render

import cv2         # Library for openCV
import threading   # Library for threading -- which allows code to run in backend
import playsound   # Library for alarm sound
import smtplib     # Library for email sending

from django.http import JsonResponse
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse

from django.views.decorators import gzip

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import os


import requests

from django.urls import reverse

fire_detection_process = None

def start_stop_backend_process(request):
    global fire_detection_process
    
    action = request.GET.get('action')

    if action == 'start':
        if fire_detection_process is None or not fire_detection_process.is_alive():
            # Start the fire detection backend
            try:
                backend_url = reverse('fire_detection_backend')
                response = requests.get(request.build_absolute_uri(backend_url))
                if response.status_code == 200:
                    return JsonResponse({'success': True, 'message': 'Fire detection backend started'})
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to start fire detection backend'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'success': False, 'message': f'Error starting backend: {e}'})
        else:
            return JsonResponse({'success': False, 'message': 'Fire detection backend is already running'})
    elif action == 'stop':
        if fire_detection_process and fire_detection_process.is_alive():
            # Stop the fire detection backend
            fire_detection_process.join()  # Wait for the process to finish
            fire_detection_process = None
            return JsonResponse({'success': True, 'message': 'Fire detection backend stopped'})
        else:
            return JsonResponse({'success': False, 'message': 'Fire detection backend is not running'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid action'})


def play_alarm_sound_function():
        playsound.playsound('static/fire_detection/fire_alarm.mp3', True)
        print("Fire alarm end")
        
# Function to send email
def send_mail_function():
        recipientmail = "add recipients mail"
        recipientmail = recipientmail.lower()
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login("add senders mail", 'add senders password')
            server.sendmail('add senders mail', recipientmail, "Warning fire accident has been reported")
            print("Alert mail sent successfully to {}".format(recipientmail))
            server.close()
        except Exception as e:
            print(e)
            
            


def fire_detection_backend_processing(frame):
    
    
    
    # Load the cascade classifier for fire detection
    fire_cascade = cv2.CascadeClassifier('static/fire_detection/fire_detection_cascade_model.xml')
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect fires in the frame
    fires = fire_cascade.detectMultiScale(gray, 1.2, 5)
    
    # Process each detected fire
    for (x, y, w, h) in fires:
        cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)

        # Print message and start alarm sound
        print("Fire detected!")
        threading.Thread(target=play_alarm_sound_function).start()
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'fire_detection_group', {
                'type': 'send_fire_detection_event',
                'event': 'fire_detected',
            }
        )

        # Send email notification
        if not runOnce:
            print("Sending email notification...")
            threading.Thread(target=send_mail_function).start()
            runOnce = True
    
    # Convert frame to JPEG format
    _, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()


  
def fire_detection_feed_generator():
    cap = cv2.VideoCapture(0)
    
    while True:
        print(cap.read())
        ret, frame = cap.read()
        cv2.imshow("Fire Detection", frame)
        print("Reading frame")
        if not ret:
            break
        processed_frame = fire_detection_backend_processing(frame)
        cv2.imshow("Fire Detection", frame)

        print("Yielding frame")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n\r\n')

    cap.release()
    


@gzip.gzip_page
def fire_detection_feed(request):
    #print("Video feed request")
    return StreamingHttpResponse(fire_detection_feed_generator(), content_type='multipart/x-mixed-replace; boundary=frame')

def fire_detection(request):
    return render(request, 'fire_detection/firedetection.html')
