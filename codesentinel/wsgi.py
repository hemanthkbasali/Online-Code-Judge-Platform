"""WSGI config for CodeSentinel."""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codesentinel.settings")

application = get_wsgi_application()
