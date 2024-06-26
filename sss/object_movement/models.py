from django.db import models
from admin_app.models import CustomUser

class ObjectMovementLogs(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    movement_image = models.ImageField(upload_to="object_movement_logs")
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
