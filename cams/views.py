import datetime as dt
from django.utils import timezone
from django.http import Http404, HttpResponseForbidden, StreamingHttpResponse
from django.views.decorators import gzip
from rest_framework import viewsets

from cams import interfaces
from cams.models import Channel, Record
from cams.serializers import ChannelSerializer, RecordSerializer

@gzip.gzip_page
def image_stream(request, channel_id): 
    try:
        channel = Channel.objects.get(pk=channel_id)
    except Channel.DoesNotExist:
        raise Http404('Este canal no existe')

    try:
        camera_interface = interfaces.RedisCamera(access_key=channel.access_key)

        return StreamingHttpResponse(interfaces.frame_generator(camera_interface),
            content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as err:
        print(err)
        raise Http404('No se ha iniciado el streaming')


class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class RecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        date__gt = self.request.query_params.get('date__gt',
            timezone.now() - dt.timedelta(minutes=20))

        if date__gt is not None:
            queryset = queryset.filter(date__gt=date__gt)
        return queryset
