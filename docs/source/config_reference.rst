Config Reference
================

dectest is designed to be highly configurable, and as such it has many
configuration nodes. Each option is listed below.

.. note:: You may hear the term "python name". The python name of something (as
   defined by me) is the full module name, followed by the location of the
   object inside that module. So for example, the function ``abspath`` in the
   ``os.path`` module would have the python name of ``os.path.abspath``

The ``testing`` section
-----------------------

The testing configuration section is probabaly the largest, as it deals with
dectest's primary function.

``runtests``
::::::::::::

+----------+----------------------+-----------------+
|Name      | Type                 | Default         |
+==========+======================+=================+
|runtests  | boolean              | True            |
+----------+----------------------+-----------------+

This option controls if tests are run at all. If this option is ``False``, then
calling an untested method will not test it, and manually calling testing
methods will not run the tests either.

``testasrun``
:::::::::::::

+----------+----------------------+-----------------+
|Name      | Type                 | Default         |
+==========+======================+=================+
|testasrun | boolean              | True            |
+----------+----------------------+-----------------+

The testasrun option controls wether or not dectest tests functions as they are
run, or if it just waits untill the user/application calls the
:meth:`~dectest.suite.TestSuite.test` method.

``sideaffects``
:::::::::::::::

+------------+----------------------+-----------------+
|Name        | Type                 | Default         |
+============+======================+=================+
|sideaffects | list of str          | []              |
+------------+----------------------+-----------------+

This options dictates which side affect tests are activated. It should be a list
of the python names of the side affect tests. dectest will import each class and
make it availible at the attribute of
:class:`~dectest.suite.TestSuite.TestClass` with a name equal to the value of
the ``name`` attribute of the side affect class.

``pretest``
:::::::::::

+------------+----------------------+-----------------+
|Name        | Type                 | Default         |
+============+======================+=================+
| pretest    | str                  | ''              |
+------------+----------------------+-----------------+

The pretest option is the python name of a function that will be run before any
tests are run. This option is globally enforced, and will **allways** be called
before a test is run.


``posttest``
::::::::::::

+------------+----------------------+-----------------+
|Name        | Type                 | Default         |
+============+======================+=================+
| posttest   | str                  | ''              |
+------------+----------------------+-----------------+

The reverse of the pretest option; a function that will be run after any tests
are run.
