import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Do not change these! Override them in local_settings.py if necessary.
DEBUG = False
TEMPLATE_DEBUG = False

# ALLOWED_HOSTS is required in >Django 1.5. Since we allow customers to CNAME their domain
# to microcosm, we cannot make use of this feature. Host is verified in the API.
ALLOWED_HOSTS = [
    '*',
]

# Test runner gets unhappy if there's no database defined.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'

# For Django sites framework, not used for anything in microcosm.
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = '/srv/www/django/sitegen/static/'

# URL prefix for static files.
STATIC_URL = '/static/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.static',
)

TEMPLATE_DIRS = ()

MIDDLEWARE_CLASSES = (

    # Note: if using messages, enable the sessions middleware too
    'django.middleware.common.CommonMiddleware',

    # CSRF protection on form submission
    'django.middleware.csrf.CsrfViewMiddleware',

    # convenience for request context like site, user account, etc.
    'core.middleware.context.ContextMiddleware',

    # cache busting for static files
    'core.middleware.modtimeurls.ModTimeUrlsMiddleware',

    # time all requests and report to riemann
    #'microcosm.middleware.timing.TimingMiddleware',

    # push exceptions to riemann
    #'microcosm.middleware.exception.ExceptionMiddleware',

)

ROOT_URLCONF = 'sitegen.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sitegen.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'core',
    'microcosm_site',
    'microcosm_admin',
    'updates',
    'gunicorn',
)

# Populate the settings below in local_settings.py (see the local_settings.py.sample for example values).
from local_settings import CLIENT_ID
from local_settings import CLIENT_SECRET
from local_settings import API_SCHEME
from local_settings import API_DOMAIN_NAME
from local_settings import API_PATH
from local_settings import API_VERSION
from local_settings import RIEMANN_ENABLED
from local_settings import RIEMANN_HOST
from local_settings import MEMCACHE_HOST
from local_settings import MEMCACHE_PORT
from local_settings import SECRET_KEY
from local_settings import PAGE_SIZE
from local_settings import DEBUG