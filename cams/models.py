import json
import logging

import numpy as np
from django.db import models
from distancia2.fields import JSONField

logger = logging.getLogger()


class Channel(models.Model):
    STATE_ACTIVE = 'active'
    STATE_INACTIVE = 'inactive'
    STATE_LOCKED = 'locked'
    STATE_FAILED = 'failed'

    LOCAL_FILE_INTERFACE = 'LocalFileCamera'
    RTSP_INTERFACE = 'RTSPCamera'
    REDIS_INTERFACE = 'RedisCamera'

    STATE_CHOICES = [
        (STATE_ACTIVE, STATE_ACTIVE),
        (STATE_INACTIVE, STATE_INACTIVE),
        (STATE_LOCKED, STATE_LOCKED),
        (STATE_FAILED, STATE_FAILED),
    ]

    CAMERA_INTERFACE_CHOICES = [
        # (LOCAL_FILE_INTERFACE, LOCAL_FILE_INTERFACE),
        (RTSP_INTERFACE, RTSP_INTERFACE),
        # (REDIS_INTERFACE, REDIS_INTERFACE),
    ]

    name = models.CharField(max_length=256)
    state = models.CharField(max_length=20,
        default=STATE_INACTIVE, choices=STATE_CHOICES)
    enabled = models.BooleanField(default=False)
    process_id = models.CharField(max_length=100, blank=True)
    processor_name = models.CharField(max_length=100, blank=True)
    camera_reference = models.CharField(max_length=100)
    camera_interface = models.CharField(max_length=100,
        choices=CAMERA_INTERFACE_CHOICES)
    last_connection = models.DateTimeField(blank=True, null=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    credential = models.ForeignKey('RemoteCredential',
        on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    def attach(self, process_id):
        if Channel.objects.filter(pk=self.pk, state=Channel.STATE_ACTIVE).exists():
            logger.error(f'The camera {self.name} has been attached to another process.')
            return False

        self.process_id = process_id
        self.state = Channel.STATE_ACTIVE
        self.save()
        return True

    @property
    def last_record(self):
        return self.records.first()

    @property
    def access_key(self):
        return f'{type(self).__name__}_{self.id}'

    @classmethod
    def get_access_key(cls, _id):
        return f'{cls.__name__}_{_id}'


class Record(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='records', related_query_name='record')
    amount_people = models.IntegerField()
    breaking_secure_distance = models.IntegerField()
    minimal_distance = models.FloatField()
    average_distance = models.FloatField()
    graphical = JSONField()

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date'], name='date_index'),
        ]


class Alarm(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='alarms', related_query_name='alarm')
    type = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)

    class Meta:
        ordering = ['-date']


class RemoteCredential(models.Model):
    host = models.CharField(max_length=256, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)

    def __str__(self):
        return '{}: {}'.format(self.host, self.username)
