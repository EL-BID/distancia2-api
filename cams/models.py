import json
import logging

import numpy as np
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from distancia2.fields import JSONField

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger()

process_id_validator = RegexValidator(regex=r'\w+\.\w+',
    message=_('El parametro debe estar en el formato "nombre_servidor.nombre_hilo01"'))


class Channel(models.Model):
    STATE_ACTIVE = 'active'
    STATE_INACTIVE = 'inactive'
    STATE_LOCKED = 'locked'
    STATE_FAILED = 'failed'

    LOCAL_FILE_INTERFACE = 'LocalFileCamera'
    RTSP_INTERFACE = 'RTSPCamera'
    HTTP_INTERFACE = 'HTTPCamera'
    HTTPS_INTERFACE = 'HTTPSCamera'
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
        (HTTP_INTERFACE, HTTP_INTERFACE),
        (HTTPS_INTERFACE, HTTPS_INTERFACE),
        # (REDIS_INTERFACE, REDIS_INTERFACE),
    ]

    URL_CAMERA_PROTOCOLS = {
        RTSP_INTERFACE: 'rtsp',
        HTTP_INTERFACE: 'http',
        HTTPS_INTERFACE: 'https'
    }

    name = models.CharField(max_length=256,
        help_text='Nombre de referecia de la cámara.')
    state = models.CharField(max_length=20,
        default=STATE_INACTIVE, choices=STATE_CHOICES)
    enabled = models.BooleanField(default=False,
        help_text='Se utiliza para determinar si el sistema se conectará a la cámara.')
    process_id = models.CharField(max_length=100, blank=True, validators=[process_id_validator],
        help_text='Referecia del servidor y del hilo dispuesto para el procesamiento de la cámara.')
    processor_name = models.CharField(max_length=100, blank=True,
        help_text='Parametro utilizado en el caso de disponibilidad de GPU.')
    camera_reference = models.CharField(max_length=100,
        help_text='Path de la direccion url de la cámara.')
    camera_interface = models.CharField(max_length=100,
        default=RTSP_INTERFACE, choices=CAMERA_INTERFACE_CHOICES,
        help_text='Tipo de conexión a la cámara.')
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
        if settings.QUERY_LAST_RECORD:
            return self.records.first()
        else:
            return None

    @property
    def url(self):
        if self.credential and self.camera_interface in self.URL_CAMERA_PROTOCOLS:
            protocol = self.URL_CAMERA_PROTOCOLS[self.camera_interface]
            return self.credential.build_url(protocol, self.camera_reference)
        else:
            return self.camera_reference

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
    host = models.CharField(max_length=256, default='localhost')
    port = models.IntegerField(blank=True, null=True, default=554)
    username = models.CharField(max_length=256, blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return '{}: {}'.format(self.host, self.username)

    def build_url(self, protocol, camera_reference):
        url = protocol + '://'
        if self.username:
            url += self.username
            if self.password:
                url += ':' + self.password
            url += '@'

        url += self.host
        if self.port:
            url += ':' + str(self.port)

        if camera_reference is not None:
            url += camera_reference
        return url


class GroupedRecord(models.Model):
    group_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
        related_name='grouped_records', related_query_name='grouped_record')
    amount_records = models.IntegerField()
    amount_people = models.IntegerField()
    amount_people_breaking_secure_distance = models.IntegerField()
    minimal_distance = models.FloatField()
    average_distance = models.FloatField()
    percentile90_amount_people = models.FloatField()

    class Meta:
        ordering = ['-group_date']
        unique_together = ['channel', 'group_date']
        indexes = [
            models.Index(fields=['-group_date'], name='group_date_index'),
        ]
