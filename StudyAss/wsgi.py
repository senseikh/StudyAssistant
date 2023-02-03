"""
WSGI config for StudyAss project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, 
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudyAss.settings')

application = get_wsgi_application()
