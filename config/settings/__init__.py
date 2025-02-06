import os
import environ


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
env = environ.Env()

SECRET_KEY = env("SU_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("No SU_SECRET_KEY set for production!")

DEBUG = env.bool("SU_DEBUG", default=False)



if DEBUG:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = ["https://127.0.0.1", "https://localhost"]
else:
    ALLOWED_HOSTS = env("SU_ALLOWED_HOSTS").split(",")
    CSRF_TRUSTED_ORIGINS = env("SU_CSRF_TRUSTED_ORIGINS").split(",")

SITE_ID=1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django_summernote',
    'django_user_agents',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    
    'main',  
    'captcha', 
    'accounts',     
    'policy_concent',
    'cms',
    'contact',
    'selfurl',
    # "django_cron",
    'license_control',
    'django_celery_results',
    'django_celery_beat',

    
]



CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("SU_CACHES_LOCATION"),   
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

USER_AGENTS_CACHE = 'default'
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_EXTENDED = True

CELERY_BROKER_URL = env("SU_CELERY_BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CACHE_MIDDLEWARE_SECONDS = 3600




TEMPLATE_TAGS = ['django_summernote.templatetags.summernote']
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

LOGIN_URL = "/accounts/login/"

# LOGIN_REDIRECT_URL = "/accounts/%s/"

LOGOUT_REDIRECT_URL = '/'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',  #new    
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware', #new    
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]
    

ROOT_URLCONF = 'config.urls'



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processor.core_con'
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


from .settings_database import *
from .settings_local import *
# from .settings_security import *


STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if DEBUG:
    from .dev import *
else:
    from .pro import *

LOGIN_REQUIRE_WITHIN_DAYS = 7


MONTH_IN_SECONDS = 30 * 24 * 60 * 60 
VT_RATE_LIMITE_PER_MONTH = 15500
VT_API_KEY = env('SU_VT_API_KEY')
GEOLOCATIONDBKEY = env('SU_GEOLOCATIONDBKEY')
IP2LOCATIONKEY = env('SU_IP2LOCATIONKEY')


# CRON_CLASSES = [
#     "main.cron_jobs.SelfCronJob",    
# ]

CLEAN_DECISION = 'clean'  

