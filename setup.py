#!/usr/bin/env python
#import extend_me
_doc = """
Extend Me - Class based extension/plugin library
================================================

This module provides mechanism of extension of your application
based on 'extension via inheritance'. Under this words I mean
ability to define new extensions of application objects simply
by subclassing of extensible classes of app.

For example we have app with class 'Worker' which we would like
to make extensible (allowing third party modules to extend or
change its behavior). Thinking strait, there are a lot of work
to be done, to impelement mechanism of loading, registering,
end enabling extension, with lot of glue code, which must define
some entry points to connect extension and main app. But why not
make it simpler, supposing that any subclass of 'Worker' will
extend it? And this module provides implementation of this
in two ways:

    - Explicit (by using metaclass *ExtensibleType* directly)
        - When using this way You will heve seperatly Base class
        to be subclassed by extension classes and class getter
        which will construct class based on all defined extensions
        using multiple inhertance

    - Implicit (by using Extensible class which use metaclass
        magic implicitly)
        - *Extensible* class takes care of all metaclass magic
        related to generation objects of correct class


How it Works
------------

Metaclass (*ExtensibleType*) tracks all subclasses of class it
is applied to, and provides method to build class based on all
subclasses of base class, thus using all functionality of all
subclasses. Thus generation of correct class is separate process
which should be used everywhere where extensible class is requred.

To simplify this class *Extensible* was implemented. It has redefined
method *__new__* which automaticaly creates instances of correct class
(class that inherited from base class and all its extensions')
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='extend_me',
    version='1.0.0',  # extend_me.__version__,
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
