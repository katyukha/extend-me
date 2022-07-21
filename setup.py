#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

_doc = open('README.rst', 'rt').read()

setup(
    name='extend_me',
    version='1.1.5',
    description='Class based extension/plugin library',
    author='Dmytro Katyukha',
    author_email='dmytro.katyukha@gmail.com',
    url='https://github.com/katyukha/extend-me',
    long_description=_doc,
    install_requires=[
        'six>=1.13',
    ],
    license="MPL 2.0",
    py_modules=['extend_me'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['extension', 'plugin'],
)
