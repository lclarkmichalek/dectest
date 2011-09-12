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
    __run_tests = staticmethod(lambda: True)
    sideaffect_tests = {}
    
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
        fails = 0
        for name, tc in self.future_tests.iteritems():
            args, kwargs = tc["input"]
            output = tc["func"](*args, **kwargs)
            failed = False
            failed = failed or not output == tc["output"]
            for test in tc["sideaffects"]:
                failed = failed or not test.test()
            
            if failed:
                sys.stdout.write('f')
                fails += 1
            else:
                sys.stdout.write('.')
        print "\n",
        print "=" * 80
        if fails == 0:
            print "All tests passed successfully"
        else:
            if fails == 1:
                print "1 test failed"
            else:
                print "{0} tests failed".format(fails)
    
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
        self.future_tests[name]["input"] = (), {}
        self.future_tests[name]["output"] = None
        self.future_tests[name]["sideaffects"] = []
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
    
    @classmethod
    def activate_sideaffect_test(klass, test_klass):
        """
        Activates a sideaffect test which test cases can then use.
        """
        klass.sideaffect_tests[test_klass.name] = test_klass
    
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
    
    def __getattr__(self, name):
        if name in self.parent.sideaffect_tests:
            sat = self.parent.sideaffect_tests[name]()
            self.parent.future_tests[self.name]["sideaffects"].append(
                sat)
            return sat.decorator

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
