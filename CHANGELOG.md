# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-15

### Added
- Full Python 3 support (3.6+)
- Comprehensive error handling with detailed error messages
- Support for mysql-connector-python 8.0+
- Dictionary cursor support for returning results as dictionaries
- Buffered cursor option for better performance with large result sets
- Time zone configuration per connection
- Route-specific database configuration override
- Automatic resource cleanup in all error scenarios
- Connection parameter validation
- Better transaction management with autocommit control
- Support for raise_on_warnings and use_pure parameters
- Comprehensive test suite with unittest
- Modern packaging with setuptools and pyproject.toml
- Full documentation with examples

### Changed
- **BREAKING**: Dropped Python 2 support completely
- Minimum Python version is now 3.6
- Requires Bottle 0.12+ (dropped support for Bottle 0.9)
- Updated default charset from 'utf8' to 'utf8mb4' for better Unicode support
- Improved error messages to be more descriptive
- Better resource management with proper connection cleanup
- Modernized code structure following Python 3 best practices
- Updated documentation with better examples and configuration options
- Simplified code by removing Python 2 compatibility layers

### Fixed
- Connection leak issues when errors occur
- Proper cleanup in finally blocks even when cleanup itself fails
- Proper handling of connection state checking
- Resource cleanup on all error paths

### Security
- Updated to use utf8mb4 charset by default for better Unicode support
- Added connection parameter validation to prevent injection issues
- Proper error message handling without exposing sensitive information

### Removed
- Python 2 support and all compatibility code
- Support for Bottle versions < 0.12
- Deprecated distutils usage in favor of setuptools
- Unsafe exec() usage in setup.py
- Legacy inspect.getargspec() usage
- "### CUT HERE" marker in module file

## [0.0.4] - 2023-XX-XX

### Added
- Initial Python 2 compatible version
- Basic MySQL connection management
- Simple plugin system for Bottle framework

---

[Unreleased]: https://github.com/OloZ17/bottle-mysql-connector/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OloZ17/bottle-mysql-connector/compare/v0.0.4...v0.1.0
[0.0.4]: https://github.com/OloZ17/bottle-mysql-connector/releases/tag/v0.0.4