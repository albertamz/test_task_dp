import os
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = '6x0*&)@#53!=b_^wdyoale@7fh18v)*!4v&+!-903)j9yf8r)c'
DEBUG = True

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "db",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["app/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kiev"
USE_I18N = True
USE_TZ = False
USE_L10N = False

APPEND_SLASH = True

STATIC_URL = "static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "files/static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "files/static_prod")

MEDIA_ROOT = os.path.join(BASE_DIR, "files/media")
MEDIA_URL = "media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

now = datetime.now()
path = f"files/logs/server"
path += f"/{now.year}"
if not os.path.exists(path):
    os.mkdir(path)
path += f"/{now.month}"
if not os.path.exists(path):
    os.mkdir(path)
path += f"/{now.day}.log"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {"format": "LOG_%(levelname)-2s %(name)-12s: %(message)s;"},
        "file": {"format": "%(asctime)s %(levelname)-2s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": path,
        },
    },
    "loggers": {"": {"level": "INFO", "handlers": ["console", "file"]}},
}
