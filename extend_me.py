# -*- coding: utf-8 -*-
# Copyright © 2014-2018 Dmytro Katyukha <dmytro.katyukha@gmail.com>

#######################################################################
# This Source Code Form is subject to the terms of the Mozilla Public #
# License, v. 2.0. If a copy of the MPL was not distributed with this #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.            #
#######################################################################

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


Examples
--------

ExtensibleType
~~~~~~~~~~~~~~

At the begining we should create a metaclass that will automaticaly
gether all information about all extensions, and apply this metaclass
to class we would like to enable extensions for::

    >>> import six  # Used for Python 2/3 compatability
    >>> mc = ExtensibleType._("Object")

    >>> @six.add_metaclass(mc)
    ... class Object(object):
    ...     pass

Not method *_* of *ExtensibleType*. This method is used to create metaclass
for specific object. It receives one argument - string that will be used as
name of class generated by this metaclass

Next we may define extension for this class. It is very simple.
Just subclass previously defined class::

    >>> class ObjectExtension(Object):
    ...     cool_attribute = 1
    ...     def method1(self):
    ...         return "Test"

So... at this momet we have base class and extension. And here is that
core magic occures. Metaclass that was created at the begining automaticaly
collects all subclasses of base class. So it is posible now to create new
class that is subclass of all subclasses of base class using
multiple inheritance.
And metaclass *mc* will do it for You::

    >>> cls = mc.get_class()

And now You can use cls for Your needs, instead of base class.
It can do all that base class can, and all that extensions can::

    >>> obj = cls()
    >>> obj.method1()
    'Test'
    >>> obj.cool_attribute
    1


ExtensibleByHashType
~~~~~~~~~~~~~~~~~~~~

Same as *ExtensibleType*, but allows to build tree of classes
for diferent names (types). Just look examples below.

First, create metaclass that will specify inheritance rules::

    >>> import six  # Used for Python 2/3 compatability
    >>> mc = ExtensibleByHashType._("Connector", hashattr='name')

Here we see aditional parametr in _ method: ``hashattr='name'``
which describes what meta attribute will be used as key(hash).

Next step - we have to create Base class with this metaclass.
As example we will look into connection classes of *openerp_proxy* project::

    >>> @six.add_metaclass(mc)
    ... class ConnectorBase(object):
    ...     # Base class for all connectors
    ...
    ...     def __init__(self, host, port, verbose=False):
    ...         self.host = host
    ...         self.port = port
    ...         self.verbose = verbose
    ...
    ...     def _get_service(self, name):
    ...         raise NotImplementedError
    ...
    ...     def get_service(self, name):
    ...         # Returns service for specified *name*
    ...         return self._get_service(name)

Base class describes only interface, and may be some part of abstract logic
And as next step we will extend it in diferent ways to support different
connection types::

    >>> class ConnectorXMLRPC(ConnectorBase):
    ...     # XML-RPC connector
    ...     class Meta:
    ...         name = 'xml-rpc' # remember definition of metaclass?
    ...                          # this attribute is used as hash(key)
    ...                          # to unique identify each banch of extensions
    ...                          # of base class
    ...
    ...     def __init__(self, *args, **kwargs):
    ...         super(ConnectorXMLRPC, self).__init__(*args, **kwargs)
    ...         self.__services = {}
    ...
    ...     def get_service_url(self, service_name):
    ...         return 'http://%s:%s/xmlrpc/%s' % (self.host,
    ...                                            self.port,
    ...                                            service_name)
    ...
    ...     def _get_service(self, name):
    ...         service = self.__services.get(name, False)
    ...         if service is False:
    ...             service = XMLRPCProxy(self.get_service_url(name),
    ...                                   verbose=self.verbose)
    ...             self.__services[name] = service
    ...         return service
    ...
    ...
    ... # Pay attention on base class.
    >>> class ConnectorXMLRPCS(ConnectorXMLRPC):
    ...     # XML-RPCS Connector
    ...     class Meta:
    ...         name = 'xml-rpcs'
    ...
    ...     def get_service_url(self, service_name):
    ...         return 'https://%s:%s/xmlrpc/%s' % (self.host,
    ...                                             self.port,
    ...                                             service_name)

Code above creates two connectors: one for XML-RPC and one for XML-RPCS.
Each of connectors may be extended by simple inheritance. And if required any
extension may define new branch(key)(hash) as wee see in example above.

To use this connector *mc* has method *get_class(name[, default=False])*
wich will return class generated for hash=*name*::

    >>> cls = mc.get_class('xml-rpc')
    >>> [b.__name__ for b in cls.__bases__]
    ['ConnectorXMLRPC', 'ConnectorBase']
    >>> cls.__name__
    'Connector'

    >>> cls = mc.get_class('xml-rpcs')
    >>> [b.__name__ for b in cls.__bases__]
    ['ConnectorXMLRPCS', 'ConnectorBase']
    >>> cls.__name__
    'Connector'

Example above shows what classes will be generated for specified names.
By default, if *mc.get_class* called with unregistered name
(No extension with ``Meta.name == name`` defined) it will raise *ValueError*

If You want to allow creating of classes with not *Meta.name* defined,
just pass ``default=True`` to *mc.get_class*::

    >>> cls = mc.get_class('unexisting-protocol', default=True)
    >>> [b.__name__ for b in cls.__bases__]
    ['ConnectorBase']
    >>> cls.__name__
    'Connector'


Extensible
~~~~~~~~~~

This class provides one more level of abstraction, allowing to hide
all metaclass magic behide the scene. So, using it You don't need to worry
about metaclasses and class creation process. Just inherit extensions
from base class, and use in Your program instances of base class.
Let's see it in example::

    >>> class MyCoolClass(Extensible):
    ...     my_attr_1 = 25
    ...     def my_method1(self, arg1):
    ...         print('Hello, %s' % arg1)

    >>> class MyCoolClassExtension1(MyCoolClass):
    ...     def my_method1(self, arg1):
    ...         super(MyCoolClassExtension1, self).my_method1(arg1.upper())
    ...
    ...     def my_method2(self, arg1):
    ...         print("Good by, %s" % arg1)

And now using simply instances of base class You have all abilities
that provided by extensions::

    >>> my_cool_obj = MyCoolClass()
    >>> print(my_cool_obj.my_attr_1)
    25
    >>> my_cool_obj.my_method1('World')
    Hello, WORLD
    >>> my_cool_obj.my_method2('World')
    Good by, World

"""
__author__ = "Dmytro Katyukha <dmytro.katyukha@gmail.com>"
__version__ = "1.1.5"

import collections
import six

__all__ = ('ExtensibleType', 'Extensible', 'ExtensibleByHashType', )


class ExtensibleType(type):
    """ Metaclass for Extensible objects

        To make object (class) extendsible just do following.

        Create metaclass for extension point::

            >>> import six  # Used for Python 2/3 compatability
            >>> # Generate metaclass to be used:
            >>> mc = ExtensibleType._("MyClassName")

        Define base class for which will be starting point for extensions::

            >>> # Define base class
            >>> @six.add_metaclass(mc)
            ... class Object(object):
            ...   pass

        Define just simple extension which introduces new method,
        simply subclassing base class::

            >>> # Define extension
            >>> class ObjectExtension(Object):
            ...     def method1(self):
            ...         return "Test"

        Now to get class with all loaded extension enabled, just do::

            >>> # Get class to be used for object creations
            >>> cls = mc.get_class()

        And now check what we got::

            >>> # Now all classes that subclass Object
            >>> # will be base classes for one, generated by mc.get_class()
            >>> Object in cls.__bases__
            True
            >>> ObjectExtension in cls.__bases__
            True
            >>> cls.__name__ == "MyClassName"
            True
            >>> [b.__name__ for b in cls.__bases__]
            ['ObjectExtension', 'Object']

            >>> # Create class based on all extensions
            >>> obj = cls()
            >>> obj.method1()
            'Test'
            >>> obj2 = mc.get_object()
            >>> obj2.method1()
            'Test'

        Next try to use ABC with this class::

            >>> import abc
            >>> from six.moves import collections_abc
            >>> amc = ExtensibleType._("TestABC", with_meta=abc.ABCMeta)
            >>> @six.add_metaclass(amc)
            ... class ABCSequence(collections_abc.Sequence):
            ...    def __init__(self, seq):
            ...        self.seq = seq
            ...    def __getitem__(self, index):
            ...        return self.seq[index]
            ...    def __len__(self):
            ...        return len(self.seq)
            >>> seq = amc.get_class()([1, 1, 2])

        And now check if Sequence logic forks fine::

            >>> seq[1]
            1
            >>> seq[2]
            2
            >>> seq[3]
            Traceback (most recent call last):
            ...
            IndexError: list index out of range
            >>> len(seq)
            3
            >>> 1 in seq
            True
            >>> 3 in seq
            False
            >>> seq.count(2)
            1
            >>> seq.count(1)
            2
            >>> [i for i in seq]
            [1, 1, 2]

        And let's try to build extension::

            >>> class NABCSequence(ABCSequence):
            ...     def count2(self, *args, **kwargs):
            ...         return self.count(*args, **kwargs)*2

            >>> # Get object with all extensions applied
            >>> seq2 = amc.get_object([1, 1, 2])
            >>> seq2.count2(1)
            4
            >>> seq2.count2(2)
            2
            >>> seq2.count(1)
            2
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ExtensibleType, mcs).__new__(mcs, name, bases, attrs)

        if getattr(cls, '_generated', False):
            return cls

        mcs._add_base_class(cls)

        return cls

    @classmethod
    def _add_base_class(mcs, cls):
        # Do all magic only if subclass had defined required attributes
        if getattr(mcs, '_cls_name', None):
            if cls not in mcs._base_classes:
                mcs._base_classes.insert(0, cls)
                mcs._generated_class = None  # Clean cache

    @classmethod
    def _(mcs, cls_name="Object", with_meta=None):
        """ Method to generate real metaclass to be used::

                mc = ExtensibleType._("MyClass")  # note this line
                @six.add_metaclass(mc)
                class MyClassBase(object):
                    pass

            :param str cls_name: name of generated class
            :param class with_meta: Mix aditional metaclass in.
                                    (default: None)
            :return: specific metaclass to track new inheritance tree
        """
        if with_meta is not None:
            class EXType(with_meta, mcs):
                _cls_name = cls_name
                _base_classes = []
                _generated_class = None
        else:
            class EXType(mcs):
                _cls_name = cls_name
                _base_classes = []
                _generated_class = None

        return EXType

    @classmethod
    def get_class(mcs):
        """ Generates new class to gether logic of all available extensions
            ::

                mc = ExtensibleType._("MyClass")
                @six.add_metaclass(mc)
                class MyClassBase(object):
                    pass

                # get class with all extensions enabled
                MyClass = mc.get_class()

        """
        if mcs._generated_class is None:
            mcs._generated_class = type(
                mcs._cls_name,
                tuple(mcs._base_classes),
                {'_generated': True})
        return mcs._generated_class

    @classmethod
    def get_object(mcs, *args, **kwargs):
        """ Creates new object with all extensions applied

            all *args* and *keyword arguments* will be forwarded
            to generated class constructor

            Same as ``.get_class()(*args, **kwargs)``
        """
        return mcs.get_class()(*args, **kwargs)


class ExtensibleByHashType(ExtensibleType):
    """ Metaclass for extensible object that allows
        to build extension trees. This may be useful in
        situations where there is some set of similar objects
        which in some cases may behave diferently, which looks
        like all of them have same base class and some set of
        subclasses for each situation. For example we have
        some set of services which have same protocol, but we
        would like to code some aditional logic for each service.
        In this case we could build next architecture

        At first define metaclass which will control building extensions
            >>> mc = ExtensibleByHashType._("MyCoolClass", hashattr='name')

        Then define base class which represents common inteface
        for each service:
            >>> @six.add_metaclass(mc)
            ... class ServiceBase(object):
            ...     def do_reduce(self, f, *args):
            ...         # Think that here is call to remote server by API.
            ...         # for example simple reduce is taken only to test
            ...         # that inheritance works fine
            ...         it = iter(args)
            ...         res = next(it)
            ...         for x in it:
            ...             res = f(res, x)
            ...         return res

        Try define service:
            >>> class ServiceAddition(ServiceBase):
            ...     class Meta:
            ...         name = 'Addition'
            ...
            ...     def add(self, a, b):
            ...         return self.do_reduce(lambda x,y: x+y, a, b)

        Define second service
            >>> class ServiceMul(ServiceBase):
            ...     class Meta:
            ...         name = 'Mul'
            ...
            ...     def mul(self, a, b):
            ...         return self.do_reduce(lambda x,y: x*y, a, b)

        And let's check what we have now
            >>> adder = mc.get_class('Addition')()
            >>> adder.do_reduce(lambda x,y: x+y, 2, 5)
            7
            >>> adder.add(2, 5)
            7
            >>> adder.mul(2, 5)
            Traceback (most recent call last):
            ...
            AttributeError: 'MyCoolClass' object has no attribute 'mul'
            >>> adder.do_reduce(lambda x, y: x * y, 2, 5)
            10
            >>> multiplier = mc.get_class('Mul')()
            >>> multiplier.do_reduce(lambda x, y: x * y, 2, 5)
            10
            >>> multiplier.do_reduce(lambda x,y: x+y, 2, 5)
            7
            >>> multiplier.mul(2, 5)
            10
            >>> multiplier.add(2, 5)
            Traceback (most recent call last):
            ...
            AttributeError: 'MyCoolClass' object has no attribute 'add'

        Let's try to get unregistered service
            >>> srv = mc.get_class('X')()
            Traceback (most recent call last):
            ...
            ValueError: There is no class registered for key 'X'
            >>> srv = mc.get_class('X', default=True)()
            >>> srv.do_reduce(lambda x,y: x+y, 2, 5)
            7

        And now let's check what base classes were used to build
        each instance of service

            >>> [b.__name__ for b in adder.__class__.__bases__]
            ['ServiceAddition', 'ServiceBase']
            >>> [b.__name__ for b in multiplier.__class__.__bases__]
            ['ServiceMul', 'ServiceBase']
            >>> [b.__name__ for b in srv.__class__.__bases__]
            ['ServiceBase']

        Check if get_registered_names works fine:

            >>> sorted(mc.get_registered_names())
            ['Addition', 'Mul']

        And the simple example of integration with ABC
        (or other metaclassess)::

            >>> import abc
            >>> from six.moves import collections_abc
            >>> mc = ExtensibleByHashType._("TestABC",
            ...                             with_meta=abc.ABCMeta,
            ...                             hashattr='name')
            >>> @six.add_metaclass(mc)
            ... class TestBase(collections_abc.Sequence):
            ...     def __init__(self, seq):
            ...         self.seq = seq
            ...     def __getitem__(self, index):
            ...         return self.seq[index]
            ...     def __len__(self):
            ...         return len(self.seq)
            ...     def count_x2(self, *args, **kwargs):
            ...        return self.seq.count(*args, **kwargs) * 2
            ...
            >>> class TestX3(TestBase):
            ...     class Meta:
            ...         name = 'X3'
            ...
            ...     def count_x3(self, *args, **kwargs):
            ...         return self.seq.count(*args, **kwargs) * 3
            ...
            >>> Test = mc.get_class(None, default=True)
            >>> test = Test([1, 1, 2])
            >>> test.count(1)
            2
            >>> test.count_x2(1)
            4
            >>> test.count_x3(1)
            Traceback (most recent call last):
            ...
            AttributeError: 'TestABC' object has no attribute 'count_x3'
            >>>
            >>> Test3 = mc.get_class('X3')
            >>> test3 = Test3([1, 1, 2])
            >>> test3.count_x3(1)
            6
            >>> test3.count_x2(1)
            4
    """
    @classmethod
    def _get_base_classes(mcs, name=None):
        if name is None:
            return mcs._base_classes
        return mcs._base_classes_hash[name] + mcs._base_classes

    @classmethod
    def _add_base_class(mcs, cls):
        """ Adds new class *cls* to base classes
        """
        # Do all magic only if subclass had defined required attributes
        if getattr(mcs, '_base_classes_hash', None) is not None:
            meta = getattr(cls, 'Meta', None)
            _hash = getattr(meta, mcs._hashattr, None)
            if _hash is None and cls not in mcs._get_base_classes():
                mcs._base_classes.insert(0, cls)
                mcs._generated_class = {}  # Cleanup all caches
            elif _hash is not None and cls not in mcs._get_base_classes(_hash):
                mcs._base_classes_hash[_hash].insert(0, cls)
                mcs._generated_class[_hash] = None

    @classmethod
    def _(mcs, cls_name='Object', with_meta=None, hashattr='_name'):
        """ Method to generate real metaclass to be used
            ::

                # Create metaclass *mc*
                mc = ExtensibleByHashType._("MyClass", hashattr='name')

                # Create class using *mc* as metaclass
                @six.add_metaclass(mc)
                class MyClassBase(object):
                    pass

            :param str cls_name: name of generated class
            :param class with_meta: Mix aditional metaclass in.
                                    (default: None)
            :param hashattr: name of class Meta attribute to be used as hash.
                             default='_name'
            :return: specific metaclass to track new inheritance tree
        """
        extype = super(ExtensibleByHashType, mcs)._(cls_name=cls_name,
                                                    with_meta=with_meta)

        class EXHType(extype):
            _hashattr = hashattr
            _base_classes_hash = collections.defaultdict(list)

            # Override it by dict to store diferent
            # base generated class for each hash
            _generated_class = {}

        return EXHType

    @classmethod
    def get_class(mcs, name, default=False):
        """ Generates new class to gether logic of all available extensions
            ::

                # Create metaclass *mc*
                mc = ExtensibleByHashType._("MyClass", hashattr='name')

                # Use metaclass *mc* to create base class for extensions
                @six.add_metaclass(mc)
                class MyClassBase(object):
                    pass

                # Create extension
                class MyClassX1(MyClassBase):
                    class Meta:
                        name = 'X1'

                # get default class
                MyClass = mc.get_class(None, default=True)

                # get specific class
                MyX1 = mc.get_class('X1')

            :param name: key to get class for
            :param bool default: if set to True will generate default class for
                                 if there no special class defined for such key
            :return: generated class for requested type
        """
        if default is False and name not in mcs._base_classes_hash:
            raise ValueError(
                "There is no class registered for key '%s'" % name)
        if mcs._generated_class.get(name, None) is None:
            cls = type(
                mcs._cls_name,
                tuple(mcs._get_base_classes(name)),
                {'_generated': True})
            mcs._generated_class[name] = cls
        return mcs._generated_class[name]

    @classmethod
    def get_object(mcs, *args, **kwargs):
        """ this method is not implemented for *ExtensibleByHashType* class
        """
        raise NotImplementedError(
            "this method is not implemented for ExtensibleByHashType class")

    @classmethod
    def get_registered_names(mcs):
        """ Return's list of names (keys) registered in this tree.
            For each name specific classes exists
        """
        return [k for k, v in six.iteritems(mcs._base_classes_hash) if v]


class TMeta(ExtensibleType):
    """ Helper metaclass to implement ability to use same class as base class
        for extensions and as class to create objects based on all subclasses
        of this class

        Used internaly by class Extensible class

        Example usage:
            >>> @six.add_metaclass(TMeta)
            ... class Root(object):
            ...     class ExtensibleMeta:
            ...         _extensible_meta_base = True
            ...

            Subclassing Root we could create separate extension
            tree/list. In this example all subclasses of CBase will
            extend CBase in a way as CBase was subclass of all of them
            >>> class CBase(Root): pass
            >>> [b.__name__ for b in type(CBase)._base_classes]
            ['CBase']
            >>> class C1(CBase): pass
            >>> [b.__name__ for b in type(CBase)._base_classes]
            ['C1', 'CBase']
            >>> class C2(CBase): pass
            >>> [b.__name__ for b in type(CBase)._base_classes]
            ['C2', 'C1', 'CBase']

            In same way we could create another tree/list of extensions
            >>> class XBase(Root): pass
            >>> [b.__name__ for b in type(XBase)._base_classes]
            ['XBase']
            >>> class X1(XBase): pass
            >>> [b.__name__ for b in type(XBase)._base_classes]
            ['X1', 'XBase']
            >>> class X2(XBase): pass
            >>> [b.__name__ for b in type(XBase)._base_classes]
            ['X2', 'X1', 'XBase']

            Test that initialization of new objects performed only once
            (such bug was present in versions <= 1.1.0)
            >>> class ZBase(Root):
            ...     def __init__(self):
            ...         if not hasattr(self, 'counter'):
            ...             self.counter = 1
            ...         else:
            ...             self.counter += 1
            >>> z0 = type(ZBase).get_class()()
            >>> z0.counter
            1
            >>> class Z1(ZBase):
            ...     pass
            >>> z1 = type(ZBase).get_class()()
            >>> z1.counter
            1
    """
    def __new__(mcs, name, bases, attrs):
        extensible_meta = attrs.pop('ExtensibleMeta', False)

        # all extension work done. Normal creation may be continued
        if getattr(mcs, '_extensible_meta_done', False):
            return super(TMeta, mcs).__new__(mcs, name, bases, attrs)

        # If we create extensible root class, no magic required
        if getattr(extensible_meta, '_extensible_meta_base', False):
            return super(TMeta, mcs).__new__(mcs, name, bases, attrs)

        with_meta = getattr(extensible_meta, 'with_meta', None)
        # If we create class that is subclass of 'Extensible' or\
        # other root class do all the magi:
        #  - Generate metaclass for class to be created
        #  - Add attribute that means "not futher extension magic required"
        #    (_extensible_meta_done)
        mc = mcs._(name, with_meta=with_meta)
        mc._extensible_meta_done = True
        if six.PY2:
            # set newly generated metaclass for this object
            attrs['__metaclass__'] = mc
        # Create new class with generated metaclass
        return mc(name, bases, attrs)


@six.add_metaclass(TMeta)
class Extensible(object):
    """ All direct subclasses of this class will be extensible through
        inheritance

        So to create new class that should be extensible just inherit it
        from this class:

            >>> class MyClass(Extensible): pass

        After this all subclasses of *MyClass* will extend it.
        For example, create simple extension which will add attribute and
        method to class:

            >>> class MyClassExtension(MyClass):
            ...     my_attr = 42
            ...     def my_method(self):
            ...         print ("Hello, %s" % self.my_attr)

        After this we expect that attributes and methods defined in extensions
        will be available in MyClass object:

            >>> my_obj = MyClass()
            >>> my_obj.my_attr
            42
            >>> my_obj.my_method()
            Hello, 42

        So as we see, we could extend any objects derived from Extensible
        class using simple inheritence with out any long code.
        This is useful for plugin or extension systems,
        making extension work when it just imported.
        But as disadvantage of this approach, we will get error when we try
        to access attributes of extensions from base class:

            >>> MyClass.my_attr
            Traceback (most recent call last):
            ...
            AttributeError: type object 'MyClass' has no attribute 'my_attr'

            >>> MyClass.my_method()
            Traceback (most recent call last):
            ...
            AttributeError: type object 'MyClass' has no attribute 'my_method'

        This happens because *Extensible* class implements some black magic
        using inheritance and metaclasses.
        Extensible class have overridden *__new__* method in the way when
        it creates instance not of base class but of automatically generated
        class which inherits from all its extensions.

            >>> [b.__name__ for b in my_obj.__class__.__bases__]
            ['MyClassExtension', 'MyClass']

        Thus any behavior of objects created by *MyClass* may be changed
        by extensions. And as one more thing, extensions that inherits from
        extensions will be extensions of base class,
        not extension of extension.
        So we could do things like:

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
        not be changed, they will not get new methods or attributes
        from new extensions

            >>> my_obj.my_attr
            42
            >>> my_obj.my_method()
            Hello, 42
            >>> my_obj.my_method_2()
            Traceback (most recent call last):
            ...
            AttributeError: 'MyClass' object has no attribute 'my_method_2'

        Test that initialization of new objects performed only once
        (such bug was present in versions <= 1.1.0)

            >>> class ZBase(Extensible):
            ...     def __init__(self):
            ...         if not hasattr(self, 'counter'):
            ...             self.counter = 1
            ...         else:
            ...             self.counter += 1
            >>> z0 = ZBase()
            >>> z0.counter
            1
            >>> class Z1(ZBase):
            ...     pass
            >>> z1 = ZBase()
            >>> z1.counter
            1

    """
    class ExtensibleMeta:
        _extensible_meta_base = True

    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_generated', False):
            return super(Extensible, cls).__new__(cls)
        gcls = type(cls).get_class()
        return gcls.__new__(gcls, *args, **kwargs)


if __name__ == '__main__':
    import doctest
    exit(doctest.testmod().failed)
