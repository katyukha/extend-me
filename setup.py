#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

_doc = open('README.rst', 'rt').read()

setup(
    name='extend_me',
    version='1.1.2',  # extend_me.__version__,
    description='Class based extension/plugin library',
    author='Dmytro Katyukha',
    author_email='firemage.dima@gmail.com',
    url='https://github.com/katyukha/extend-me',
    long_description=_doc,  # extend_me.__doc__,
    #packages=[],
    #scripts=[],
    install_requires=[
        'six',
    ],
    license="GPL",
    py_modules=['extend_me'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['extension', 'plugin'],
)
