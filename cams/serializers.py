from rest_framework.reverse import reverse_lazy
from rest_framework import serializers

from cams.models import Channel, Record, Alarm

class ChannelSerializer(serializers.ModelSerializer):
    # config = serializers.JSONField(source='get_config')
    image_stream = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ('id', 'name', 'state', 'enabled', 'process_id',
            'camera_interface', 'last_connection', 'image_stream')

    def get_image_stream(self, instance):
        return reverse_lazy('image_stream', args=[instance.pk],
            request=self.context['request'])


class RecordSerializer(serializers.ModelSerializer):
    channel_name = serializers.JSONField(source='channel.name')
    minimal_distance = serializers.DecimalField(max_digits=15,
        decimal_places=3, coerce_to_string=False)
    average_distance = serializers.DecimalField(max_digits=15,
        decimal_places=3, coerce_to_string=False)

    class Meta:
        model = Record
        fields = ('date', 'channel_name', 'amount_people', 'average_distance',
            'minimal_distance', 'breaking_secure_distance')
