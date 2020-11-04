import argparse
import cv2
from functools import wraps
from time import time

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('Tardó: {:2.4f} segundos'.format(te-ts))
        return result
    return wrap

@timing
def test_camera(url):
    camera = cv2.VideoCapture(url)

    if camera.isOpened():
        print('Se logró establecer conexión con la camara de forma exitosa ! !')
    else:
        print('No se logra conectar con la url ' + url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Permite probar la url de una camara con opencv.')
    parser.add_argument('url', help='url de la camara')
    args = parser.parse_args()
    test_camera(args.url)
