from django.http import HttpResponseServerError, StreamingHttpResponse
from django.views.decorators import gzip

import cv2

from .interfaces import frame_generator, LocalFileCamera

@gzip.gzip_page
def index(request): 
    try:
        input_file = 'sample1.mp4'
        camera_instance = LocalFileCamera(input_file)
        return StreamingHttpResponse(frame_generator(camera_instance),
            content_type='multipart/x-mixed-replace; boundary=frame')
    except HttpResponseServerError:
        print("aborted")
