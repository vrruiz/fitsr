import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'fitsr.settings'
sys.path.append('/var/www/fitsr.infoastro.com/')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
