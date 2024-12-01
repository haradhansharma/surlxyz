from . import DEBUG, env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'new_selfurl' if DEBUG else env("SU_DB_NAME"),
        'USER': 'root' if DEBUG else env("SU_DB_USER"),
        'PASSWORD': '' if DEBUG else env("SU_DB_PASSWORD"),
        'HOST': env("SU_DB_HOST"),
        'PORT': env("SU_DB_PORT"),
        'OPTIONS': {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

    
  


