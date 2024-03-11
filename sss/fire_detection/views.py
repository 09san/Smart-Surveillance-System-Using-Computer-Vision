from django.shortcuts import render

import cv2         # Library for openCV
import threading   # Library for threading -- which allows code to run in backend
import playsound   # Library for alarm sound
import smtplib     # Library for email sending

from django.http import JsonResponse
from django.http import HttpResponse

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


def fire_detection_backend(request):
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
    
    # Load the cascade classifier for fire detection
    fire_cascade = cv2.CascadeClassifier('static/fire_detection/fire_detection_cascade_model.xml')
    
    # Initialize video capture from webcam
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect fires in the frame
        fires = fire_cascade.detectMultiScale(frame, 1.2, 5)

        for (x, y, w, h) in fires:
            cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)

            print("Fire alarm initiated")
            threading.Thread(target=play_alarm_sound_function).start()

            # Send email notification
            if not runOnce:
                print("Mail send initiated")
                threading.Thread(target=send_mail_function).start()
                runOnce = True

        # Display the frame
        cv2.imshow('Fire Detection', frame)

        # Check for key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close the window
    video_capture.release()
    cv2.destroyAllWindows()

    return HttpResponse("Fire detection backend finished")


    

def fire_detection(request):
    return render(request, 'fire_detection/firedetection.html')
