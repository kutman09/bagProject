"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# SQLite on Vercel is ephemeral (/tmp), so ensure tables exist on cold start.
if os.getenv("VERCEL"):
    call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
