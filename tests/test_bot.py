"""
Unit tests for TSA Wait Times Twitter Bot
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time2wait


class TestFormatTweet:
    """Tests for format_tweet function"""

    def test_format_tweet_with_valid_data(self):
        """Test formatting tweet with valid wait times"""
        wait_times = {
            "NORTH CHECKPOINT": 10,
            "SOUTH CHECKPOINT": 25,
            "PRECHECK ONLY": 5
        }

        result = time2wait.format_tweet(wait_times)

        assert "Current TSA wait times" in result
        assert "North" in result
        assert "South" in result
        assert "10 min" in result
        assert "25 min" in result
        assert "🟢" in result  # Green emoji for 10 min
        assert "🟡" in result  # Yellow emoji for 25 min

    def test_format_tweet_empty_dict(self):
        """Test formatting tweet with empty wait times"""
        wait_times = {}

        result = time2wait.format_tweet(wait_times)

        assert "currently unavailable" in result
        assert "https://www.atl.com/times/" in result

    def test_format_tweet_emoji_thresholds(self):
        """Test that correct emojis are used for different wait times"""
        test_cases = [
            (10, "🟢"),   # Green
            (20, "🟡"),   # Yellow
            (40, "🟠"),   # Orange
            (55, "🟣"),   # Purple
            (70, "🔴"),   # Red
        ]

        for wait_time, expected_emoji in test_cases:
            wait_times = {"TEST CHECKPOINT": wait_time}
            result = time2wait.format_tweet(wait_times)
            assert expected_emoji in result

    def test_format_tweet_name_formatting(self):
        """Test that checkpoint names are properly formatted"""
        wait_times = {
            "NORTH CHECKPOINT": 15,
            "PRECHECK ONLY": 10
        }

        result = time2wait.format_tweet(wait_times)

        assert "North:" in result
        assert "(Pre-Check Only)" in result
        assert "CHECKPOINT" not in result


class TestGetWaitTimes:
    """Tests for get_wait_times function"""

    def test_get_wait_times_valid_html(self):
        """Test parsing valid HTML"""
        html = """
        <html>
            <h1>DOMESTIC Terminal</h1>
            <div>
                <div class="lomestic"><h2>NORTH CHECKPOINT</h2></div>
                <div class="lomestic float-right">
                    <div class="declasser3">
                        <button><span>15</span></button>
                    </div>
                </div>
            </div>
        </html>
        """

        result = time2wait.get_wait_times(html)

        assert isinstance(result, dict)
        assert "NORTH CHECKPOINT" in result
        assert result["NORTH CHECKPOINT"] == 15

    def test_get_wait_times_no_domestic_heading(self):
        """Test parsing HTML without DOMESTIC heading"""
        html = "<html><body>No relevant content</body></html>"

        result = time2wait.get_wait_times(html)

        assert result == {}

    def test_get_wait_times_invalid_html(self):
        """Test parsing invalid HTML"""
        html = "Not valid HTML at all!"

        result = time2wait.get_wait_times(html)

        assert isinstance(result, dict)

    def test_get_wait_times_mismatched_counts(self):
        """Test when checkpoint count doesn't match time count"""
        html = """
        <html>
            <h1>DOMESTIC Terminal</h1>
            <div>
                <div class="lomestic"><h2>NORTH CHECKPOINT</h2></div>
                <div class="lomestic"><h2>SOUTH CHECKPOINT</h2></div>
                <div class="lomestic float-right">
                    <div class="declasser3">
                        <button><span>15</span></button>
                    </div>
                </div>
            </div>
        </html>
        """

        result = time2wait.get_wait_times(html)

        # Should still parse what it can
        assert isinstance(result, dict)


class TestDownloadHtml:
    """Tests for download_html function"""

    @patch('time2wait.requests.Session')
    def test_download_html_success(self, mock_session_class):
        """Test successful HTML download"""
        # Setup mock
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.headers.get.return_value = "text/html"
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        result = time2wait.download_html("https://example.com", mock_session)

        assert result == "<html>Test</html>"
        mock_session.get.assert_called_once()

    @patch('time2wait.requests.Session')
    def test_download_html_timeout(self, mock_session_class):
        """Test timeout handling"""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Timeout")

        result = time2wait.download_html("https://example.com", mock_session)

        assert result is None

    @patch('time2wait.requests.Session')
    def test_download_html_non_html_response(self, mock_session_class):
        """Test non-HTML response handling"""
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.headers.get.return_value = "application/json"
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        result = time2wait.download_html("https://example.com", mock_session)

        assert result is None


class TestSendTweet:
    """Tests for send_tweet function"""

    @patch('time2wait.Client')
    def test_send_tweet_success(self, mock_client_class):
        """Test successful tweet sending"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = {'id': '123456'}
        mock_client.create_tweet.return_value = mock_response

        result = time2wait.send_tweet("Test tweet", mock_client)

        assert result is True
        mock_client.create_tweet.assert_called_once()

    @patch('time2wait.Client')
    def test_send_tweet_empty_text(self, mock_client_class):
        """Test sending empty tweet"""
        mock_client = Mock()

        result = time2wait.send_tweet("", mock_client)

        assert result is False
        mock_client.create_tweet.assert_not_called()

    @patch('time2wait.Client')
    def test_send_tweet_too_long(self, mock_client_class):
        """Test tweet truncation for long messages"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = {'id': '123456'}
        mock_client.create_tweet.return_value = mock_response

        long_tweet = "A" * 300  # Exceeds 280 character limit
        result = time2wait.send_tweet(long_tweet, mock_client)

        # Should still succeed after truncation
        assert result is True
        call_args = mock_client.create_tweet.call_args
        assert len(call_args[1]['text']) <= 280

    @patch('time2wait.Client')
    def test_send_tweet_api_error(self, mock_client_class):
        """Test handling of API errors"""
        mock_client = Mock()
        mock_client.create_tweet.side_effect = Exception("API Error")

        result = time2wait.send_tweet("Test tweet", mock_client)

        assert result is False


class TestValidateEnvironmentVariables:
    """Tests for validate_environment_variables function"""

    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret'
    })
    def test_validate_all_present(self):
        """Test validation when all variables are present"""
        result = time2wait.validate_environment_variables()
        assert result is True

    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        # Missing other required variables
    }, clear=True)
    def test_validate_missing_variables(self):
        """Test validation when variables are missing"""
        result = time2wait.validate_environment_variables()
        assert result is False


class TestHealthCheck:
    """Tests for health_check function"""

    @patch('time2wait.validate_environment_variables')
    @patch('time2wait.get_requests_session')
    def test_health_check_success(self, mock_session, mock_validate):
        """Test successful health check"""
        mock_validate.return_value = True
        mock_sess = MagicMock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_sess.get.return_value = mock_response
        mock_session.return_value = mock_sess

        result = time2wait.health_check()

        assert result is True

    @patch('time2wait.validate_environment_variables')
    def test_health_check_env_fail(self, mock_validate):
        """Test health check with invalid environment"""
        mock_validate.return_value = False

        result = time2wait.health_check()

        assert result is False


class TestGetRequestsSession:
    """Tests for get_requests_session function"""

    def test_session_creation(self):
        """Test that session is created with retry logic"""
        session = time2wait.get_requests_session()

        assert session is not None
        # Verify adapters are mounted
        assert 'https://' in session.adapters
        assert 'http://' in session.adapters


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
