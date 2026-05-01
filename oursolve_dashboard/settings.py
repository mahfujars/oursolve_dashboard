import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security — override SECRET_KEY via environment variable on the server
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-only-insecure-key-change-before-deploying-to-production'
)

DEBUG = os.environ.get('DJANGO_DEBUG', '') == 'True'

ALLOWED_HOSTS = [
    'oursolve.com',
    'www.oursolve.com',
    'localhost',
    '127.0.0.1',
]

SITE_URL = 'https://oursolve.com'

# ---------------------------------------------------------------------------
# Run the app under /dashboard/ on cPanel
# ---------------------------------------------------------------------------
FORCE_SCRIPT_NAME = '/dashboard'
USE_X_FORWARDED_HOST = True

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',  # must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # Third-party
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'corsheaders',
    # Local
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oursolve_dashboard.middleware.NoCacheMiddleware',
]

ROOT_URLCONF = 'oursolve_dashboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oursolve_dashboard.wsgi.application'

# ---------------------------------------------------------------------------
# Database — SQLite (cPanel compatible, no extra services needed)
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = '/dashboard/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/dashboard/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', 'Bold', 'Italic', 'Underline', 'Strike', 'RemoveFormat'],
            ['BulletedList', 'NumberedList', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['TextColor', 'BGColor'],
            ['CodeSnippet'],
            ['Source', 'Maximize'],
        ],
        'extraPlugins': 'codesnippet',
        'codeSnippet_theme': 'github',
        'height': 520,
        'width': '100%',
    },
}

# ---------------------------------------------------------------------------
# CORS — allow the static site to call the API
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    'https://oursolve.com',
    'https://www.oursolve.com',
]

CORS_URLS_REGEX = r'^/dashboard/api/.*$'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
    },
}

# ---------------------------------------------------------------------------
# Logging — writes errors to /home/oursolve/oursolve_dashboard/logs/django.log
# ---------------------------------------------------------------------------
_LOG_DIR = BASE_DIR / 'logs'
try:
    _LOG_DIR.mkdir(exist_ok=True)
except OSError:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(_LOG_DIR / 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Point the admin login page back to /dashboard/
LOGIN_URL = '/dashboard/login/'

# ---------------------------------------------------------------------------
# Jazzmin — professional admin theme
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Oursolve Admin",
    "site_header": "Oursolve",
    "site_brand": "Oursolve",
    "welcome_sign": "Welcome to Oursolve Dashboard",
    "copyright": "Oursolve",
    "search_model": ["blog.BlogPost", "blog.Category"],
    "topmenu_links": [
        {"name": "View Site", "url": "https://oursolve.com", "new_window": True},
        {"name": "Blog", "url": "https://oursolve.com/blog/", "new_window": True},
        {"model": "blog.BlogPost"},
    ],
    "usermenu_links": [
        {"name": "View Site", "url": "https://oursolve.com", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "blog",
        "blog.BlogPost",
        "blog.Category",
        "blog.Tool",
        "blog.SiteSettings",
        "auth",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "blog": "fas fa-blog",
        "blog.BlogPost": "fas fa-file-alt",
        "blog.Category": "fas fa-folder-open",
        "blog.Tool": "fas fa-tools",
        "blog.SiteSettings": "fas fa-cog",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "brand_colour": "navbar-purple",
    "accent": "accent-purple",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-purple",
    "sidebar_nav_compact_style": True,
    "sidebar_nav_child_indent": True,
    "actions_sticky_top": True,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-success",
    },
}
