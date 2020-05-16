from abc import ABC, abstractmethod

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
        self.camera = cv2.VideoCapture(file_path)

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

        successful_encode, jpeg_frame = cv2.imencode('.jpg', raw_frame)

        if not successful_encode:
            message = 'No se puede codificar el fotograma'
            raise Exception(message)

        return jpeg_frame.tobytes()


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
        raw_frame = self.client.get(self.key)
        self.client.get(self.key)

        if not raw_frame:
            message = f'No hay fotogramas disponibles para "{self.key}"' 
            raise ClosedConnection(message)

        return raw_frame


# class IPCamera(Camera)
#     def __init__(self, file_path, **kwargs):
#         # input_file = 'sample1.mp4'
#         self.camera = cv2.VideoCapture(file_path)

#     def release(self):
#         self.camera.release()

#     def get_frame(self):
#         ret, image = self.video.read()
#         ret, jpeg = cv2.imencode('.jpg', image)

#         return jpeg.tobytes()


class RefusedConnection(Exception):
    pass


class ClosedConnection(Exception):
    pass
