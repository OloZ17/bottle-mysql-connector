#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup

# Get the long description from README if it exists
here = os.path.abspath(os.path.dirname(__file__))
try:
    with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = '''
Bottle-MySQL-Connector is a plugin that integrates MySQL with your Bottle application.
It automatically passes a mysql database connection handle to route callbacks that require it.
'''

# Get version from the module without importing it
def get_version():
    with open(os.path.join(here, 'bottle_mysql_connector.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[1].strip())
    return '0.1.0'  # Fallback version

setup(
    name='bottle-mysql-connector',
    version=get_version(),
    url='https://github.com/OloZ17/bottle-mysql-connector',
    description='MySQL integration for Bottle using mysql-connector-python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Thomas Lamarche',
    author_email='thomas.lamarche17@gmail.com',
    license='MIT',
    platforms='any',
    python_requires='>=3.6',
    py_modules=['bottle_mysql_connector'],
    install_requires=[
        'bottle>=0.12',
        'mysql-connector-python>=8.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
    ],
    keywords='bottle plugin mysql database',
    project_urls={
        'Bug Reports': 'https://github.com/OloZ17/bottle-mysql-connector/issues',
        'Source': 'https://github.com/OloZ17/bottle-mysql-connector',
    },
)