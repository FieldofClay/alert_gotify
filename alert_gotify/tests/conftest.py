# encoding = utf-8
"""
Shared pytest configuration and fixtures for all tests.
"""
import sys
import os
from unittest.mock import Mock, MagicMock
import pytest


# Add package bin directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "package", "bin"))


@pytest.fixture
def mock_helper():
    """Create a mock helper object that simulates the UCC helper."""
    helper = Mock()
    
    # Default parameter values
    helper.get_param = Mock(side_effect=lambda key: {
        'url': None,
        'token': None,
        'message': 'Test message',
        'title': 'Test title',
        'priority': '5',
        'ssl_verify': None,
    }.get(key))
    
    # Default global settings
    helper.get_global_setting = Mock(side_effect=lambda key: {
        'gotify_url': 'https://gotify.example.com',
        'gotify_token': 'test_global_token',
    }.get(key))
    
    # Logging methods
    helper.log_info = Mock()
    helper.log_error = Mock()
    helper.log_warning = Mock()
    helper.log_debug = Mock()
    
    return helper


@pytest.fixture
def mock_helper_with_overrides():
    """Create a mock helper with URL and token overrides."""
    helper = Mock()
    
    helper.get_param = Mock(side_effect=lambda key: {
        'url': 'https://custom.gotify.local',
        'token': 'custom_token_123',
        'message': 'Override test message',
        'title': 'Override title',
        'priority': '8',
        'ssl_verify': '0',
    }.get(key))
    
    helper.get_global_setting = Mock(side_effect=lambda key: {
        'gotify_url': 'https://gotify.example.com',
        'gotify_token': 'test_global_token',
    }.get(key))
    
    helper.log_info = Mock()
    helper.log_error = Mock()
    helper.log_warning = Mock()
    helper.log_debug = Mock()
    
    return helper


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
