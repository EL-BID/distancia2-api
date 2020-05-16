import socket

from cams import interfaces
from cams.models import Channel, Record, Alarm
from processors import CamProcessor

def processing_routine(channel):
    channel_config = channel.get_config()
    input_camera = getattr(interfaces, channel.camera_interface)(**channel_config)
    redis_transmitter = interfaces.RedisCamera(channel_config.get('access_key'))
    processor = CamProcessor()

    while True:
        raw_frame = input_camera.get_frame()

        try:
            results = processor.inference(raw_frame)
        except Exception as err:
            print(err)
            raise err

        redis_transmitter.send_frame(results['frame'])
        # Record.objects.create(results['statistical'])

if __name__ == "__main__":
    server_name = socket.gethostname()

    channels = Channel.objects.filter(process_id__starts_with=server_name)
    processing_routine(channels[0])
