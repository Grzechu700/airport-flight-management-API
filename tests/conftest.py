"""
Test configuration file - disables rate limiting for tests only.
This file configures the test environment without modifying project settings.
"""
import pytest
from django.conf import settings


def pytest_configure():
    """
    Configure Django settings for tests.
    This runs before any tests and disables throttling.
    """
    if hasattr(settings, 'REST_FRAMEWORK'):
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}
