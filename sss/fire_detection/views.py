from django.shortcuts import render

import cv2         # Library for openCV
import threading   # Library for threading -- which allows code to run in backend
import playsound   # Library for alarm sound
import smtplib     # Library for email sending

from django.http import JsonResponse

import os


import requests

fire_detection_process= None
def start_stop_backend_process(request):
    global fire_detection_process
    
    action = request.GET.get('action')

    if action == 'start':
        if fire_detection_process is None or not fire_detection_process.is_alive():
            # Start the fire detection backend
            response = requests.get('http://127.0.0.1/:8000/home/firedetection/fire_detection_backend/')
            if response.status_code == 200:
                return JsonResponse({'success': True, 'message': 'Fire detection backend started'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to start fire detection backend'})
            
            # fire_detection_process = threading.Thread(target=fire_detection_backend)
            # fire_detection_process.start()
            # return JsonResponse({'success': True, 'message': 'Fire detection backend started'})
      
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

# Create your views here.
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
    
    # # Load the cascade classifier
    fire_cascade = cv2.CascadeClassifier('static/fire_detection/fire_detection_cascade_model.xml')
    
    # Assuming the XML file is in the 'fire_detection' app directory
    # xml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fire_detection_cascade_model.xml')
    # fire_cascade = cv2.CascadeClassifier(xml_file_path)
        

    # Initialize video capture
    #vid = cv2.VideoCapture(0)
    runOnce = False

    while True:
        Alarm_Status = False
        ret, frame = cv2.VideoCapture(0).read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fire = fire_cascade.detectMultiScale(frame, 1.2, 5)

        for (x, y, w, h) in fire:
            cv2.rectangle(frame, (x-20, y-20), (x+w+20, y+h+20), (255, 0, 0), 2)

            print("Fire alarm initiated")
            threading.Thread(target=play_alarm_sound_function).start()

            if not runOnce:
                print("Mail send initiated")
                threading.Thread(target=send_mail_function).start()
                runOnce = True

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and destroy windows
    # vid.release()
    cv2.destroyAllWindows()

    

    

def fire_detection(request):
    return render(request, 'fire_detection/firedetection.html')
