# encoding = utf-8
"""
Unit tests for alert_gotify main module.
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Mock the splunktaucclib module before importing
sys.modules['splunktaucclib'] = MagicMock()
sys.modules['splunktaucclib.alert_actions_base'] = MagicMock()

# Import the module to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "package", "bin"))

# Import from the main module file, not the package
import importlib.util
spec = importlib.util.spec_from_file_location(
    "alert_gotify_module",
    os.path.join(os.path.dirname(__file__), "..", "..", "package", "bin", "alert_gotify.py")
)
alert_gotify_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alert_gotify_module)
AlertActionWorkeralert_gotify = alert_gotify_module.AlertActionWorkeralert_gotify


@pytest.mark.unit
class TestAlertActionWorker:
    """Test the main AlertActionWorker class."""

    def test_worker_initialization(self):
        """Test that worker can be initialized."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        assert worker is not None

    def test_validate_params_success_with_global_settings(self):
        """Test validation succeeds when message/priority provided and global settings exist."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        # Mock get_param and get_global_setting
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test message',
            'priority': '5',
            'url': None,
            'token': None,
        }.get(key))
        
        worker.get_global_setting = Mock(side_effect=lambda key: {
            'gotify_url': 'https://gotify.example.com',
            'gotify_token': 'test_token',
        }.get(key))
        
        worker.log_error = Mock()
        
        assert worker.validate_params() is True
        worker.log_error.assert_not_called()

    def test_validate_params_success_with_overrides(self):
        """Test validation succeeds when URL/token provided in alert config."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test message',
            'priority': '5',
            'url': 'https://custom.gotify.local',
            'token': 'custom_token',
        }.get(key))
        
        worker.get_global_setting = Mock(side_effect=lambda key: None)
        worker.log_error = Mock()
        
        assert worker.validate_params() is True
        worker.log_error.assert_not_called()

    def test_validate_params_fails_without_message(self):
        """Test validation fails when message is missing."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': None,
            'priority': '5',
            'url': 'https://gotify.example.com',
            'token': 'test_token',
        }.get(key))
        
        worker.get_global_setting = Mock(side_effect=lambda key: None)
        worker.log_error = Mock()
        
        assert worker.validate_params() is False
        worker.log_error.assert_called()

    def test_validate_params_fails_without_priority(self):
        """Test validation fails when priority is missing."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test message',
            'priority': None,
            'url': 'https://gotify.example.com',
            'token': 'test_token',
        }.get(key))
        
        worker.get_global_setting = Mock(side_effect=lambda key: None)
        worker.log_error = Mock()
        
        assert worker.validate_params() is False
        worker.log_error.assert_called()

    def test_validate_params_fails_without_url(self):
        """Test validation fails when URL not in alert config or global settings."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test message',
            'priority': '5',
            'url': None,
            'token': 'test_token',
        }.get(key))
        
        worker.get_global_setting = Mock(side_effect=lambda key: {
            'gotify_url': None,
            'gotify_token': 'test_token',
        }.get(key))
        
        worker.log_error = Mock()
        
        assert worker.validate_params() is False
        assert 'URL' in str(worker.log_error.call_args)

    def test_validate_params_fails_without_token(self):
        """Test validation fails when token not in alert config or global settings."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test message',
            'priority': '5',
            'url': 'https://gotify.example.com',
            'token': None,
        }.get(key))
        
        worker.get_global_setting = Mock(side_effect=lambda key: {
            'gotify_url': 'https://gotify.example.com',
            'gotify_token': None,
        }.get(key))
        
        worker.log_error = Mock()
        
        assert worker.validate_params() is False
        assert 'token' in str(worker.log_error.call_args)

    @patch('alert_gotify.modalert_alert_gotify_helper.process_event')
    def test_process_event_success(self, mock_process_event):
        """Test successful event processing."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        # Mock validation to succeed
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test',
            'priority': '5',
            'url': 'https://gotify.example.com',
            'token': 'test_token',
        }.get(key))
        worker.get_global_setting = Mock(return_value=None)
        worker.log_error = Mock()
        
        # Mock helper to return success
        mock_process_event.return_value = 0
        
        result = worker.process_event()
        
        assert result == 0
        mock_process_event.assert_called_once()

    @patch('alert_gotify.modalert_alert_gotify_helper.process_event')
    def test_process_event_validation_failure(self, mock_process_event):
        """Test event processing with validation failure."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        # Mock validation to fail
        worker.get_param = Mock(side_effect=lambda key: {
            'message': None,  # Missing required field
            'priority': '5',
        }.get(key))
        worker.get_global_setting = Mock(return_value=None)
        worker.log_error = Mock()
        
        result = worker.process_event()
        
        assert result == 3
        mock_process_event.assert_not_called()

    @patch('alert_gotify.modalert_alert_gotify_helper.process_event')
    def test_process_event_attribute_error(self, mock_process_event):
        """Test event processing with AttributeError."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test',
            'priority': '5',
            'url': 'https://gotify.example.com',
            'token': 'test_token',
        }.get(key))
        worker.get_global_setting = Mock(return_value=None)
        worker.log_error = Mock()
        
        mock_process_event.side_effect = AttributeError("Test error")
        
        result = worker.process_event()
        
        assert result == 4
        worker.log_error.assert_called()

    @patch('alert_gotify.modalert_alert_gotify_helper.process_event')
    def test_process_event_generic_exception(self, mock_process_event):
        """Test event processing with generic exception."""
        worker = AlertActionWorkeralert_gotify("alert_gotify", "alert_gotify")
        
        worker.get_param = Mock(side_effect=lambda key: {
            'message': 'Test',
            'priority': '5',
            'url': 'https://gotify.example.com',
            'token': 'test_token',
        }.get(key))
        worker.get_global_setting = Mock(return_value=None)
        worker.log_error = Mock()
        
        mock_process_event.side_effect = Exception("Generic error")
        
        result = worker.process_event()
        
        assert result == 5
        worker.log_error.assert_called()
