#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='connme',
    version='0.1.0',
    description='Client untuk Hostapd',
    long_description=readme + '\n\n' + history,
    author='Ikhwan Setiawan',
    author_email='kuro.kid@gmail.com',
    url='https://github.com/kurokid/connme',
    packages=[
        'connme',
    ],
    package_dir={'connme': 'connme'},
    include_package_data=True,
    install_requires=[
        'hostapd', 
        'dnsmasq', 
        'iptables', 
        'iw',
    ],
    data_files=[
        ('share/applications', ['data/connme.desktop']),
        ('share/pixmaps', ['data/connme.png']),
        ('/etc', ['data/connme.conf']),
    ],
    scripts = ['bin/connme', 'bin/tether'],
    license="GPL",
    zip_safe=False,
    keywords='connme',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)