'''
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

application = bottle.default_app()
# host is optional, default is localhost
plugin = bottle_mysql_connector.Plugin(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
application.install(plugin)

@app.route('/show/:<tem>')
def show(item, db):
    query = "SELECT {0} from items where name= %s".format(table)
    data = (item,)
    db.execute(query, data)
    row = db.fetchone()
    if row:
        return template('showitem', page=row)
    return HTTPError(404, "Page not found")

'''

__author__ = "Thomas Lamarche"
__version__ = '0.0.3'
__license__ = 'MIT'

### CUT HERE (see setup.py)

import inspect
import mysql.connector
import bottle


# PluginError is defined to bottle >= 0.10
if not hasattr(bottle, 'PluginError'):
    class PluginError(bottle.BottleException):
        pass
    bottle.PluginError = PluginError

class MySQLConnectorPlugin(object):
    '''
    This plugin passes a mysql database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis.
    '''

    name = 'mysql'
    api = 2

    def __init__(self, user=None, password=None, database=None, host='localhost', port=3306, autocommit=True, dictionary=True, keyword='db', charset='utf8', time_zone=None, buffered=False):
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

    def setup(self, app):
        '''
        Make sure that other installed plugins don't affect the same keyword argument.
        '''
        for other in app.plugins:
            if not isinstance(other, MySQLConnectorPlugin):
                continue
            if other.keyword == self.keyword:
                raise PluginError("Found another mysql-connector plugin with conflicting settings (non-unique keyword).")
            elif other.name == self.name:
                self.name += '_%s' % self.keyword

    def apply(self, callback, route):
        # hack to support bottle v0.9.x
        if bottle.__version__.startswith('0.9'):
            config = route['config']
            _callback = route['callback']
        else:
            config = route.config
            _callback = route.callback

        # Override global configuration with route-specific values.
        if "mysql" in config:
            # support for configuration before `ConfigDict` namespaces
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


        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        argspec = inspect.getargspec(_callback)
        if keyword not in argspec.args:
            return callback

        CONFIG = { 'user': user, 'password': password, 'database': database, 'charset': charset}

        def wrapper(*args, **kwargs):
            # Connect to the database
            try:
                cnx = mysql.connector.connect(**CONFIG)
                # Using dictionnary as cursor lets us return result as a dictionary instead of the default list
                # Using buffered to fetch the entire result set from the server and buffers the rows
                if dictionary and buffered:
                    cursor=cnx.cursor(dictionary=True, buffered=True)
                elif dictionary:
                    cursor=cnx.cursor(dictionary=True)
                else:
                    cursor = cnx.cursor()
                if time_zone:
                    cursor.execute("set time_zone=%s", (time_zone, ))
            except bottle.HTTPResponse, e:
                raise bottle.HTTPError(500, "Database Error", e)

            # Add the connection handle as a keyword argument.
            kwargs[keyword] = cursor

            try:
                rv = callback(*args, **kwargs)
                if autocommit:
                    cnx.commit()
            except mysql.connector.IntegrityError as e:
                cnx.rollback()
                raise bottle.HTTPError(500, "Database Error", e)
            except bottle.HTTPError as e:
                raise
            except bottle.HTTPResponse as e:
                if autocommit:
                    cnx.commit()
                raise
            finally:
                if cursor:
                    cursor.close()
                if cnx:
                    cnx.close()
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper

Plugin = MySQLConnectorPlugin
