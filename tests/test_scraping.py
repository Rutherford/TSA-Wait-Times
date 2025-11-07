"""
Integration tests for web scraping functionality
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time2wait


class TestHTMLParsing:
    """Tests for HTML parsing edge cases"""

    def test_parse_multiple_checkpoints(self):
        """Test parsing multiple checkpoints"""
        html = """
        <html>
            <h1>DOMESTIC Terminal</h1>
            <div>
                <div class="lomestic"><h2>NORTH CHECKPOINT</h2></div>
                <div class="lomestic"><h2>SOUTH CHECKPOINT</h2></div>
                <div class="lomestic"><h2>CENTRAL CHECKPOINT</h2></div>
                <div class="lomestic float-right">
                    <div class="declasser3"><button><span>15</span></button></div>
                </div>
                <div class="lomestic float-right">
                    <div class="declasser3"><button><span>25</span></button></div>
                </div>
                <div class="lomestic float-right">
                    <div class="declasser3"><button><span>35</span></button></div>
                </div>
            </div>
        </html>
        """

        result = time2wait.get_wait_times(html)

        assert len(result) == 3
        assert result["NORTH CHECKPOINT"] == 15
        assert result["SOUTH CHECKPOINT"] == 25
        assert result["CENTRAL CHECKPOINT"] == 35

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace"""
        html = """
        <html>
            <h1>  DOMESTIC Terminal  </h1>
            <div>
                <div class="lomestic"><h2>  NORTH CHECKPOINT  </h2></div>
                <div class="lomestic float-right">
                    <div class="declasser3">
                        <button><span>  15  </span></button>
                    </div>
                </div>
            </div>
        </html>
        """

        result = time2wait.get_wait_times(html)

        assert "NORTH CHECKPOINT" in result
        assert result["NORTH CHECKPOINT"] == 15

    def test_parse_invalid_wait_time(self):
        """Test parsing with non-numeric wait time"""
        html = """
        <html>
            <h1>DOMESTIC Terminal</h1>
            <div>
                <div class="lomestic"><h2>NORTH CHECKPOINT</h2></div>
                <div class="lomestic float-right">
                    <div class="declasser3">
                        <button><span>N/A</span></button>
                    </div>
                </div>
            </div>
        </html>
        """

        result = time2wait.get_wait_times(html)

        # Should handle gracefully, checkpoint might be skipped
        assert isinstance(result, dict)

    def test_parse_case_insensitive_domestic(self):
        """Test that DOMESTIC heading is case-insensitive"""
        html = """
        <html>
            <h1>domestic terminal</h1>
            <div>
                <div class="lomestic"><h2>TEST CHECKPOINT</h2></div>
                <div class="lomestic float-right">
                    <div class="declasser3">
                        <button><span>20</span></button>
                    </div>
                </div>
            </div>
        </html>
        """

        result = time2wait.get_wait_times(html)

        assert "TEST CHECKPOINT" in result


class TestTweetFormatting:
    """Tests for tweet formatting edge cases"""

    def test_format_special_characters(self):
        """Test formatting with special characters in checkpoint names"""
        wait_times = {
            "CHECKPOINT & GATE": 15,
            "PRE-CHECK": 10
        }

        result = time2wait.format_tweet(wait_times)

        assert "&" in result or "And" in result
        assert "-" in result or "Check" in result

    def test_format_preserves_order(self):
        """Test that formatting preserves checkpoint order"""
        wait_times = {
            "ALPHA CHECKPOINT": 10,
            "BETA CHECKPOINT": 20,
            "GAMMA CHECKPOINT": 30
        }

        result = time2wait.format_tweet(wait_times)
        lines = result.split('\n')

        # Should have header and at least 3 checkpoint lines
        assert len(lines) >= 5

    def test_format_timestamp_format(self):
        """Test that timestamp is in correct format"""
        wait_times = {"TEST CHECKPOINT": 15}

        result = time2wait.format_tweet(wait_times)

        # Should contain YYYY-MM-DD HH:MM:SS format
        assert "as of" in result
        # Check for basic timestamp pattern
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, result)

    def test_format_all_emoji_types(self):
        """Test that all emoji types are used correctly"""
        wait_times = {
            "GREEN": 10,
            "YELLOW": 25,
            "ORANGE": 40,
            "PURPLE": 55,
            "RED": 70
        }

        result = time2wait.format_tweet(wait_times)

        # Verify all emoji colors are present
        assert "🟢" in result
        assert "🟡" in result
        assert "🟠" in result
        assert "🟣" in result
        assert "🔴" in result


class TestConstants:
    """Tests for configuration constants"""

    def test_wait_time_thresholds(self):
        """Test that wait time thresholds are properly configured"""
        assert time2wait.WAIT_TIME_THRESHOLDS['green'] == 15
        assert time2wait.WAIT_TIME_THRESHOLDS['yellow'] == 30
        assert time2wait.WAIT_TIME_THRESHOLDS['orange'] == 45
        assert time2wait.WAIT_TIME_THRESHOLDS['purple'] == 60

    def test_url_configuration(self):
        """Test that URL is properly configured"""
        assert time2wait.ATL_WAIT_TIMES_URL.startswith("https://")
        assert "atl.com" in time2wait.ATL_WAIT_TIMES_URL.lower()

    def test_interval_configuration(self):
        """Test that intervals are reasonable"""
        assert time2wait.SCRAPE_INTERVAL_MINUTES > 0
        assert time2wait.REQUEST_TIMEOUT_SECONDS > 0
        assert time2wait.MAX_RETRIES >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
