import os
import sys
import dj_database_url

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'SM@g_V0u%eN$/jJb_lRZUOYnpo=P*{aS9nUPj~kWD2iMB%vkDy')

# SECURITY WARNING: don't run with debug turned on in production!
env_debug = os.environ.get('DEBUG', 'False')
DEBUG = True if env_debug == 'True' else False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'corsheaders',
    'comments',
    'rest_framework',
    'djcelery',
    'common',
    'testreport',
    'cdws_api',
    'stages',
    'metrics',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'pycd.disablecsrf.DisableCSRF',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTH_LDAP3_SERVER_URI = os.environ.get('AUTH_LDAP3_SERVER_URI', '')

AUTH_LDAP3_SEARCH_USER_DN = os.environ.get('AUTH_LDAP3_SEARCH_USER_DN', '')

AUTH_LDAP3_SEARCH_USER_PASSWORD = os.environ.get(
    'AUTH_LDAP3_SEARCH_USER_PASSWORD', None)

AUTH_LDAP3_SEARCH_BASE = os.environ.get('AUTH_LDAP3_SEARCH_BASE', '')

AUTH_LDAP3_SEARCH_FILTER = os.environ.get('AUTH_LDAP3_SEARCH_FILTER', '')

AUTH_LDAP3_ATTRIBUTES_MAPPING = {
    'username': 'sAMAccountName',
    'first_name': None,
    'last_name': None,
    'email': 'mail',
    'is_active': None,
    'is_superuser': None,
    'is_staff': None
}

if AUTH_LDAP3_SEARCH_USER_PASSWORD is not None:
    AUTHENTICATION_BACKENDS = (
        'authentication.backend.ADBackend',
        'django.contrib.auth.backends.ModelBackend',
    )
else:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )

ROOT_URLCONF = 'pycd.urls'
WSGI_APPLICATION = 'pycd.wsgi.application'

if 'test' in sys.argv:
    TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
    TEST_OUTPUT_VERBOSE = True
    TEST_OUTPUT_DESCRIPTIONS = True
    TEST_OUTPUT_DIR = 'reports'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3'
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config()
    }

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Novosibirsk')
USE_I18N = True
USE_L10N = True
USE_TZ = True

CDWS_API_HOSTNAME = os.environ.get('CDWS_API_HOSTNAME')

if not CDWS_API_HOSTNAME:
    raise RuntimeError('Please set the environment variable CDWS_API_HOSTNAME')

CDWS_API_PATH = 'api'
CDWS_DEPLOY_DIR = os.environ.get('CDWS_DEPLOY_DIR', '/opt')
CDWS_WORKING_DIR = os.environ.get('CDWS_WORKING_DIR', '/tmp/')


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'common.context_processors.projects'
)

REST_FRAMEWORK = {
    'PAGINATE_BY': 100,
    'PAGINATE_BY_PARAM': 'page_size',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['console']
    },
    'formatters': {
        'standard': {
            'format': '{ "level": "%(levelname)s", '
                      '"message": "%(message)s", '
                      '"lineno": "%(lineno)s", '
                      '"pathname": "%(pathname)s" }',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

CELERY_HOST = os.environ.get('CELERY_HOST', '')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_URL = os.environ.get('BROKER_URL')
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_USER = 'ubuntu'
CELERY_TRACK_STARTED = True
CELERY_CHORD_PROPAGATES = True
CELERY_RESULT_ENGINE_OPTIONS = {'pool_recycle': 3600}

JIRA_INTEGRATION = os.environ.get('JIRA_INTEGRATION', False)
# if JIRA_INTEGRATION = True, please fill constants below
TIME_BEFORE_UPDATE_BUG_INFO = os.environ.get(
    'TIME_BEFORE_UPDATE_BUG_INFO', 10800)
BUG_TIME_EXPIRED = os.environ.get('BUG_TIME_EXPIRED', 1209600)
BUG_STATE_EXPIRED = os.environ.get('BUG_STATE_EXPIRED')
BUG_TRACKING_SYSTEM_HOST = os.environ.get('BUG_TRACKING_SYSTEM_HOST')
BUG_TRACKING_SYSTEM_LOGIN = os.environ.get('BUG_TRACKING_SYSTEM_LOGIN')
BUG_TRACKING_SYSTEM_PASSWORD = os.environ.get('BUG_TRACKING_SYSTEM_PASSWORD')
BUG_TRACKING_SYSTEM_BUG_PATH = os.environ.get('BUG_TRACKING_SYSTEM_BUG_PATH')
TRACKING_SYSTEM_SEARCH_PATH = os.environ.get('TRACKING_SYSTEM_SEARCH_PATH')

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
if not DEBUG:
    COOKIE_DOMAIN = os.environ.get('COOKIE_DOMAIN', '')
    SESSION_COOKIE_DOMAIN = COOKIE_DOMAIN

STORE_TESTRESULTS_IN_DAYS = os.environ.get('STORE_TESTRESULTS_IN_DAYS', 7)
RUNDECK_URL = os.environ.get('RUNDECK_URL', '')
