# Bottle MySQL Connector

[![PyPI version](https://badge.fury.io/py/bottle-mysql-connector.svg)](https://badge.fury.io/py/bottle-mysql-connector)
[![Python Versions](https://img.shields.io/pypi/pyversions/bottle-mysql-connector.svg)](https://pypi.org/project/bottle-mysql-connector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight MySQL plugin for the Bottle web framework, using the official mysql-connector-python driver.

## Features

- 🚀 **Simple Integration** - Easy to setup and use with Bottle applications
- 🔌 **Automatic Connection Management** - Handles connection lifecycle automatically
- 📘 **Dictionary Cursor Support** - Returns query results as dictionaries for easy data access
- ⚡ **Performance Optimized** - Supports buffered cursors and connection pooling
- 🛡️ **Robust Error Handling** - Automatic rollback on errors with detailed error messages
- 🎯 **Flexible Configuration** - Route-specific database configuration override
- 🐍 **Modern Python Support** - Fully compatible with Python 3.6+

## Installation

Install via pip:

```bash
pip install bottle-mysql-connector
```

Or install from source:

```bash
git clone https://github.com/OloZ17/bottle-mysql-connector.git
cd bottle-mysql-connector
pip install .
```

## Quick Start

### Basic Usage

```python
import bottle
from bottle_mysql_connector import Plugin

# Create a Bottle app
app = bottle.Bottle()

# Configure the MySQL plugin
plugin = Plugin(
    user='your_user',
    password='your_password',
    database='your_database',
    host='localhost',
    port=3306,
    charset='utf8mb4',
    dictionary=True,  # Return rows as dictionaries
    autocommit=True   # Autocommit transactions
)

# Install the plugin
app.install(plugin)

# Define routes that use the database
@app.route('/users')
def get_users(db):
    """The 'db' parameter is automatically injected by the plugin."""
    db.execute("SELECT id, name, email FROM users")
    users = db.fetchall()
    return {'users': users}

@app.route('/user/<user_id:int>')
def get_user(user_id, db):
    db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = db.fetchone()
    if user:
        return user
    return bottle.HTTPError(404, "User not found")

@app.route('/create_user', method='POST')
def create_user(db):
    data = bottle.request.json
    db.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (data['name'], data['email'])
    )
    return {'id': db.lastrowid, 'status': 'created'}

# Run the application
if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
```

## Configuration Options

| Parameter           | Type | Default     | Description                                   |
| ------------------- | ---- | ----------- | --------------------------------------------- |
| `user`              | str  | None        | MySQL username (required)                     |
| `password`          | str  | None        | MySQL password (required)                     |
| `database`          | str  | None        | Database name (required)                      |
| `host`              | str  | 'localhost' | MySQL server hostname or IP                   |
| `port`              | int  | 3306        | MySQL server port                             |
| `charset`           | str  | 'utf8mb4'   | Character set for the connection              |
| `autocommit`        | bool | True        | Enable automatic commit after each query      |
| `dictionary`        | bool | True        | Return rows as dictionaries instead of tuples |
| `buffered`          | bool | False       | Fetch and buffer all result rows immediately  |
| `time_zone`         | str  | None        | Set the time zone for the connection          |
| `keyword`           | str  | 'db'        | Parameter name for cursor injection in routes |
| `raise_on_warnings` | bool | False       | Raise exceptions for MySQL warnings           |
| `use_pure`          | bool | True        | Use pure Python implementation of connector   |

## Advanced Usage

### Route-specific Configuration

Override database settings for specific routes:

```python
@app.route('/special', mysql={'database': 'other_db', 'autocommit': False})
def special_route(db):
    """This route uses a different database and manual commit."""
    db.execute("SELECT * FROM special_table")
    data = db.fetchall()
    db.connection.commit()  # Manual commit required
    return {'data': data}
```

### Manual Transaction Management

Disable autocommit for transaction control:

```python
@app.route('/transfer', method='POST', mysql={'autocommit': False})
def transfer_funds(db):
    try:
        # Start transaction
        db.execute("START TRANSACTION")

        # Perform multiple operations
        db.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (100, 1))
        db.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (100, 2))

        # Commit if all operations succeed
        db.connection.commit()
        return {'status': 'success', 'message': 'Transfer completed'}

    except Exception as e:
        # Rollback on error
        db.connection.rollback()
        return bottle.HTTPError(500, f"Transfer failed: {str(e)}")
```

### Working with Stored Procedures

```python
@app.route('/call_procedure/<proc_name>')
def call_procedure(proc_name, db):
    # Call a stored procedure
    db.callproc(proc_name, args=['arg1', 'arg2'])

    # Fetch results if the procedure returns data
    results = []
    for result in db.stored_results():
        results.extend(result.fetchall())

    return {'results': results}
```

### Pagination Example

```python
@app.route('/users/page/<page:int>')
def get_users_paginated(page, db):
    per_page = 10
    offset = (page - 1) * per_page

    # Get total count
    db.execute("SELECT COUNT(*) as total FROM users")
    total = db.fetchone()['total']

    # Get paginated results
    db.execute(
        "SELECT * FROM users LIMIT %s OFFSET %s",
        (per_page, offset)
    )
    users = db.fetchall()

    return {
        'users': users,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    }
```

### Using Connection Pooling

For production environments with high traffic:

```python
from mysql.connector import pooling

# Create a connection pool
dbconfig = {
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
    'host': 'localhost'
}

# Create pool with 5-32 connections
cnxpool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    **dbconfig
)

# Use the pool in your application
# The plugin will automatically use connections from the pool
```

## Error Handling

The plugin provides comprehensive error handling:

```python
@app.route('/safe_operation')
def safe_operation(db):
    try:
        db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return db.fetchone()
    except mysql.connector.IntegrityError as e:
        # Handle integrity constraint violations
        return bottle.HTTPError(400, f"Data integrity error: {e}")
    except mysql.connector.DataError as e:
        # Handle data type errors
        return bottle.HTTPError(400, f"Invalid data: {e}")
    except mysql.connector.DatabaseError as e:
        # Handle general database errors
        return bottle.HTTPError(500, f"Database error: {e}")
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=bottle_mysql_connector --cov-report=html
```

## Requirements

- Python 3.6 or higher
- bottle >= 0.12
- mysql-connector-python >= 8.0.0

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to:

- Update tests as appropriate
- Follow the existing code style
- Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/OloZ17/bottle-mysql-connector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OloZ17/bottle-mysql-connector/discussions)
- **Email**: lamarche@kwaga.com

## Acknowledgments

- The Bottle framework team for their excellent micro web framework
- Oracle for the mysql-connector-python driver
- All contributors who have helped improve this plugin

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Authors

- **Thomas Lamarche** - _Initial work_ - [OloZ17](https://github.com/OloZ17)

---

Made with ❤️ for the Bottle and MySQL communities
