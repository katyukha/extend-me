"""
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


Class reference and usage
-------------------------
"""
#
# Copyright (C) 2014  Dmytro Katyukha
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "Dmytro Katyukha <firemage.dima@gmail.com>"
__version__ = "1.0.0"

import six
__all__ = ('ExtensibleType', 'Extensible')


class ExtensibleType(type):
    """ Metaclass for Extandable objects

        To make object (class) extendable just use this as metaclass:

            >>> import six  # Used for Python 2/3 compatability
            >>> # Generate metaclass to be used:
            >>> mc = ExtensibleType._("MyClassName")

            >>> # Define base class
            >>> @six.add_metaclass(mc)
            ... class Object(object):
            ...   pass

            >>> # Define extension
            >>> class ObjectExtension(Object):
            ...     def method1(self):
            ...         return "Test"

            >>> # Get class to be used for object creations
            >>> cls = mc.get_class()

            >>> # And now all classes that subclass Object
            >>> # will be base classes for one, generated by mc.get_class()
            >>> Object in cls.__bases__
            True
            >>> ObjectExtension in cls.__bases__
            True
            >>> cls.__name__ == "MyClassName"
            True

            >>> # Create class based on all extensions
            >>> obj = cls()
            >>> obj.method1()
            'Test'
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ExtensibleType, mcs).__new__(mcs, name, bases, attrs)

        if getattr(cls, '_generated', False):
            return cls

        # Do all magic only if subclass had defined required attributes
        if getattr(mcs, '_cls_name', None):
            if cls not in mcs._base_classes:
                mcs._base_classes.insert(0, cls)
                mcs._generated_class = None  # Clean cache

        return cls

    @classmethod
    def _(mcs, cls_name="Object"):
        """ Method to generate real metaclass to be used

            @param cls_name: name of generated class
        """
        class EXType(mcs):
            _cls_name = cls_name
            _base_classes = []
            _generated_class = None

        return EXType

    @classmethod
    def _get_base_classes(mcs):
        """ Returns list of classes to be as base classses for generated one
        """
        return mcs._base_classes

    @classmethod
    def _get_class(mcs):
        return type(mcs._cls_name, tuple(mcs._get_base_classes()), {'_generated': True})

    @classmethod
    def get_class(mcs):
        """ Generates new class to gether logic of all available extensions
        """
        if mcs._generated_class is None:
            mcs.__generated_class = mcs._get_class()
        return mcs.__generated_class


class TMeta(ExtensibleType):
    """ Helper metaclass to implement ability to use same class as bas class for
        extensions and as class to create objects baed on all extensions of this class

        Used internaly by class Extensible

        Example usage:
            >>> @six.add_metaclass(TMeta)
            ... class Root(object):
            ...     _extensible_meta_base = True

                # Subclassing Root we could create separate extension
                # tree/list. In this example all subclasses of CBase will
                # extend CBase in a way as CBase was subclass of all of them
            >>> class CBase(Root): pass
            >>> [b.__name__ for b in type(CBase)._base_classes]
            ['CBase']
            >>> class C1(CBase): pass
            >>> [b.__name__ for b in type(CBase)._base_classes]
            ['C1', 'CBase']
            >>> class C2(CBase): pass
            >>> [b.__name__ for b in type(CBase)._base_classes]
            ['C2', 'C1', 'CBase']

                # In same way we could create another tree/list of extensions
            >>> class XBase(Root): pass
            >>> [b.__name__ for b in type(XBase)._base_classes]
            ['XBase']
            >>> class X1(XBase): pass
            >>> [b.__name__ for b in type(XBase)._base_classes]
            ['X1', 'XBase']
            >>> class X2(XBase): pass
            >>> [b.__name__ for b in type(XBase)._base_classes]
            ['X2', 'X1', 'XBase']
    """
    def __new__(mcs, name, bases, attrs):
        # all extension work done. Normal creation may be continued
        if attrs.pop('_extensible_meta_done', False):
            return super(TMeta, mcs).__new__(mcs, name, bases, attrs)

        # If any base class have metaclass which is result of finished black
        # magic below, continue normal creation
        for base in bases:
            if getattr(type(base), '_extensible_meta_done', False):
                return super(TMeta, mcs).__new__(mcs, name, bases, attrs)

        # If we create class that is not 'Extensible' or other root class
        # do all the magic
        if not attrs.pop('_extensible_meta_base', False):
            mc = mcs._(name)  # Generate metaclass for class to be created
            mc._extensible_meta_done = True  # Add attribute that means "not futher extension magic required"
            attrs['_extensible_meta_done'] = True  # Required to avoid infinite recursion on __new__
            if six.PY2:
                attrs['__metaclass__'] = mc  # set newly generated metaclass for this object
            return mc(name, bases, attrs)  # Create new class with generated metaclass
        else:
            return super(TMeta, mcs).__new__(mcs, name, bases, attrs)


@six.add_metaclass(TMeta)
class Extensible(object):
    """ All direct subclasses of this class will be extensible through inhertance

        So to create new class that should be extensible just inhert it from this class:

            >>> class MyClass(Extensible): pass

        After this all subclasses of MyClass will extend it.
        For example, create simple extension which will add attribute and method to class:

            >>> class MyClassExtension(MyClass):
            ...     my_attr = 42
            ...     def my_method(self):
            ...         print ("Hello, %s" % self.my_attr)

        After this we expect that attributes and methods defined in extensions will be
        available in MyClass object:

            >>> my_obj = MyClass()
            >>> my_obj.my_attr
            42
            >>> my_obj.my_method()
            Hello, 42

        So as we see, we could extend any objects derived from Extensible class using simple
        inheritence with out any long code. This is useful for plugin or extension systems,
        making extension work when it just imported. But as disadvantage of this approach,
        when we ll get error when we try to access attributes of extensions from base class:

            >>> MyClass.my_attr
            Traceback (most recent call last):
            ...
            AttributeError: type object 'MyClass' has no attribute 'my_attr'

            >>> MyClass.my_method()
            Traceback (most recent call last):
            ...
            AttributeError: type object 'MyClass' has no attribute 'my_method'

        This happens because Extension class implements some black magic using inheritance and metaclasses.
        Extensible class have overridden __new__ method in the way when it creates instance not of base class
        but of automatically generated class which inherits from all its extensions.

            >>> [b.__name__ for b in my_obj.__class__.__bases__]
            ['MyClassExtension', 'MyClass']

        Thus any behavior of objects created by MyClass may be changed by extensions.
        And as one more thing, extensions that inherits from extensions will be extensions of
        base class, not extension of extension. So we could do things like:

            >>> class MyNewExtension(MyClassExtension):
            ...     my_attr = 25
            ...     def my_method_2(self):
            ...         print ("Method 2")
            >>> my_obj_2 = MyClass()  # Not after creating new extension we
            >>>                       # create new object
            >>> my_obj_2.my_attr
            25
            >>> my_obj_2.my_method()
            Hello, 25
            >>> my_obj_2.my_method_2()
            Method 2

        and objects created before definition of new extension will
        not be changed, they will not get new methods or attributes from new extensions

            >>> my_obj.my_attr
            42
            >>> my_obj.my_method()
            Hello, 42
            >>> my_obj.my_method_2()
            Traceback (most recent call last):
            ...
            AttributeError: 'MyClass' object has no attribute 'my_method_2'
    """
    _extensible_meta_base = True

    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_generated', False):
            return super(Extensible, cls).__new__(cls, *args, **kwargs)
        return type(cls).get_class()(*args, **kwargs)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
