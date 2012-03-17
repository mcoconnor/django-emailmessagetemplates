from django.conf import settings

__all__ = []

_DEFAULTS = {
    'EMAILTEMPLATES_DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    'EMAILTEMPLATES_LOG_EMAILS': True,
    'EMAILTEMPLATES_LOG_RETENTION_DAYS': 30,
}

for key, value in _DEFAULTS.iteritems():
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    # Suppress errors from DJANGO_SETTINGS_MODULE not being set
    except ImportError:
        pass

class EmailTemplateError(ValueError):
    pass