"""
Test suite initialization - disables rate limiting for all tests.
This ensures throttling doesn't interfere with test execution.
"""
from django.conf import settings
from django.core.cache import cache


# Disable throttling for tests
if hasattr(settings, 'REST_FRAMEWORK'):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }

# Clear cache to ensure clean state
cache.clear()
