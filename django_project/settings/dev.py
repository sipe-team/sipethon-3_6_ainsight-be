from .base import *

ENVIRONMENT = "dev"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "HOST": "db.tkfurcrlobggbeotpevg.supabase.co",
        "USER": "postgres",
        "PASSWORD": "fAfQ6wutJVDRByjS",
        "PORT": "5432",
    }
}