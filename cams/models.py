import json
from django.db import models


class Channel(models.Model):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    FAILED = 'failed'

    STATE_CHOICES = [
        (ACTIVE, ACTIVE),
        (INACTIVE, INACTIVE),
        (FAILED, FAILED),
    ]

    name = models.CharField(max_length=256)
    state = models.CharField(max_length=20,
        default=INACTIVE, choices=STATE_CHOICES)
    enabled = models.BooleanField(default=False)
    process_id = models.CharField(max_length=100)
    camera_interface = models.CharField(max_length=100)
    last_connection = models.DateTimeField()
    config = models.TextField()
    # latitude = models.FloatField()
    # longitude = models.FloatField()

    def __str__(self):
        return self.name

    def get_config(self):
        return json.loads(self.config)


class Record(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='records', related_query_name='record')
    # people_count = models.IntegerField()
    # people_min = models.IntegerField()
    # people_average = models.FloatField()


class Alarm(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='alarms', related_query_name='alarm')
    type = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
