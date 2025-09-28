# Contributing to Bottle MySQL Connector

First off, thank you for considering contributing to Bottle MySQL Connector! It's people like you that make this plugin a great tool for the community.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what you expected**
- **Include Python version, Bottle version, and mysql-connector-python version**
- **Include any error messages or stack traces**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**

### Your First Code Contribution

Unsure where to begin? You can start by looking through these issues:

- Issues labeled `good first issue` - should only require a few lines of code
- Issues labeled `help wanted` - more involved issues

### Pull Requests

1. Fork the repository and create your branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

3. Make your changes and ensure:

   - The code follows the existing style
   - You've added tests for your changes
   - All tests pass
   - Documentation is updated

4. Run the test suite:

   ```bash
   pytest tests/
   ```

5. Check code style:

   ```bash
   flake8 bottle_mysql_connector.py
   black --check bottle_mysql_connector.py
   ```

6. Commit your changes:

   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

8. Submit a pull request through GitHub

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/OloZ17/bottle-mysql-connector.git
   cd bottle-mysql-connector
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:

   ```bash
   pip install -e ".[dev]"
   ```

4. Set up a test MySQL database:
   ```sql
   CREATE DATABASE test_bottle_mysql;
   CREATE USER 'test_user'@'localhost' IDENTIFIED BY 'test_password';
   GRANT ALL PRIVILEGES ON test_bottle_mysql.* TO 'test_user'@'localhost';
   ```

## Style Guide

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 100 characters
- Use type hints where appropriate
- Add docstrings to all public functions and classes

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:

```
Add support for connection pooling

- Implement pool configuration in Plugin.__init__
- Add pool_size and pool_name parameters
- Update documentation with pooling examples

Fixes #123
```

### Documentation Style

- Use Markdown for documentation files
- Include code examples for new features
- Update README.md if adding new functionality
- Keep CHANGELOG.md up to date

## Testing

### Writing Tests

- Write tests for all new functionality
- Ensure tests are isolated and don't depend on external services
- Use mocking for database connections in unit tests
- Name test files as `test_*.py`
- Name test functions as `test_*`

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=bottle_mysql_connector

# Run specific test file
pytest tests/test_plugin.py

# Run specific test
pytest tests/test_plugin.py::TestMySQLConnectorPlugin::test_plugin_initialization
```

## Release Process

1. Update version in `bottle_mysql_connector.py`
2. Update CHANGELOG.md with release notes
3. Create a git tag:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   ```
4. Push the tag:
   ```bash
   git push origin v0.1.0
   ```

## Questions?

Feel free to open an issue with the label `question` if you have any questions about contributing.

Thank you for contributing! 🎉
