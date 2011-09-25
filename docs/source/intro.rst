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

Config options
..............

For a complete list of all the configuration nodes that dectest listens to,
inspect the ``DEFAULTS`` in the :mod:`~dectest.config` module. However, there
are some values that are exceedingly usefull to set, these are listed below:

+----------+-------------+------+---------------------------------------------+
| Section  |     Item    | type | Effect                                      |
+==========+=============+======+=============================================+
| testing  | runtests    | bool | If true, tests are run                      |
+----------+-------------+------+---------------------------------------------+
| testing  | testasrun   | bool | If true, tests are run as the function they |
|          |             |      | decorate is run                             |
+----------+-------------+------+---------------------------------------------+
| testing  | sideaffects | list | A list of the python names of the side      |
|          |             |      | affect tests you want activated             |
+----------+-------------+------+---------------------------------------------+
| testing  | pretest     | str  | The python name of a function to be run     |
|          |             |      | before any tests are run                    |
+----------+-------------+------+---------------------------------------------+
| testing  | posttest    | str  | The python name of a function to be run     |
|          |             |      | after any tests are run                     |
+----------+-------------+------+---------------------------------------------+

For a full reference, see the :doc:`config_reference`.

A note on types
^^^^^^^^^^^^^^^

In general, dectest will try to do "the right thing" with regard to types. For
instance, if the specified type for an option is ``bool`` and the configuration
value has the type ``str``, then dectest will run through a mapping from str to
bool trying to convert the types. For more information on this specific example,
see the documentation for :meth:`~dectest.config.ConfigInterface.get_bool`.
Similarly, if a config option asks for a python name, but is given a python
object instead, then it will adapt without complaint.

Side affect tests
-----------------

Side affects are vital to test for, so we need to have a way to do so with
decorators. Enter the creativly named "side affect tests". Side affect test are
generic tests that can be enabled in config and then used as decorators. The
easiest way to explain this is probabaly via an example::

    #!/usr/bin/python2.7
    # side_affect_test.py
    from dectest import TestSuite, DictConfig
    
    config = {
        'testing': {
	     'sideaffects': ['dectest.sideaffects.GlobalStateChange'],
             }
         }
    
    testsuite = TestSuite(__name__, config=DictConfig(config))
    
    global var
    var = 3
    
    @testsuite.register("global_change")
    @testsuite.global_change.input(3)
    @testsuite.global_change.globalstatechange({'var': 3})
    def set_state(i):
        var = i

Importing this and running the ``set_state`` function will result in a passed
test. We can also give the sideaffect test a function to test for relative
changes in state::

    @testsuite.register("global_change")
    @testsuite.global_change.input(1)
    @testsuite.global_change.globalstatechange(
                                  {'var': (lambda a, b: a + 1 == b)})
    def increment_state(i):
        var += i

The lambda (or function) will be passed the value of the variable before the
function is called, and then the value after the function is called.

Writing side affect tests
:::::::::::::::::::::::::

dectest only provides two (very generic) side affect tests by default:
:class:`~dectest.sideaffects.GlobalStateChange` and 
:class:`~dectest.sideaffects.ClassStateChange`. This might seem worrying, as
neither provides any kind of specialised testing. However, it is very easy to
write side affect tests. A base class
:class:`~dectest.sideaffects.SideAffectTest` is provided, which gives sane
defaults, allowing the side affect test developer to override only the methods
he needs.

The methods that dectest will call at the appropriate times are:

* ``decorator(*args, **kwargs)`` - The decorator provided to users to activate
  the side affect test.
* ``test()`` - The actual testing function, should return ``True`` if the test
  has passed, otherwise ``False``.
* ``pre_test()`` - Called before the tested function is run.

It also looks for two attributes

* ``name`` - The name of the side affect test (the attribute it will be 
  accessible from from the :class:`~dectest.suite.TestCase` class). This
  attribute is required, without it your side affect test will not work.
* ``needs_instance`` - Does the test case need a copy of the instance the
  tested function is bound to.

``decorator``
.............

The decorator function is exposed to the user by the test case. For example, the
decorator function of the :class:`~dectest.sideaffects.ClassStateChange` class
might be exposed to the user as ``testsuite.testcase.classtatechange``.
Let's use an example here (output is in the comments)::

    #!/usr/bin/python2.7
    # first_side_affect_test.py
    from dectest import TestSuite, DictConfig
    from dectest.sideaffects import SideAffectTest
    
    class FirstSideAffectTest(SideAffectTest):
        name = "firsttest"
	
	def decorator(self, *args, **kwargs):
	    print args, kwargs
	    def inner_decorator(function):
	        print "Got function " + function
		
		def wrapper(*args, **kwargs):
		    print "Running function"
		    return function(*args, **kwargs)
		return wrapper
	    return inner_decorator
    
    config = {'testing': {'sideaffects': [FirstSideAffectTest]}}
    ts = TestSuite(__name__, config=DictConfig(config))
    
    @ts.register("tc")
    @ts.tc.firsttest(1, a=3)
    def foo():
        return
    # (1,), {'a': 3}
    # Got function <function foo at 0x9624304>
    
    foo()
    # Running function

This example shows two things. The first is how the ``name`` attribute of a
side affect test affects the attribute of the test case it is accessible from;
the ``name`` attribute of the the ``FirstSideAffectTest`` class is
``"firsttest"``, thus we access it's decorator via ``ts.tc.firsttest``. The
second thing that this example shows is just how many levels of nesting are 
required if you want to overwrite the actuall function that is being decorated.
