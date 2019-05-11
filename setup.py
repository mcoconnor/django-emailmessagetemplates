#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "0.1.3"

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-emailmessagetemplates',
    version=version,
    description="""A Django app that allows users to edit email content with an easy-to-integrate developer API.""",
    long_description=readme + '\n\n' + history,
    author='Michael O''Connor',
    author_email='michael@mcoconnor.net',
    url='https://github.com/mcoconnor/django-emailmessagetemplates',
    packages=['emailmessagetemplates',],
    include_package_data=True,
    install_requires=['django-appconf',],
    extras_require = {'text_autogen':  ["html2text"],},
    license="BSD",
    zip_safe=False,
    keywords=['django','email','template'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',  
        'Environment :: Web Environment',
    ],
)
