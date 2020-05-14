import json
import logging
from django.db import models

logger = logging.getLogger()

class ChannelManager(models.Manager):
    def get_and_lock(self, camera_interface, cameras_number):
        queryset = self.get_queryset().filter(camera_interface=camera_interface, state=Channel.STATE_INACTIVE)
        channels_available_count = queryset.count()

        if not channels_available_count:
            logger.warning('Do not have cameras availables to be analized.')
            return queryset

        if channels_available_count < cameras_number:
            logger.warning(f'Will be analized {channels_available_count} cameras availables.')
            cameras_locked = channels_available_count

        else:
            cameras_locked = cameras_number

        new_qs = []
        for channel in queryset[:cameras_locked]:
            channel.state = Channel.STATE_LOCKED
            channel.save(update_fields=['state'])
            new_qs.append(channel)

        return new_qs


class Channel(models.Model):
    STATE_ACTIVE = 'active'
    STATE_INACTIVE = 'inactive'
    STATE_LOCKED = 'locked'
    STATE_FAILED = 'failed'

    LOCAL_FILE_INTERFACE = 'LocalFileCamera'
    REDIS_INTERFACE = 'RedisCamera'

    STATE_CHOICES = [
        (STATE_ACTIVE, STATE_ACTIVE),
        (STATE_INACTIVE, STATE_INACTIVE),
        (STATE_LOCKED, STATE_LOCKED),
        (STATE_FAILED, STATE_FAILED),
    ]

    CAMERA_INTERFACE_CHOICES = [
        (LOCAL_FILE_INTERFACE, LOCAL_FILE_INTERFACE),
        (REDIS_INTERFACE, REDIS_INTERFACE),
    ]

    name = models.CharField(max_length=256)
    state = models.CharField(max_length=20,
        default=STATE_INACTIVE, choices=STATE_CHOICES)
    enabled = models.BooleanField(default=False)
    process_id = models.CharField(max_length=100, blank=True)
    camera_interface = models.CharField(max_length=100,
        choices=CAMERA_INTERFACE_CHOICES)
    live = models.BooleanField(default=False)
    last_connection = models.DateTimeField(blank=True, null=True)
    config = models.TextField(default='{}')
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    objects = ChannelManager()

    def __str__(self):
        return self.name

    def get_config(self):
        return json.loads(self.config)

    def attach(self, process_id):
        if Channel.objects.filter(pk=self.pk, state=Channel.STATE_ACTIVE).exists():
            logger.error(f'The camera {self.name} has been attached to another process.')
            return False

        self.process_id = process_id
        self.state = Channel.STATE_ACTIVE
        self.save()
        return True

    # def release(self)


class Record(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='records', related_query_name='record')
    details = models.TextField()


class Alarm(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='alarms', related_query_name='alarm')
    type = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
