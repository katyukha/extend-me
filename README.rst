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

