# Contributing to TSA Wait Times Bot

Thank you for your interest in contributing to the TSA Wait Times Bot! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

For feature requests:
- Use a clear, descriptive title
- Provide detailed explanation of the feature
- Explain why this feature would be useful
- Include examples of how it would work

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Make your changes** following our coding standards
4. **Add tests** for any new functionality
5. **Run tests**: `pytest tests/ -v`
6. **Run linters**:
   ```bash
   black time2wait.py
   flake8 time2wait.py
   mypy time2wait.py --ignore-missing-imports
   ```
7. **Update documentation** if needed
8. **Commit your changes** with clear, descriptive messages
9. **Push to your fork** and submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/TSA-Wait-Times.git
cd TSA-Wait-Times

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Maximum line length: 120 characters
- Use docstrings for all functions, classes, and modules

### Code Quality Tools

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pytest** for testing

### Writing Tests

- Write tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_format_tweet_with_valid_data():
    """Test formatting tweet with valid wait times"""
    # Arrange
    wait_times = {"NORTH CHECKPOINT": 10}

    # Act
    result = format_tweet(wait_times)

    # Assert
    assert "North" in result
    assert "10 min" in result
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add feature: Brief description

Detailed explanation of what changed and why.

Fixes #123
```

Prefix types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## Testing

### Running Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=time2wait --cov-report=html

# Run specific test file
pytest tests/test_bot.py -v

# Run specific test
pytest tests/test_bot.py::TestFormatTweet::test_format_tweet_with_valid_data -v
```

### Writing Integration Tests

For testing web scraping:
- Use mock responses when possible
- Don't hit actual ATL website in tests
- Test edge cases (empty responses, malformed HTML, etc.)

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add comments for complex logic
- Update CHANGELOG.md

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md with changes
3. Create pull request to `main`
4. After merge, tag release: `git tag v2.0.1`
5. Push tags: `git push --tags`

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Reach out to maintainers

Thank you for contributing! 🎉
