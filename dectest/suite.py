"""
The main test suite class, class:`TestSuite` is found in this module.
"""

import sys

class TestSuite():
    """
    This is the main test suite class. It should be asigned to a variable at
    import time, and can then be used to reference decorators that can be used
    for detailing any tests created.
    """
    __run_tests = lambda: True
    
    def __init__(self, name):
        """
        Initialises the test suite, mainly populating some hidden attributes.
        """
        self.__name = name
        self.future_tests = {}
    
    def test(self):
        """
        Runs all the test cases.
        """
        if not self.__run_tests():
            return
        
        print "Test Suite '{0}'".format(self.__name)
        print "=" * 80
        fail = 0
        for name, tc in self.future_tests.iteritems():
            args, kwargs = tc["input"]
            output = tc["func"](*args, **kwargs)
            if output != tc["output"]:
                sys.stdout.write('f')
                fail += 1
            else:
                sys.stdout.write('.')
        print "\n",
        print "=" * 80
        if fail == 0:
            print "All tests passed successfully"
        else:
            if fail == 1:
                print "1 test failed"
            else:
                print "{0} tests failed".format(fail)
    
    def register(self, name):
        """
        Creates a new test case, with the given name. The :class:`TestCase`
        object will be availible as an attribute of the :class:`TestSuite` with
        the same name as the new test case.
        
        >>> ts = TestSuite()
        >>> @ts.register("tc")
        ... def test():
        ...     return
        ...
        >>> type(ts.tc)
        <class 'dectest.suite.TestCase'>
        
        """
        self.future_tests[name] = {}
        def decorator(func):
            """
            The decorator for the test function.
            """
            self.future_tests[name]["func"] = func
            return func
        
        return decorator
    
    @classmethod
    def set_run_tests(klass, func):
        """
        Sets the function that will determine whether tests are run or not. The
        function is called with no arguments, and should return a boolean with
        `True` indicating that tests should be run.
        """
        klass.__run_tests = func
    
    def __getattr__(self, name):
        return TestCase(self, name)

class TestCase():
    """
    An individual testcase. Automatically created by
    :method:`TestSuite.register`.
    """
    def __init__(self, parent, name):
        """
        Initialises state.
        """
        self.name = name
        self.parent = parent
        if name not in self.parent.future_tests:
            self.parent.future_tests[self.name]["input"] = (), {}
            self.parent.future_tests[self.name]["output"] = None

    
    def input(self, *args, **kwargs):
        """
        Sets the input for the test function when testing commenses.
        """
        self.parent.future_tests[self.name]['input'] = (args, kwargs)
        
        return self._blank_decorator
    
    def out(self, out=None):
        """
        Sets the expected output of the test function.
        """
        self.parent.future_tests[self.name]["output"] = out
        
        return self._blank_decorator

    def setfunc(self, func):
        """
        Sets the function to test.
        """
        self.parent.future_tests[self.name]["func"] = func
    
    def test(self):
        """
        Runs the specific test case.
        """
        args, kwargs = self.input
        assert self.test_func(*args, **kwargs) == self.out, \
               "TestCase {0} failed".format(self.name)
    
    @staticmethod
    def _blank_decorator(func):
        """
        Just a decorator that does nothing.
        """
        return func
