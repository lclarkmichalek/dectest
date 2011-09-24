.. module:: dectest.sideaffects

Side Affect Tests
=================

Side affects are important to test for, as in almost any non-functional
language, they are used extensivly. dectest provides generic tests to test for
different kinds of side affects.

Base side affect test
---------------------

This class provides a blank side affect test as an example as what a side affect
test should provide. 

.. autoclass:: SideAffectTest

Side affect tests
-----------------

Some situations are incredibly common, and thus dectest provides built in
classes to deal with them.

.. autoclass:: GlobalStateChange

.. autoclass:: ClassStateChange
