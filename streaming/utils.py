
import cv2

def frame_to_jpg(frame):
    successful_encode, jpeg_frame = cv2.imencode('.jpg', frame)

    if not successful_encode:
        message = 'No se puede codificar el fotograma'
        raise Exception(message)

    return jpeg_frame.tobytes()
