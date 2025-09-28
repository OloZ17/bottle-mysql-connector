#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for bottle-mysql-connector plugin.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import bottle
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bottle_mysql_connector import MySQLConnectorPlugin, Plugin


class TestMySQLConnectorPlugin(unittest.TestCase):
    """Test cases for MySQLConnectorPlugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = MySQLConnectorPlugin(
            user='test_user',
            password='test_pass',
            database='test_db'
        )
        self.app = bottle.Bottle()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app = None
        self.plugin = None
    
    def test_plugin_initialization_defaults(self):
        """Test plugin initialization with default values."""
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db'
        )
        self.assertEqual(plugin.host, 'localhost')
        self.assertEqual(plugin.port, 3306)
        self.assertEqual(plugin.charset, 'utf8mb4')
        self.assertEqual(plugin.keyword, 'db')
        self.assertTrue(plugin.autocommit)
        self.assertTrue(plugin.dictionary)
        self.assertFalse(plugin.buffered)
        self.assertIsNone(plugin.time_zone)
    
    def test_plugin_initialization_custom(self):
        """Test plugin initialization with custom values."""
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            host='192.168.1.1',
            port=3307,
            charset='utf8',
            keyword='database',
            autocommit=False,
            dictionary=False,
            buffered=True,
            time_zone='+00:00'
        )
        self.assertEqual(plugin.host, '192.168.1.1')
        self.assertEqual(plugin.port, 3307)
        self.assertEqual(plugin.charset, 'utf8')
        self.assertEqual(plugin.keyword, 'database')
        self.assertFalse(plugin.autocommit)
        self.assertFalse(plugin.dictionary)
        self.assertTrue(plugin.buffered)
        self.assertEqual(plugin.time_zone, '+00:00')
    
    def test_plugin_alias(self):
        """Test that Plugin is an alias for MySQLConnectorPlugin."""
        self.assertIs(Plugin, MySQLConnectorPlugin)
    
    def test_plugin_name_and_api(self):
        """Test plugin name and API version."""
        self.assertEqual(self.plugin.name, 'mysql')
        self.assertEqual(self.plugin.api, 2)
    
    def test_plugin_setup_no_conflict(self):
        """Test plugin setup doesn't conflict when keywords are different."""
        plugin1 = MySQLConnectorPlugin(
            user='user1',
            password='pass1',
            database='db1',
            keyword='db1'
        )
        plugin2 = MySQLConnectorPlugin(
            user='user2',
            password='pass2',
            database='db2',
            keyword='db2'
        )
        
        self.app.install(plugin1)
        self.app.install(plugin2)
        
        # Both plugins should be installed without conflict
        self.assertIn(plugin1, self.app.plugins)
        self.assertIn(plugin2, self.app.plugins)
    
    def test_plugin_setup_conflict_keyword(self):
        """Test plugin setup raises error with conflicting keywords."""
        plugin1 = MySQLConnectorPlugin(
            user='user1',
            password='pass1',
            database='db1',
            keyword='db'
        )
        plugin2 = MySQLConnectorPlugin(
            user='user2',
            password='pass2',
            database='db2',
            keyword='db'  # Same keyword
        )
        
        self.app.install(plugin1)
        
        with self.assertRaises(bottle.PluginError) as context:
            plugin2.setup(self.app)
        
        self.assertIn('conflicting settings', str(context.exception))
    
    def test_plugin_setup_name_modification(self):
        """Test plugin name modification when same name exists."""
        plugin1 = MySQLConnectorPlugin(
            user='user1',
            password='pass1',
            database='db1',
            keyword='db1'
        )
        plugin2 = MySQLConnectorPlugin(
            user='user2',
            password='pass2',
            database='db2',
            keyword='db2'
        )
        
        self.app.install(plugin1)
        plugin2.setup(self.app)
        
        # Second plugin should have modified name
        self.assertEqual(plugin2.name, 'mysql_db2')
    
    @patch('mysql.connector.connect')
    def test_route_with_db_parameter(self, mock_connect):
        """Test that routes with db parameter get database connection."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Create a test route
        test_result = {'test': 'data'}
        
        @self.app.route('/test')
        def test_route(db):
            db.execute("SELECT 1")
            return test_result
        
        self.app.install(self.plugin)
        
        # Get the wrapped callback
        wrapped_callback = self.app.routes[0].callback
        
        # Call the wrapped callback directly
        result = wrapped_callback()
        
        # Verify the result
        self.assertEqual(result, test_result)
        
        # Verify database interactions
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_with("SELECT 1")
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_route_without_db_parameter(self, mock_connect):
        """Test that routes without db parameter don't get database connection."""
        @self.app.route('/test')
        def test_route():
            return {'test': 'data'}
        
        self.app.install(self.plugin)
        
        # Get the callback - should be unwrapped
        callback = self.app.routes[0].callback
        
        # Call the callback
        result = callback()
        
        # Verify the result
        self.assertEqual(result, {'test': 'data'})
        
        # Verify no database connection was made
        mock_connect.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_dictionary_cursor(self, mock_connect):
        """Test dictionary cursor creation."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            dictionary=True,
            buffered=False
        )
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify cursor was created with dictionary=True
        mock_connection.cursor.assert_called_with(dictionary=True)
    
    @patch('mysql.connector.connect')
    def test_buffered_cursor(self, mock_connect):
        """Test buffered cursor creation."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            dictionary=False,
            buffered=True
        )
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify cursor was created with buffered=True
        mock_connection.cursor.assert_called_with(buffered=True)
    
    @patch('mysql.connector.connect')
    def test_dictionary_and_buffered_cursor(self, mock_connect):
        """Test cursor with both dictionary and buffered options."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            dictionary=True,
            buffered=True
        )
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify cursor was created with both options
        mock_connection.cursor.assert_called_with(dictionary=True, buffered=True)
    
    @patch('mysql.connector.connect')
    def test_time_zone_setting(self, mock_connect):
        """Test time zone setting."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            time_zone='+05:00'
        )
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify time zone was set
        mock_cursor.execute.assert_called_with("SET time_zone = %s", ('+05:00',))
    
    @patch('mysql.connector.connect')
    def test_autocommit_true(self, mock_connect):
        """Test autocommit when enabled."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            autocommit=True
        )
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify commit was called
        mock_connection.commit.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_autocommit_false(self, mock_connect):
        """Test autocommit when disabled."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db',
            autocommit=False
        )
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify commit was not called
        mock_connection.commit.assert_not_called()
    
    @patch('mysql.connector.connect')
    def test_integrity_error_handling(self, mock_connect):
        """Test handling of IntegrityError."""
        import mysql.connector
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        @self.app.route('/test')
        def test_route(db):
            raise mysql.connector.IntegrityError("Duplicate entry")
        
        self.app.install(self.plugin)
        wrapped_callback = self.app.routes[0].callback
        
        # Should raise HTTPError
        with self.assertRaises(bottle.HTTPError) as context:
            wrapped_callback()
        
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn('Integrity Error', context.exception.body)
        
        # Verify rollback was called
        mock_connection.rollback.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_connection_error_handling(self, mock_connect):
        """Test handling of connection errors."""
        import mysql.connector
        
        mock_connect.side_effect = mysql.connector.Error("Can't connect to MySQL server")
        
        @self.app.route('/test')
        def test_route(db):
            return 'OK'
        
        self.app.install(self.plugin)
        wrapped_callback = self.app.routes[0].callback
        
        # Should raise HTTPError
        with self.assertRaises(bottle.HTTPError) as context:
            wrapped_callback()
        
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn('Connection Error', context.exception.body)
    
    @patch('mysql.connector.connect')
    def test_cleanup_on_error(self, mock_connect):
        """Test proper cleanup of resources on error."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        @self.app.route('/test')
        def test_route(db):
            raise Exception("Test error")
        
        self.app.install(self.plugin)
        wrapped_callback = self.app.routes[0].callback
        
        # Should raise the exception
        with self.assertRaises(Exception):
            wrapped_callback()
        
        # Verify cleanup was performed
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
        mock_connection.rollback.assert_called_once()
    
    @patch('mysql.connector.connect')
    def test_route_config_override(self, mock_connect):
        """Test route-specific configuration override."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Set default database
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='default_db'
        )
        
        # Create route with override
        @self.app.route('/test', mysql={'database': 'override_db'})
        def test_route(db):
            return 'OK'
        
        self.app.install(plugin)
        wrapped_callback = self.app.routes[0].callback
        wrapped_callback()
        
        # Verify connection was made with override database
        call_args = mock_connect.call_args[1]
        self.assertEqual(call_args['database'], 'override_db')


class TestPluginIntegration(unittest.TestCase):
    """Integration tests for the plugin."""
    
    @patch('mysql.connector.connect')
    def test_multiple_routes(self, mock_connect):
        """Test plugin with multiple routes."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        app = bottle.Bottle()
        plugin = MySQLConnectorPlugin(
            user='user',
            password='pass',
            database='db'
        )
        
        @app.route('/route1')
        def route1(db):
            return 'route1'
        
        @app.route('/route2')
        def route2():
            return 'route2'
        
        @app.route('/route3')
        def route3(db):
            return 'route3'
        
        app.install(plugin)
        
        # Test route1 (has db parameter)
        result1 = app.routes[0].callback()
        self.assertEqual(result1, 'route1')
        
        # Test route2 (no db parameter)
        result2 = app.routes[1].callback()
        self.assertEqual(result2, 'route2')
        
        # Test route3 (has db parameter)
        result3 = app.routes[2].callback()
        self.assertEqual(result3, 'route3')
        
        # Verify connections were made for routes with db parameter
        self.assertEqual(mock_connect.call_count, 2)  # route1 and route3


if __name__ == '__main__':
    unittest.main()