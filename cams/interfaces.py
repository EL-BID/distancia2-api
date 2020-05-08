from abc import ABC, abstractmethod
import cv2

def frame_generator(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


class CameraInterface(ABC):
    def __del__(self):
        self.release()

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass


class LocalFileCamera(CameraInterface):
    def __init__(self, file_path, **kwargs):
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

# class IPCamera(CameraInterface)
#     def __init__(self, file_path, **kwargs):
#         # input_file = 'sample1.mp4'
#         self.camera = cv2.VideoCapture(file_path)

#     def release(self):
#         self.camera.release()

#     def get_frame(self):
#         ret, image = self.video.read()
#         ret, jpeg = cv2.imencode('.jpg', image)

#         return jpeg.tobytes()

# class RemoteCamera(CameraInterface):
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