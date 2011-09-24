User Guide
==========

Dectest is very simple to setup, and can fit in most situations. This guide
should help you get a grasp of how to setup dectest, how to use dectest, and
how to customise dectest.

Installation
------------

Installation is simple enough. First get the code from dectest's git
repository::

    $ git clone git://github.com/bluepeppers/dectest.git
    $ cd dectest

After that, build and install dectest with the ``setup.py`` file. You will need
root permissions to install dectest, unless you are using a virtual
enviroment::

    $ python2.7 setup.py build
    $ sudo python2.7 setup.py install

Usage
-----

Dectest is found in the :mod:`dectest` package. Though the package has multiple
modules inside it, for simple use, just importing :mod:`dectest` should be enough.

TestSuite
:::::::::

The main class you will deal with is the :class:`~dectest.suite.TestSuite`
class. This is the class that is responsible for collecting information on the
defined tests, coordinating the efforts of side affect tests, making sure your
configuration values are heeded, and generally making things work. It only
requires a name to start. The name is used as identify the test suite in the
output, and can be completely arbitrary. We suggest using the name of the
current module, ``__name__``::

    #!/usr/bin/python2.7
    # dectest_example_one.py
    import dectest
    
    testsuite = dectest.TestSuite(__name__)

Now for the fun part, actually testing something. First we need to register a
new test case, using the :meth:`~dectest.suite.TestSuite.register` decorator.
After that, we need to define the input and output for the test case. These will
default to ``None``. We use the :meth:`~dectest.suite.TestSuite.TestCase.input`
and the :meth:`~dectest.suite.TestSuite.TestCase.out` decorators for this::
    
    @testsuite.register("testcase")
    @testsuite.testcase.input(3, i=2)
    @testsuite.testcase.out(5)
    def increment(value, incrementer=1):
        return value + incrementer

And there we go, our first function marked up for testing. Notice how we found
the test case at the ``testcase`` attribute. Test cases can be accessed with
the same name as the call to :meth:`~dectest.suite.TestSuite.register` that
created them.

So we've marked up the test, how do we run it? By running the function! By
default, dectest tests lazily. Importing the above file and running the
increment function should result in output of "Test case testcase has passed".
However, this will only happen once; dectest tries to minimize it's overhead by
only testing the first time a function is called::

    >>> import dectest_example_one
    >>> a = increment(7, 1)
    Test case testcase has passed
    >>> print a
    8
    >>> a = increment(7, 1)
    >>> print a
    8

Configuration
:::::::::::::

dectest is *very* configurable. It supports multiple configuration formats, and
it is very easy to write a new one. By default it uses the
:class:`~dectest.config.DefaultConfig` class, but dectest provides two other
usefull config methods, namely :class:`~dectest.config.DictConfig` and
:class:`~dectest.config.PythonFileConfig`. Both these can be found in the
:mod:`dectest.config` module.

To start using your own config, pass it as the ``config`` keyword argument to
the :class:`~dectest.suite.TestSuite` initialiser.

DictConfig
..........

The :class:`~dectest.config.DictConfig` class is very simple to use. Simply pass
your config in the format of a dictionary to the initialiser. For example::

    >>> from dectest.config import DictConfig
    >>> config = {
    ...    'section1': {
    ...        'item1': True
    ...	       }
    ...	   }
    >>> dictconfig = DictConfig(config)
    >>> print dictconfig.get('section1', 'item1')
    True

PythonFileConfig
................

:class:`~dectest.config.PythonFileConfig` is arguably more powerfull than the
DictConfig class shown above. The PythonFileConfig takes the path to a python
module as an argument to its initialiser. It then imports that module, and
extracts the config values from it. Here is an example config file::

    # /tmp/test_config.py
    
    class section1:
        item1 = 3
    
    class section2:
        item2 = 4

We can then load the PythonFileConfig in an interactive interpreter, and test it
out::

    >>> from dectest.config import PythonFileConfig
    >>> pfconfig = PythonFileConfig("/tmp/test_config.py")
    >>> print pfconfig.get("section1", "item1")
    3
    >>> print pfconfig.get("section2", "item2")
    4
