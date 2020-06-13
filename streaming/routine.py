import time
import socket
import logging
import datetime as dt
# import threading
from collections import defaultdict
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

def connect_camera(channel):
    active = True
    input_config = channel.config
    if channel.credential:
        input_config['credential'] = channel.credential

    InterfaceClass = getattr(interfaces, channel.camera_interface, None)
    if not InterfaceClass:
        logger.error(f"No se consigue la interface {channel.camera_interface}")
        channel.state = Channel.STATE_FAILED
        channel.save(update_fields=['state'])
        active = False

    try:
        interface = InterfaceClass(**input_config)
    except interfaces.RefusedConnection as err:
        logger.error(err)
        channel.state = Channel.STATE_FAILED
        channel.save(update_fields=['state'])
        active = False

    channel.state = Channel.STATE_ACTIVE
    channel.save(update_fields=['state'])
    logger.debug(f"Conectado al canal {channel.name}.")

    return {
        'active': active,
        'channel': channel,
        'interface': interface if active else None,
        'last_conection_try': dt.datetime.now()
    }

def processing_routine(channels):
    try:
        redis_transmitter = interfaces.RedisCamera()
    except interfaces.RefusedConnection as err:
        logger.error(err)
        time.sleep(RETAKE_TIMEOUT)
        return

    processor = CamProcessor(**channels[0].config)
    cameras = [connect_camera(channel) for channel in channels]

    while not _quit:
        now = dt.datetime.now()
        for index, camera in enumerate(cameras):
            if not camera['active']:
                if now > camera['last_conection_try'] + dt.timedelta(seconds=RETAKE_TIMEOUT):
                    logger.info(f"Reconectando canal {camera['channel'].name}...")
                    cameras[index] = connect_camera(camera['channel'])
                continue

            try:
                raw_frame = camera['interface'].get_frame()
                results = processor.inference(raw_frame)

            except KeyboardInterrupt as err:
                raise err

            except Exception as err:
                camera['channel'].state = Channel.STATE_FAILED
                camera['channel'].save(update_fields=['state'])
                logger.error(err)
                continue

            logger.debug(f"Capturadas {results['statistical']['amount_people']} personas en {camera['channel'].name}")

            redis_transmitter.send_frame(
                frame_to_jpg(results['frame'])
            )
            Record.objects.create(graphical=results['graphical'],
                channel=camera['channel'], **results['statistical'])

    for camera in cameras:
        camera['channel'].state = Channel.STATE_INACTIVE
        camera['channel'].save(update_fields=['state'])

    logger.info('Rutina interrumpida por teclado.')

def main():
    global _quit
    server_name = socket.gethostname()

    channels = Channel.objects.filter(enabled=True,
        process_id__startswith=server_name)

    channels_by_thread = defaultdict(list)
    [channels_by_thread[channel.process_id].append(channel) for channel in channels]

    logger.info(f'Inicializando: Se procesaran {len(channels)} canales.')

    try:
        with ThreadPoolExecutor(max_workers=len(channels_by_thread)) as executor:
            executor.map(processing_routine, channels_by_thread.values())
            # executor.submit(supervisor, index)
    except KeyboardInterrupt:
        _quit = True
