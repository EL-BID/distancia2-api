import time
import socket
import logging
# import threading
from concurrent.futures import ThreadPoolExecutor

from cams import interfaces
from cams.models import Channel, Record, Alarm
from streaming.processors import CamProcessor
from streaming.utils import frame_to_jpg

LOGGING_FORMAT = '%(asctime)s [%(processName)s_%(thread)s]: %(message)s'
logging.basicConfig(level=logging.DEBUG,
    format=LOGGING_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('ProcesingRoutine')

RETAKE_TIMEOUT = 60
_quit = False
def processing_routine(channel):
    input_config = channel.config
    if channel.credential:
        input_config['credential'] = channel.credential

    interface = getattr(interfaces, channel.camera_interface, None)
    if not interface:
        logger.error(f"No se consigue interface {channel.camera_interface}")
        return

    try:
        input_camera = interface(**input_config)
        redis_transmitter = interfaces.RedisCamera(channel.config.get('access_key'))
    except interfaces.RefusedConnection as err:
        logger.error(err)
        time.sleep(RETAKE_TIMEOUT)
        logger.info(f'Retaken channel {channel.name}')
        return processing_routine(channel)

    processor = CamProcessor(**input_config)

    channel.state = Channel.STATE_ACTIVE
    channel.save(update_fields=['state'])
    logger.debug(f"Conectado al canal {channel.name}.")

    while not _quit:
        try:
            raw_frame = input_camera.get_frame()
            results = processor.inference(raw_frame)

        except interfaces.ClosedConnection as err:
            channel.state = Channel.STATE_FAILED
            channel.save(update_fields=['state'])
            logger.error(err)
            time.sleep(RETAKE_TIMEOUT)
            logger.info(f'Retomando canal {channel.name}.')
            return processing_routine(channel)

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

    channel.state = Channel.STATE_INACTIVE
    channel.save(update_fields=['state'])
    logger.info('Rutina interrumpida por teclado.')

def main(channel_id=None):
    global _quit
    server_name = socket.gethostname()

    channels = Channel.objects.filter(enabled=True,
        process_id__startswith=server_name)

    logger.info(f'Inicializando: Se procesaran {len(channels)} canales.')

    try:
        if channel_id:
            processing_routine(channels[channel_id])
        else:
            with ThreadPoolExecutor(max_workers=len(channels)) as executor:
                executor.map(processing_routine, channels)
                # executor.submit(supervisor, index)
    except KeyboardInterrupt:
        _quit = True
