# fire_detection/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FireDetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def send_fire_detection_event(self, event):
        await self.send(text_data=json.dumps({
            'fire_detected': True
        }))
