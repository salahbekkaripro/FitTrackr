"""
WSGI config for FitTrackr project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitTrackr.settings')

application = get_wsgi_application()

# Serve staticfiles + media via WhiteNoise (small media set for boutique)
BASE_DIR = Path(__file__).resolve().parent.parent
application = WhiteNoise(application, root=str(BASE_DIR / "staticfiles"))
application.add_files(str(BASE_DIR / "media"), prefix="media/")
