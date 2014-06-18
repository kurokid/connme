#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='connme',
    version='0.5',
    description='Client untuk Hostapd',
    long_description=readme + '\n\n' + history,
    author='Ikhwan Setiawan',
    author_email='kuro.kid@gmail.com',
    url='https://github.com/kurokid/connme',
    packages=find_packages(exclude=['tests']),
    package_dir={'connme': 'connme'},
    include_package_data=True,
    package_data = {
        # '': ['*.txt', '*.rst'],
        'connme': ['data/*.html', 'data/*.css'],
    },
    install_requires=[
        'setuptools',
        'qt4'
    ],
    data_files=[
        ('share/applications', ['data/connme.desktop']),
        ('share/pixmaps', ['data/connme.png']),
        ('/etc', ['data/connme.conf']),
	('/usr/share/polkit-1/actions', ['data/org.freedesktop.pkexec.connme.policy']),
    ],
    scripts = ['bin/connme', 'bin/create_ap'],
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
