Bottle-MySQL-Connector
======================

MySQL is the world's most used relational database management system (RDBMS) that runs
as a server providing multi-user access to a number of databases.

This plugin simplifies the use of mysql databases in your Bottle applications using MySQL Connector/Python, a self-contained Python driver for communicating with MySQL servers.

Once installed, all you have to do is to add an ``db`` keyword argument 
(configurable) to route callbacks that need a database connection.


`Bottle-MySQL-Connector` is written by [Thomas Lamarche](https://github.com/OloZ17)


Installation
------------

Install using pip:

    $ pip install bottle-mysql-connector

or download the latest version from github: https://github.com/OloZ17/bottle-mysql-connector

    $ git clone git://github.com/OloZ17/bottle-mysql-connector.git
    $ cd bottle-mysql-connector
    $ python setup.py install

Usage
-----

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

Routes that do not expect an ``db`` keyword argument are not affected.

The connection handle is configurable so that rows can be returned as either an
index (like tuples) or as dictionaries. At the end of the request cycle, outstanding
transactions are committed and the connection is closed automatically.
If an error occurs, any changes to the database since the last commit are rolled back to keep
the database in a consistent state.

Configuration
-------------

The following configuration options exist for the plugin class:

* **user**: Username that will be used to connect to the database (default: None).
* **password**: Password that will be used to connect to the database (default: None).
* **database**: Database name that will be connected to (default: None).
* **host**: Database server host (default: 'localhost').
* **port**: Databse server port (default: 3306).
* **keyword**: The keyword argument name that triggers the plugin (default: 'db').
* **autocommit**: Whether or not to commit outstanding transactions at the end of the request cycle (default: True).
* **dictionnary**: Whether or not to support dict-like access to row objects (default: True).
* **charset**: Database connection charset (default: 'utf8')
* **timezone**: Database connection time zone (default: None).
* **buffered**: To fetch the entire result set from the server and buffers the rows (default: False).

You can override each of these values on a per-route basis: 

    @app.route('/cache/<item>', mysql={'buffered': True})
    def cache(item, db):
        ...

