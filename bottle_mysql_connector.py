"""
Bottle-MySQL-Connector is a plugin that integrates MySQL with your Bottle
application. It automatically connects to a database at the beginning of a
request, passes the database handle to the route callback and closes the
connection afterwards.

To automatically detect routes that need a database connection, the plugin
searches for route callbacks that require a `db` keyword argument
(configurable) and skips routes that do not. This removes any overhead for
routes that don't need a database connection.

Results are returned as dictionaries if you put option at true

Usage Example::

    import bottle
    import bottle_mysql_connector

    app = bottle.Bottle()
    # host is optional, default is localhost
    plugin = bottle_mysql_connector.Plugin(
        user='DB_USER', 
        password='DB_PASSWORD', 
        database='DB_NAME', 
        host='DB_HOST', 
        port=3306
    )
    app.install(plugin)

    @app.route('/show/<item>')
    def show(item, db):
        query = "SELECT * from items where name = %s"
        data = (item,)
        db.execute(query, data)
        row = db.fetchone()
        if row:
            return bottle.template('showitem', page=row)
        return bottle.HTTPError(404, "Page not found")

"""

__author__ = "Thomas Lamarche"
__version__ = '0.1.0'
__license__ = 'MIT'

import inspect
import mysql.connector
import bottle


# PluginError is defined to bottle >= 0.10
if not hasattr(bottle, 'PluginError'):
    class PluginError(bottle.BottleException):
        pass
    bottle.PluginError = PluginError


class MySQLConnectorPlugin(object):
    """
    This plugin passes a mysql database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis.
    """

    name = 'mysql'
    api = 2

    def __init__(self, user=None, password=None, database=None, host='localhost', port=3306, autocommit=True,
                 dictionary=True, keyword='db', charset='utf8mb4', time_zone=None, buffered=False,
                 raise_on_warnings=False, use_pure=True):
        """
        Initialize the MySQL plugin.

        Args:
            user: MySQL username
            password: MySQL password
            database: Database name
            host: MySQL server host (default: localhost)
            port: MySQL server port (default: 3306)
            autocommit: Enable autocommit (default: True)
            dictionary: Return results as dictionaries (default: True)
            keyword: Keyword argument name for database cursor (default: 'db')
            charset: Character set to use (default: 'utf8mb4')
            time_zone: Time zone to set for the connection
            buffered: Use buffered cursor (default: False)
            raise_on_warnings: Raise exceptions on warnings (default: False)
            use_pure: Use pure Python implementation (default: True)
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.autocommit = autocommit
        self.dictionary = dictionary
        self.keyword = keyword
        self.charset = charset
        self.time_zone = time_zone
        self.buffered = buffered
        self.raise_on_warnings = raise_on_warnings
        self.use_pure = use_pure

    def setup(self, app):
        """
        Make sure that other installed plugins don't affect the same keyword argument.
        """
        for other in app.plugins:
            if not isinstance(other, MySQLConnectorPlugin):
                continue
            if other.keyword == self.keyword:
                raise PluginError(
                    "Found another mysql-connector plugin with conflicting settings (non-unique keyword).")
            elif other.name == self.name:
                self.name += '_%s' % self.keyword

    def apply(self, callback, route):
        # Get route configuration
        config = route.config
        _callback = route.callback

        # Override global configuration with route-specific values.
        if "mysql" in config:
            # Support for configuration before `ConfigDict` namespaces
            g = lambda key, default: config.get('mysql', {}).get(key, default)
        else:
            g = lambda key, default: config.get('mysql.' + key, default)

        host = g('host', self.host)
        port = g('port', self.port)
        user = g('user', self.user)
        password = g('password', self.password)
        database = g('database', self.database)
        autocommit = g('autocommit', self.autocommit)
        dictionary = g('dictionary', self.dictionary)
        keyword = g('keyword', self.keyword)
        charset = g('charset', self.charset)
        time_zone = g('time_zone', self.time_zone)
        buffered = g('buffered', self.buffered)
        raise_on_warnings = g('raise_on_warnings', self.raise_on_warnings)
        use_pure = g('use_pure', self.use_pure)

        # Test if the original callback accepts the keyword argument.
        # Ignore it if it does not need a database handle.
        sig = inspect.signature(_callback)
        if keyword not in sig.parameters:
            return callback

        def wrapper(*args, **kwargs):
            # Configuration for MySQL connection
            config_dict = {
                'user': user,
                'password': password,
                'host': host,
                'port': port,
                'database': database,
                'charset': charset,
                'autocommit': autocommit,
                'raise_on_warnings': raise_on_warnings,
                'use_pure': use_pure
            }
            
            # Remove None values
            config_dict = {k: v for k, v in config_dict.items() if v is not None}
            
            cnx = None
            cursor = None
            
            try:
                # Connect to the database
                cnx = mysql.connector.connect(**config_dict)
                
                # Create cursor with appropriate options
                cursor_kwargs = {}
                if dictionary:
                    cursor_kwargs['dictionary'] = True
                if buffered:
                    cursor_kwargs['buffered'] = True
                    
                cursor = cnx.cursor(**cursor_kwargs)
                
                # Set time zone if specified
                if time_zone:
                    cursor.execute("SET time_zone = %s", (time_zone,))
                    
            except mysql.connector.Error as e:
                if cnx:
                    cnx.close()
                raise bottle.HTTPError(500, f"Database Connection Error: {e}")
            except Exception as e:
                if cnx:
                    cnx.close()
                raise bottle.HTTPError(500, f"Unexpected Error: {e}")

            # Add the cursor as a keyword argument
            kwargs[keyword] = cursor

            try:
                # Execute the route callback
                rv = callback(*args, **kwargs)
                
                # Commit if autocommit is enabled and connection is still open
                if autocommit and cnx and cnx.is_connected():
                    cnx.commit()
                    
                return rv
                
            except mysql.connector.IntegrityError as e:
                if cnx and cnx.is_connected():
                    cnx.rollback()
                raise bottle.HTTPError(500, f"Database Integrity Error: {e}")
            except mysql.connector.Error as e:
                if cnx and cnx.is_connected():
                    cnx.rollback()
                raise bottle.HTTPError(500, f"Database Error: {e}")
            except bottle.HTTPError:
                if autocommit and cnx and cnx.is_connected():
                    cnx.rollback()
                raise
            except bottle.HTTPResponse:
                if autocommit and cnx and cnx.is_connected():
                    cnx.commit()
                raise
            except Exception as e:
                if cnx and cnx.is_connected():
                    cnx.rollback()
                raise
            finally:
                # Clean up resources
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass
                if cnx:
                    try:
                        cnx.close()
                    except:
                        pass

        # Replace the route callback with the wrapped one
        return wrapper


# Alias for backward compatibility
Plugin = MySQLConnectorPlugin