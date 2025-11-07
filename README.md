# TSA Wait Times Twitter Bot

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An automated Twitter bot that monitors and posts live TSA checkpoint wait times at Hartsfield-Jackson Atlanta International Airport (ATL).

## Features

- 🔄 **Automated Monitoring**: Scrapes TSA wait times every 30 minutes
- 🐦 **Twitter Integration**: Posts updates using Twitter API v2
- 🎨 **Visual Indicators**: Color-coded emojis based on wait times
  - 🟢 Green: ≤ 15 minutes
  - 🟡 Yellow: 16-30 minutes
  - 🟠 Orange: 31-45 minutes
  - 🟣 Purple: 46-60 minutes
  - 🔴 Red: > 60 minutes
- 🔒 **Secure**: Environment-based credential management
- 📊 **Logging**: Comprehensive logging with rotation
- 🛡️ **Resilient**: Automatic retry logic and error handling
- 🚦 **Health Checks**: Built-in health monitoring
- ⚡ **Graceful Shutdown**: Proper signal handling

## Prerequisites

- Python 3.8 or higher
- Twitter Developer Account with API access
- Twitter API credentials (API Key, API Secret, Access Token, Access Token Secret)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rutherford/TSA-Wait-Times.git
cd TSA-Wait-Times
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file and add your Twitter API credentials:

```env
TWITTER_API_KEY=your_actual_api_key
TWITTER_API_SECRET=your_actual_api_secret
TWITTER_ACCESS_TOKEN=your_actual_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret
```

## Usage

### Run the Bot

```bash
python time2wait.py
```

### Run with Docker

```bash
docker build -t tsa-wait-times-bot .
docker run -d --name tsa-bot --env-file .env tsa-wait-times-bot
```

### Run as a System Service (Linux)

```bash
sudo cp tsa-bot.service /etc/systemd/system/
sudo systemctl enable tsa-bot
sudo systemctl start tsa-bot
sudo systemctl status tsa-bot
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TWITTER_API_KEY` | Yes | - | Twitter API Consumer Key |
| `TWITTER_API_SECRET` | Yes | - | Twitter API Consumer Secret |
| `TWITTER_ACCESS_TOKEN` | Yes | - | Twitter Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Yes | - | Twitter Access Token Secret |
| `SCRAPE_INTERVAL_MINUTES` | No | 30 | Minutes between updates |
| `REQUEST_TIMEOUT_SECONDS` | No | 10 | HTTP request timeout |
| `MAX_RETRIES` | No | 3 | Max retry attempts for failed requests |

### Logging

Logs are written to:
- **Console**: INFO level and above
- **File**: `tsa_bot.log` (DEBUG level, rotated at 10MB, 5 backups)

## Project Structure

```
TSA-Wait-Times/
├── time2wait.py          # Main bot application
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── Dockerfile           # Docker container configuration
├── tsa-bot.service      # Systemd service file
├── tests/               # Unit tests
│   ├── __init__.py
│   ├── test_bot.py
│   └── test_scraping.py
└── docs/                # Additional documentation
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=time2wait tests/

# Run specific test file
pytest tests/test_bot.py -v
```

### Code Quality

```bash
# Format code
black time2wait.py

# Lint code
pylint time2wait.py

# Type checking
mypy time2wait.py
```

## Troubleshooting

### Bot Won't Start

1. **Check credentials**: Ensure all Twitter API credentials are correctly set in `.env`
2. **Check permissions**: Verify your Twitter app has read/write permissions
3. **Check logs**: Review `tsa_bot.log` for detailed error messages

### Network Issues

- The bot includes automatic retry logic with exponential backoff
- Check your internet connection
- Verify the ATL website is accessible: https://www.atl.com/times/

### Twitter API Errors

- **Rate Limits**: The bot respects Twitter's rate limits
- **Authentication**: Ensure your credentials are valid and not expired
- **Permissions**: Your Twitter app needs read/write access

## Security Best Practices

⚠️ **Never commit your `.env` file to version control**

- Always use `.env` for sensitive credentials
- Rotate your API keys periodically
- Use environment-specific credentials for development/production
- Review Twitter API logs regularly for unusual activity

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TSA wait times data provided by [Hartsfield-Jackson Atlanta International Airport](https://www.atl.com/)
- Twitter API integration via [Tweepy](https://www.tweepy.org/)

## Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/Rutherford/TSA-Wait-Times/issues)
- Check existing [Discussions](https://github.com/Rutherford/TSA-Wait-Times/discussions)

## Changelog

### Version 2.0.0 (Latest)
- ✅ Complete rewrite with production-grade architecture
- ✅ Removed hardcoded credentials (now uses environment variables)
- ✅ Added comprehensive error handling and retry logic
- ✅ Implemented proper logging with rotation
- ✅ Added graceful shutdown handling
- ✅ Switched to Tweepy for Twitter API integration
- ✅ Added health checks and monitoring
- ✅ Removed unused OpenAI dependency
- ✅ Added Docker and systemd support
- ✅ Comprehensive documentation and tests

### Version 1.0.0
- Initial release with basic functionality
