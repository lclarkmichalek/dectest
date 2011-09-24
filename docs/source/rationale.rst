Rationale
=========

Lazy testing
------------

Setting up a test enviroment can be a pain. Instanstantiating objects, clearing
datastores, coordinating different components. And generally we have some lovely
testing framework that the language provides, so we end up writing lousey bash
scripts to setup, run, and tear down our test enviroments. These bash
scripts don't give us very much flexibility, as bash usually isn't our primary
programming language, and we don't want to spend forever writing them. All in
all this leads to a rather suboptimal situation.

Dectest gets around this problem by using your standard development enviroment
(which generally developers put a lot more effort into getting into a slick
operation than they do their testing enviroments). By opertunisticly testing,
that is, testing a function when it is run, we can intergreat testing into the
main program, we can stop testing being some secondary task, and make it a core
process.

Decorator testing
-----------------

Decorators are a lovely tool. They allow for crazy feats of metaprogramming, and
can be an incredibly simple way to expand the functionality of a function or
method. However, as far as I can see, it has never been applied to testing,
which seemed odd to me. If you are writing good, modular code then many of
the standard unit tests you might write would come down to two main things:
checking that output from the function is correct, and making sure that any 
changes to state are as expected. As the unit of encapsulation here is a
function, decorators make a lot of sense. Dectest is built around this idea,
and it provides a way to convert almost 100% of standard function based
unittests into a few lines of decorators at the head of a function.

This does come with some downsides, for example dectest only provides the most
generic of test for side affects, and the user will usually need to write a
small amount of code to configure the dectest system to their own needs. However
one of the key goals of dectest is to fit into almost any system. In some
frameworks, such as Django, there is substantial support for testing; with
dectest that should not be needed.

On demand testing
-----------------

Tests arn't generally run in production enviroments. Tests actually arn't
usually run in development enviroments. They usually end up being run in their
own 'testing' enviroments, which usually differ slightly from other enviroments.
Every difference between testing enviroments and production enviroments gives
the test suite another opertunity to present different results, leading to very
hard to find bugs. When the tests for a function pass, but in production it
crashes and burns, then you end up with a rather hard to find bug.

Dectest presents another option. In addition to running tests lazily in a
development enviroment, it makes it possible to turn on tests globaly or for a
subset of functions at runtime. This means that if you see an increase in the
number of errors in one area, you can turn on testing for the affected
functions, get your results, and then turn off testing again, all without
restarting the process. This is incredibly usefull if you are say, running a
website, and see that there is one page with an anomolous probability of error.
Conventionally, you would try and replicate this in your development or testing
enviroment, an often futile, time consuming exersise.
