
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "distancia2.settings")
django.setup()

from streaming.routine import main

if __name__ == "__main__":
    main()
