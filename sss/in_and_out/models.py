from django.db import models

class TrackedPerson(models.Model):
    person_id = models.AutoField(primary_key=True)
    # You can add more fields to store additional information about the tracked person
    # For example:
    # name = models.CharField(max_length=100)
    # age = models.IntegerField()
    # Add more fields as needed based on your requirements

class PersonMovement(models.Model):
    tracked_person = models.ForeignKey(TrackedPerson, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    movement_direction = models.CharField(max_length=3, choices=[('IN', 'IN'), ('OUT', 'OUT')])
    # You can add more fields here to store additional information about the movement
    # For example:
    # movement_location = models.CharField(max_length=100)
    # Add more fields as needed based on your requirements
