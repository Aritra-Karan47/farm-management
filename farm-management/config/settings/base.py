"""
Base settings for the Farm Management Platform.

Database: Neon PostgreSQL (primary operational DB) via DATABASE_URL env var.
Falls back to local SQLite automatically if DATABASE_URL is not set, so the
project runs out of the box for development / evaluation without needing
real Neon credentials.

File storage: Supabase (S3-compatible object storage) via django-storages
style env vars. Falls back to local filesystem storage if not configured.
"""

import os
from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

AUTH_USER_MODEL = "accounts.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # third party
    "rest_framework",
    "django_filters",
    # local apps - order matters for auth/tenancy first
    "apps.tenants",
    "apps.accounts",
    "apps.farms",
    "apps.staff",
    "apps.animals",
    "apps.breeding",
    "apps.health",
    "apps.feed",
    "apps.sales",
    "apps.procurement",
    "apps.finance",
    "apps.dashboard",
    "apps.notifications",
    "apps.reports",
    "apps.audit",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom: attaches request.farm (tenant scoping) + audit context
    "apps.tenants.middleware.CurrentFarmMiddleware",
    "apps.audit.middleware.AuditContextMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.farms.context_processors.current_farm",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database - Neon PostgreSQL, falls back to SQLite for local/dev use
# ---------------------------------------------------------------------------
DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=config("DATABASE_SSL_REQUIRE", default=True, cast=bool),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# I18N
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="Asia/Kolkata")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static / media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Supabase object storage (optional - falls back to local media/ storage)
# Set SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_BUCKET to enable.
# Actual upload wiring lives in apps/attachments storage backend; when the
# env vars are absent the app transparently uses Django's local FileSystem
# storage so the project is fully usable without a Supabase account.
# ---------------------------------------------------------------------------
SUPABASE_URL = config("SUPABASE_URL", default="")
SUPABASE_SERVICE_KEY = config("SUPABASE_SERVICE_KEY", default="")
SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="farm-attachments")

# ---------------------------------------------------------------------------
# Auth redirects
# ---------------------------------------------------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "accounts:login"

# ---------------------------------------------------------------------------
# DRF
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}

# ---------------------------------------------------------------------------
# Session / security basics
# ---------------------------------------------------------------------------
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
