from .base import *

ENVIRONMENT = "dev"

DEBUG = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "HOST": "fly-0-nrt.pooler.supabase.com",
        "USER": "postgres.aqzyuyngwfdahoeccreq",
        "PASSWORD": "UbsziHCGbA8ASkO4",
        "PORT": "5432",
    }
}

ALLOWED_HOSTS = ['ainsight-be.fly.dev']

CSRF_TRUSTED_ORIGINS = ["https://*.fly.dev/"]
