"""
WSGI config for PlataformaDeCursos project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.contrib import admin
from django.core.wsgi import get_wsgi_application
from django.urls import path, include

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PlataformaDeCursos.settings')

application = get_wsgi_application()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Cursos/', include('Cursos.urls')),
]
