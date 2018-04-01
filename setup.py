"""
Flask-Chassis
-------------
Microservice chassis
"""
import io
import re
from setuptools import setup

with io.open('flask_chassis/__init__.py', encoding='utf-8') as f:
    version = re.search(r"__version__ = '(.+)'", f.read()).group(1)

setup(
    name='Flask-Chassis',
    version=version,
    url='https://github.com/dabarrell/flask-microservice-chassis',
    license='MIT',
    author='David Barrell',
    author_email='david@barrell.me',
    description='A basic microservice chassis for flask',
    long_description=__doc__,
    packages=['flask_chassis'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)