from abc import ABC, abstractmethod
import threading

import redis
from redis.exceptions import TimeoutError
from django.conf import settings
import cv2

def frame_generator(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


class Camera(ABC):
    def __del__(self):
        self.release()

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass


class LocalFileCamera(Camera):
    def __init__(self, file_path=None, **kwargs):
        self.camera = cv2.VideoCapture(
            settings.BASE_DIR(file_path)
        )

        if not self.camera.isOpened():
            message = 'No se puede leer el archivo ' + file_path
            raise RefusedConnection(message)

    def release(self):
        self.camera.release()

    def get_frame(self):
        successful_read, raw_frame = self.camera.read()

        if not successful_read:
            message = 'No se pueden leer mas fotogramas'
            raise ClosedConnection(message)

        return raw_frame


class RedisCamera(Camera):
    client = None

    def __init__(self, access_key=None, **kwargs):
        if not access_key:
            message = 'No se encuentra el access_key en la configuracion'
            raise RefusedConnection(message)

        self.key = access_key
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            db=settings.REDIS_DATABASE,
            socket_connect_timeout=1
        )

        try:
            self.client.ping()
        except TimeoutError:
            message = 'No se puede conectar al servidor de Redis'
            raise RefusedConnection(message)

    def release(self):
        if self.client:
            self.client.close()

    def get_frame(self):
        raw_frame = self.client.get(self.key)

        if not raw_frame:
            message = f'No hay fotogramas disponibles para "{self.key}"' 
            raise ClosedConnection(message)

        return raw_frame

    def send_frame(self, frame):
        successful_send = self.client.set(self.key, frame, ex=30)

        if not successful_send:
            message = f'No pudo enviar el fotogama por "{self.key}"' 
            raise ClosedConnection(message)


class RTSPCamera(Camera):
    last_frame = None
    lock = threading.Lock()

    def __init__(self, credential=None, **kwargs):
        if not credential:
            message = 'No posee ninguna credencial asociada'
            raise RefusedConnection(message)

        url = f'rtsp://{credential.username}:{credential.password}@{credential.host}'
        if kwargs.get('detail_route'):
            url += kwargs['detail_route']

        self.camera = cv2.VideoCapture(url)

        if not self.camera.isOpened():
            message = 'No se puede acceder a ' + url
            raise RefusedConnection(message)

        thread = threading.Thread(target=self.cam_buffer)
        thread.daemon = True
        thread.start()

    def cam_buffer(self):
        while True:
            with self.lock:
                successful_read, self.last_frame = self.camera.read()

        if not successful_read:
            message = 'No se pueden leer mas fotogramas'
            raise ClosedConnection(message)

    def release(self):
        if self.camera:
            self.camera.release()

    def get_frame(self):
        if self.last_frame is None:
            message = 'Se ha cortado la comunicación'
            raise ClosedConnection(message)

        return self.last_frame


class RefusedConnection(Exception):
    pass


class ClosedConnection(Exception):
    pass
