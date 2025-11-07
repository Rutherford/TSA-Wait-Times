"""
TSA Wait Times Twitter Bot

This module scrapes TSA wait times from ATL Airport and posts them to Twitter.
It provides automatic monitoring and reporting of checkpoint wait times.

Author: TSA-Wait-Times Project
License: MIT
"""

import os
import sys
import json
import time
import signal
import logging
from typing import Dict, Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from tweepy import Client, TweepyException

# Load environment variables
load_dotenv()

# Configuration Constants
ATL_WAIT_TIMES_URL = "https://www.atl.com/times/"
SCRAPE_INTERVAL_MINUTES = 30
REQUEST_TIMEOUT_SECONDS = 10
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2

# Wait time thresholds for emoji color coding (in minutes)
WAIT_TIME_THRESHOLDS = {
    'green': 15,
    'yellow': 30,
    'orange': 45,
    'purple': 60
}

# Configure logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'tsa_bot.log'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Global flag for graceful shutdown
shutdown_requested = False


def setup_logging() -> logging.Logger:
    """
    Configure logging with both file and console handlers.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('TSAWaitTimesBot')
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    shutdown_requested = True


def get_requests_session() -> requests.Session:
    """
    Create a requests session with retry logic and timeout settings.

    Returns:
        Configured requests Session object
    """
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def validate_environment_variables() -> bool:
    """
    Validate that all required environment variables are set.

    Returns:
        True if all required variables are set, False otherwise
    """
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please ensure all variables are set in your .env file")
        return False

    return True


def download_html(url: str, session: requests.Session) -> Optional[str]:
    """
    Downloads the HTML content of a given URL with proper error handling.

    Args:
        url: The URL to download HTML from
        session: Configured requests session with retry logic

    Returns:
        The HTML content as a string, or None if an error occurs
    """
    try:
        logger.info(f"Downloading HTML from {url}")
        response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            logger.error(f"Response content type is not HTML: {content_type}")
            return None

        logger.info("Successfully downloaded HTML")
        return response.text

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {REQUEST_TIMEOUT_SECONDS} seconds")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred during request: {e}")
        return None


def get_wait_times(html: str) -> Dict[str, int]:
    """
    Parse HTML and extract TSA wait times for domestic checkpoints.

    Args:
        html: HTML content to parse

    Returns:
        Dictionary mapping checkpoint names to wait times in minutes
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Find the DOMESTIC terminal section
        domestic_h1 = soup.find('h1', string=lambda text: 'domestic' in text.lower() if text else False)

        if domestic_h1 is None:
            logger.warning("Failed to find DOMESTIC heading in HTML")
            return {}

        domestic_div = domestic_h1.parent.parent

        # Extract checkpoint names and wait times
        # Note: CSS class appears to be '.lomestic' (possibly a typo in the website's HTML)
        checkpoint_elements = domestic_div.select('.lomestic > h2')
        time_elements = domestic_div.select('.lomestic.float-right > .declasser3 > button > span')

        if not checkpoint_elements or not time_elements:
            logger.warning("No checkpoint or time elements found")
            return {}

        if len(checkpoint_elements) != len(time_elements):
            logger.warning(
                f"Mismatch between checkpoint count ({len(checkpoint_elements)}) "
                f"and time count ({len(time_elements)})"
            )

        checkpoint_names = [elem.get_text(strip=True) for elem in checkpoint_elements]
        wait_times_str = [elem.get_text(strip=True) for elem in time_elements]

        # Convert wait times to integers and create dictionary
        wait_times = {}
        for name, time_str in zip(checkpoint_names, wait_times_str):
            try:
                wait_times[name] = int(time_str)
            except ValueError:
                logger.warning(f"Could not convert wait time '{time_str}' to integer for {name}")
                continue

        logger.info(f"Successfully extracted wait times for {len(wait_times)} checkpoints")
        return wait_times

    except Exception as e:
        logger.error(f"Error parsing HTML: {e}", exc_info=True)
        return {}


def format_tweet(wait_times: Dict[str, int]) -> str:
    """
    Format wait times into a Twitter-friendly message with emojis.

    Args:
        wait_times: Dictionary mapping checkpoint names to wait times in minutes

    Returns:
        Formatted tweet string with timestamp and emoji-coded wait times
    """
    if not wait_times:
        logger.warning("No wait times to format")
        return "TSA wait times currently unavailable. Please check https://www.atl.com/times/"

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    tweet = f"Current TSA wait times (as of {timestamp}):\n\n"

    for checkpoint, wait_time in wait_times.items():
        # Determine emoji based on wait time thresholds
        if wait_time <= WAIT_TIME_THRESHOLDS['green']:
            emoji = "🟢"  # Green
        elif wait_time <= WAIT_TIME_THRESHOLDS['yellow']:
            emoji = "🟡"  # Yellow
        elif wait_time <= WAIT_TIME_THRESHOLDS['orange']:
            emoji = "🟠"  # Orange
        elif wait_time <= WAIT_TIME_THRESHOLDS['purple']:
            emoji = "🟣"  # Purple
        else:
            emoji = "🔴"  # Red

        # Clean up checkpoint name
        checkpoint_name = (
            checkpoint
            .replace("CHECKPOINT", "")
            .replace("PRECHECK ONLY", "(Pre-Check Only)")
            .strip()
            .title()
        )

        tweet += f"{emoji} {checkpoint_name}: {wait_time} min\n"

    logger.debug(f"Formatted tweet: {tweet}")
    return tweet


def send_tweet(tweet_text: str, twitter_client: Client) -> bool:
    """
    Send a tweet using the Twitter API v2 with proper authentication.

    Args:
        tweet_text: The text content to tweet
        twitter_client: Authenticated Tweepy client

    Returns:
        True if tweet was sent successfully, False otherwise
    """
    try:
        if not tweet_text or len(tweet_text.strip()) == 0:
            logger.error("Cannot send empty tweet")
            return False

        if len(tweet_text) > 280:
            logger.warning(f"Tweet length ({len(tweet_text)}) exceeds 280 characters")
            # Truncate if necessary
            tweet_text = tweet_text[:277] + "..."

        logger.info("Sending tweet to Twitter API")
        response = twitter_client.create_tweet(text=tweet_text)

        if response and response.data:
            tweet_id = response.data.get('id')
            logger.info(f"Tweet sent successfully! Tweet ID: {tweet_id}")
            return True
        else:
            logger.error("Tweet response did not contain expected data")
            return False

    except TweepyException as e:
        logger.error(f"Tweepy error sending tweet: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending tweet: {e}", exc_info=True)
        return False


def initialize_twitter_client() -> Optional[Client]:
    """
    Initialize and return an authenticated Twitter API client.

    Returns:
        Authenticated Tweepy Client, or None if initialization fails
    """
    try:
        client = Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        logger.info("Twitter client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Twitter client: {e}", exc_info=True)
        return None


def health_check() -> bool:
    """
    Perform a basic health check of the bot's dependencies.

    Returns:
        True if all health checks pass, False otherwise
    """
    logger.info("Performing health check...")

    # Check environment variables
    if not validate_environment_variables():
        return False

    # Check network connectivity
    try:
        session = get_requests_session()
        response = session.get("https://www.google.com", timeout=5)
        response.raise_for_status()
        logger.info("Network connectivity check passed")
    except Exception as e:
        logger.error(f"Network connectivity check failed: {e}")
        return False

    logger.info("Health check passed")
    return True


def run_bot():
    """
    Main bot loop: scrape wait times and post to Twitter at regular intervals.
    """
    global shutdown_requested

    logger.info("Starting TSA Wait Times Twitter Bot")

    # Perform initial health check
    if not health_check():
        logger.error("Health check failed. Exiting.")
        sys.exit(1)

    # Initialize Twitter client
    twitter_client = initialize_twitter_client()
    if not twitter_client:
        logger.error("Failed to initialize Twitter client. Exiting.")
        sys.exit(1)

    # Initialize requests session
    session = get_requests_session()

    logger.info(f"Bot configured to check wait times every {SCRAPE_INTERVAL_MINUTES} minutes")

    iteration = 0

    while not shutdown_requested:
        iteration += 1
        logger.info(f"Starting iteration {iteration}")

        try:
            # Download HTML
            html = download_html(ATL_WAIT_TIMES_URL, session)

            if html is None:
                logger.error("Failed to download HTML. Skipping this iteration.")
            else:
                # Parse wait times
                wait_times = get_wait_times(html)

                if not wait_times:
                    logger.warning("No wait times retrieved. Skipping tweet.")
                else:
                    logger.info(f"Retrieved wait times: {wait_times}")

                    # Format tweet
                    tweet = format_tweet(wait_times)
                    logger.info(f"Formatted tweet:\n{tweet}")

                    # Send tweet
                    success = send_tweet(tweet, twitter_client)

                    if success:
                        logger.info("Iteration completed successfully")
                    else:
                        logger.error("Failed to send tweet")

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

        # Sleep until next iteration (with periodic checks for shutdown signal)
        logger.info(f"Sleeping for {SCRAPE_INTERVAL_MINUTES} minutes until next check")

        sleep_duration = SCRAPE_INTERVAL_MINUTES * 60
        sleep_interval = 10  # Check for shutdown every 10 seconds

        for _ in range(0, sleep_duration, sleep_interval):
            if shutdown_requested:
                break
            time.sleep(min(sleep_interval, sleep_duration))

    logger.info("Bot shutdown completed gracefully")


def main():
    """
    Entry point for the TSA Wait Times Twitter Bot.
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        run_bot()
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
