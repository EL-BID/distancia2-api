from django.http import Http404, HttpResponseServerError, StreamingHttpResponse
from django.views.decorators import gzip
from rest_framework import viewsets

from cams import interfaces
from cams.models import Channel
from cams.serializers import ChannelSerializer

@gzip.gzip_page
def image_stream(request, channel_id): 
    try:
        channel = Channel.objects.get(pk=channel_id)
    except Channel.DoesNotExist:
        raise Http404('Este canal no existe')

    try:
        camera_instance = getattr(interfaces, channel.camera_interface)(**channel.get_config())

        return StreamingHttpResponse(interfaces.frame_generator(camera_instance),
            content_type='multipart/x-mixed-replace; boundary=frame')
    except HttpResponseServerError:
        print("aborted")


class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
