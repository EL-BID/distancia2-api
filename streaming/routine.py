import socket
import logging
# import threading
from concurrent.futures import ThreadPoolExecutor

from cams import interfaces
from cams.models import Channel, Record, Alarm
from streaming.processors import CamProcessor
from streaming.utils import frame_to_jpg

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

def processing_routine(channel):
    input_config = channel.config
    if channel.credential:
        input_config['credential'] = channel.credential

    input_camera = getattr(interfaces, channel.camera_interface)(**input_config)
    redis_transmitter = interfaces.RedisCamera(channel.config.get('access_key'))
    processor = CamProcessor()

    channel.state = Channel.STATE_ACTIVE
    channel.save(update_fields=['state'])
    logger.debug(f"Attached to channel {channel.name}")

    while True:
        try:
            raw_frame = input_camera.get_frame()
            results = processor.inference(raw_frame)

        except KeyboardInterrupt:
            channel.state = Channel.STATE_INACTIVE
            channel.save(update_fields=['state'])
            logger.debug('Rutina interrumpida por teclado.')
            break

        except interfaces.ClosedConnection as err:
            channel.state = Channel.STATE_FAILED
            channel.save(update_fields=['state'])
            logger.error(err.message)
            break

        except Exception as err:
            channel.state = Channel.STATE_FAILED
            channel.save(update_fields=['state'])
            logger.error(err)
            raise err

        logger.debug(f"Got {results['statistical']['amount_people']} people at {channel.name}")

        redis_transmitter.send_frame(
            frame_to_jpg(results['frame'])
        )
        Record.objects.create(graphical=results['graphical'],
            channel=channel, **results['statistical'])

def main(channel_id=None):
    server_name = socket.gethostname()

    channels = Channel.objects.filter(enabled=True,
        process_id__startswith=server_name)

    if channel_id:
        processing_routine(channels[channel_id])
    else:
        with ThreadPoolExecutor(max_workers=len(channels)) as executor:
            executor.map(processing_routine, channels)
            # executor.submit(supervisor, index)


if __name__ == "__main__":
    main(0)
