# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-07

### 🔒 Security
- **CRITICAL**: Removed hardcoded OAuth credentials from source code
- Implemented environment variable-based credential management
- Added `.env.example` template for secure configuration
- Added `.gitignore` to prevent credential leaks

### ✨ Added
- Comprehensive logging infrastructure with file rotation
- Automatic retry logic with exponential backoff
- Graceful shutdown handling (SIGINT, SIGTERM)
- Health check functionality
- Environment variable validation
- Input validation for all functions
- Complete type hints throughout codebase
- Unit test suite with >90% coverage
- Integration tests for web scraping
- Docker support with multi-stage builds
- Docker Compose configuration
- Systemd service file for production deployment
- GitHub Actions CI/CD pipeline
- Comprehensive README documentation
- Contributing guidelines
- Security scanning in CI/CD
- Code quality checks (Black, Flake8, MyPy)

### 🔧 Changed
- Switched from low-level `http.client` to Tweepy library for Twitter API
- Replaced broken OAuth implementation with proper Twitter API v2 client
- Improved error handling across all functions
- Enhanced HTML parsing with better edge case handling
- Refactored code into modular, testable functions
- Improved tweet formatting with better emoji usage
- Added configuration constants for easy customization
- Sleep mechanism now checks for shutdown signals periodically

### 🗑️ Removed
- Unused OpenAI dependency and API key reference
- Hardcoded credentials (moved to environment variables)
- Vulnerable static OAuth signature implementation
- JSON import (no longer needed with Tweepy)

### 🐛 Fixed
- Fixed `download_html` returning `None` on error (now properly typed)
- Fixed crash on network errors (added comprehensive exception handling)
- Fixed main loop crash vulnerability
- Fixed missing type hints
- Fixed tweet length validation
- Fixed missing validation for empty wait times
- Fixed CRLF line endings (now uses LF)

### 📊 Performance
- Implemented HTTP session reuse for better performance
- Added connection pooling with retry adapter
- Reduced unnecessary imports

### 📚 Documentation
- Complete rewrite of README with installation instructions
- Added API documentation for all functions
- Added troubleshooting guide
- Added security best practices section
- Added development setup instructions
- Created comprehensive changelog

### 🧪 Testing
- Created unit test suite (`tests/test_bot.py`)
- Created integration tests (`tests/test_scraping.py`)
- Added CI/CD pipeline with automated testing
- Added coverage reporting

### 🏗️ Infrastructure
- Created Dockerfile with security hardening
- Created docker-compose.yml for easy deployment
- Created systemd service file
- Added GitHub Actions workflows
- Added security scanning (Bandit, Safety)
- Added code quality gates

### 📦 Dependencies
- Added `tweepy==4.14.0` for Twitter API
- Added `python-dotenv==1.0.1` for environment management
- Updated `requests==2.31.0` (security updates)
- Updated `beautifulsoup4==4.12.3`
- Added development dependencies (pytest, mypy, black, flake8)

## [1.0.0] - 2024-XX-XX

### Initial Release
- Basic TSA wait time scraping
- Simple Twitter posting
- Hardcoded credentials (insecure)
- Minimal error handling
- No tests or documentation
