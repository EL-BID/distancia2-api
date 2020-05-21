import socket
import logging

from cams import interfaces
from cams.models import Channel, Record, Alarm
from streaming.processors import CamProcessor

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

def processing_routine(channel):
    input_camera = getattr(interfaces, channel.camera_interface)(**channel.config)
    redis_transmitter = interfaces.RedisCamera(channel.config.get('access_key'))
    processor = CamProcessor()

    channel.state = Channel.STATE_ACTIVE
    channel.save(update_fields=['state'])
    logger.debug(f"Attached to channel {channel.name}")

    while True:
        raw_frame = input_camera.get_frame()

        try:
            results = processor.inference(raw_frame)

        except KeyboardInterrupt:
            channel.state = Channel.STATE_INACTIVE
            channel.save(update_fields=['state'])
            logger.debug('Rutina interrumpida por teclado.')
            break

        except Exception as err:
            channel.state = Channel.STATE_FAILED
            channel.save(update_fields=['state'])
            logger.error(err)
            raise err

        logger.debug(f"Got {results['statistical']['amount_people']} people at {channel.name}")

        redis_transmitter.send_frame(
            interfaces.LocalFileCamera.frame_to_jpg(results['frame'])
        )
        Record.objects.create(graphical=results['graphical'],
            channel=channel, **results['statistical'])

def main(channel_id):
    server_name = socket.gethostname()

    channels = Channel.objects.filter(enabled=True,
        process_id__startswith=server_name)
    processing_routine(channels[channel_id])


if __name__ == "__main__":
    main(0)
