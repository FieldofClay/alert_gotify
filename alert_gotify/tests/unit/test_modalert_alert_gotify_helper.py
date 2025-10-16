# encoding = utf-8
"""
Unit tests for modalert_alert_gotify_helper module.
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "package", "bin"))
from alert_gotify import modalert_alert_gotify_helper


@pytest.mark.unit
class TestHelperStructure:
    """Test helper module structure and basic imports."""

    def test_helper_file_exists(self):
        """Test that the helper file exists."""
        helper_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "package", "bin", "alert_gotify", 
            "modalert_alert_gotify_helper.py"
        )
        assert os.path.exists(helper_path)

    def test_helper_has_process_event_function(self):
        """Test that helper defines process_event."""
        helper_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "package", "bin", "alert_gotify", 
            "modalert_alert_gotify_helper.py"
        )
        with open(helper_path, 'r') as f:
            content = f.read()
        assert 'def process_event' in content
        assert 'requests' in content  # Uses requests library


@pytest.mark.unit
class TestProcessEvent:
    """Test the process_event function."""

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_successful_message_with_global_settings(self, mock_post, mock_helper):
        """Test sending a message using global settings."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call the function
        result = modalert_alert_gotify_helper.process_event(mock_helper)

        # Verify the result
        assert result == 0
        
        # Verify requests.post was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL construction
        assert call_args[0][0] == 'https://gotify.example.com/message'
        
        # Check headers
        headers = call_args[1]['headers']
        assert headers['X-Gotify-Key'] == 'test_global_token'
        assert headers['Content-Type'] == 'application/json'
        
        # Check payload
        payload = call_args[1]['json']
        assert payload['message'] == 'Test message'
        assert payload['title'] == 'Test title'
        assert payload['priority'] == 5
        
        # Check SSL verify
        assert call_args[1]['verify'] is True
        
        # Verify logging
        mock_helper.log_info.assert_called()

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_successful_message_with_overrides(self, mock_post, mock_helper_with_overrides):
        """Test sending a message with URL/token overrides."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call the function
        result = modalert_alert_gotify_helper.process_event(mock_helper_with_overrides)

        # Verify the result
        assert result == 0
        
        # Verify requests.post was called with override values
        call_args = mock_post.call_args
        
        # Check URL uses override
        assert call_args[0][0] == 'https://custom.gotify.local/message'
        
        # Check token uses override
        headers = call_args[1]['headers']
        assert headers['X-Gotify-Key'] == 'custom_token_123'
        
        # Check SSL verify disabled
        assert call_args[1]['verify'] is False
        
        # Verify global settings were NOT called
        mock_helper_with_overrides.get_global_setting.assert_not_called()

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_message_without_title(self, mock_post, mock_helper):
        """Test sending a message without a title."""
        # Remove title from params
        mock_helper.get_param = Mock(side_effect=lambda key: {
            'url': None,
            'token': None,
            'message': 'Test message without title',
            'title': None,
            'priority': '5',
            'ssl_verify': None,
        }.get(key))
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = modalert_alert_gotify_helper.process_event(mock_helper)

        assert result == 0
        
        # Check payload doesn't include title
        payload = mock_post.call_args[1]['json']
        assert 'title' not in payload or payload.get('title') is None
        assert payload['message'] == 'Test message without title'

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_different_priority_levels(self, mock_post, mock_helper):
        """Test sending messages with different priority levels."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        for priority in ['0', '5', '10']:
            mock_helper.get_param = Mock(side_effect=lambda key, p=priority: {
                'url': None,
                'token': None,
                'message': f'Priority {p} message',
                'title': 'Test',
                'priority': p,
                'ssl_verify': None,
            }.get(key))
            
            result = modalert_alert_gotify_helper.process_event(mock_helper)
            assert result == 0
            
            payload = mock_post.call_args[1]['json']
            assert payload['priority'] == int(priority)

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_url_trailing_slash_handling(self, mock_post, mock_helper):
        """Test that URLs with trailing slashes are handled correctly."""
        # Set URL with trailing slash
        mock_helper.get_param = Mock(side_effect=lambda key: {
            'url': 'https://gotify.example.com/',
            'token': 'test_token',
            'message': 'Test',
            'title': None,
            'priority': '5',
            'ssl_verify': None,
        }.get(key))
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = modalert_alert_gotify_helper.process_event(mock_helper)

        # Should not have double slashes
        assert mock_post.call_args[0][0] == 'https://gotify.example.com/message'

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_failed_request_non_200(self, mock_post, mock_helper):
        """Test handling of non-200 response codes."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response

        result = modalert_alert_gotify_helper.process_event(mock_helper)

        assert result == 1
        mock_helper.log_error.assert_called()

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_ssl_error_handling(self, mock_post, mock_helper):
        """Test handling of SSL errors."""
        import requests
        mock_post.side_effect = requests.exceptions.SSLError('SSL verification failed')

        result = modalert_alert_gotify_helper.process_event(mock_helper)

        assert result == 1
        # Verify error logging mentions SSL
        error_calls = [str(call) for call in mock_helper.log_error.call_args_list]
        assert any('SSL' in str(call) for call in error_calls)

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_request_exception_handling(self, mock_post, mock_helper):
        """Test handling of general request exceptions."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException('Connection error')

        result = modalert_alert_gotify_helper.process_event(mock_helper)

        assert result == 1
        mock_helper.log_error.assert_called()

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_unexpected_exception_handling(self, mock_post, mock_helper):
        """Test handling of unexpected exceptions."""
        mock_post.side_effect = Exception('Unexpected error')

        result = modalert_alert_gotify_helper.process_event(mock_helper)

        assert result == 1
        mock_helper.log_error.assert_called()


@pytest.mark.unit
class TestSSLVerification:
    """Test SSL verification parameter handling."""

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_ssl_verify_default_true(self, mock_post, mock_helper):
        """Test that SSL verification defaults to True."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        modalert_alert_gotify_helper.process_event(mock_helper)

        assert mock_post.call_args[1]['verify'] is True

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_ssl_verify_string_zero(self, mock_post, mock_helper):
        """Test SSL verification with string '0'."""
        mock_helper.get_param = Mock(side_effect=lambda key: {
            'url': None,
            'token': None,
            'message': 'Test',
            'title': None,
            'priority': '5',
            'ssl_verify': '0',
        }.get(key))
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        modalert_alert_gotify_helper.process_event(mock_helper)

        assert mock_post.call_args[1]['verify'] is False

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_ssl_verify_string_one(self, mock_post, mock_helper):
        """Test SSL verification with string '1'."""
        mock_helper.get_param = Mock(side_effect=lambda key: {
            'url': None,
            'token': None,
            'message': 'Test',
            'title': None,
            'priority': '5',
            'ssl_verify': '1',
        }.get(key))
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        modalert_alert_gotify_helper.process_event(mock_helper)

        assert mock_post.call_args[1]['verify'] is True

    @patch('alert_gotify.modalert_alert_gotify_helper.requests.post')
    def test_ssl_verify_various_false_strings(self, mock_post, mock_helper):
        """Test SSL verification with various false-like strings."""
        for false_value in ['0', 'false', 'False', 'FALSE', 'no', 'No', 'NO']:
            mock_helper.get_param = Mock(side_effect=lambda key, fv=false_value: {
                'url': None,
                'token': None,
                'message': 'Test',
                'title': None,
                'priority': '5',
                'ssl_verify': fv,
            }.get(key))
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            modalert_alert_gotify_helper.process_event(mock_helper)

            assert mock_post.call_args[1]['verify'] is False, f"Failed for value: {false_value}"
