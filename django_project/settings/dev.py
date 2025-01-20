import os

from dotenv import load_dotenv

from .base import *

ENVIRONMENT = "dev"

DEBUG = True

load_dotenv()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "HOST": os.getenv('DB_HOST'),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "PORT": os.getenv('DB_PORT'),
    }
}

ALLOWED_HOSTS = ['ainsight-be.fly.dev', 'sipethon-3-6-ainsight-fe.vercel.app/', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = ["https://*.fly.dev/", 'https://*.vercel.app/']
