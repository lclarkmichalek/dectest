"""
The main test suite class, :class:`TestSuite` is found in this module.
"""

import functools
import logging
import sys

from . import config as mconfig

class TestSuite():
    """
    This is the main test suite class. It should be asigned to a variable at
    import time, and can then be used to reference decorators that can be used
    for detailing any tests created.
    """
    
    class TestCase():
        """
        An individual testcase. Generated on command, as a wrapper for the
        data stored by the :class:`TestSuite`
        """
        def __init__(self, name, parent):
            """
            Initialises state.
            """
            self.name = name
            self.parent = parent
            
        def input(self, *args, **kwargs):
            """
            Sets the input for the test function when testing commenses.
            """
            self.parent._future_tests[self.name]['input'] = (args, kwargs)
            
            return self._blank_decorator
        
        def out(self, out=None):
            """
            Sets the expected output of the test function.
            """
            self.parent._future_tests[self.name]["output"] = out
            
            return self._blank_decorator
        
        def __getattr__(self, name):
            if name in self.parent._sideaffect_tests:
                sat = self.parent._sideaffect_tests[name]()
                self.parent._future_tests[self.name]["sideaffects"].append(
                    sat)
                return sat.decorator
            raise AttributeError()
            
        def setfunc(self, func):
            """
            Sets the function to test.
            """
            self.parent._future_tests[self.name]["func"] = func
            
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
    
    _sideaffect_tests = {}
    
    def __init__(self, name, config=None, logger=None):
        """
        Initialises the test suite, mainly populating some hidden attributes.
        """
        if config is None:
            config = mconfig.DefaultConfig()
        if logger is None:
            logger = logging.getLogger(name)
        
        self._config = config
        self._logger = logger
        self._name = name
        self._future_tests = {}
        
        for name in self._config.get_list('testing', 'sideaffects') or []:
            sat = self._config.get_python(name)
            
            if not sat:
                self._logger.warning("Could not find side affect test named" + 
                                     name)
            else:
                self._sideaffect_tests[sat.name] = sat
        
        self._run_tests = self._config.get_bool('testing', 'runtests') or \
            self._config.get_default('testing', 'runtests')
    
    def test(self):
        """
        Runs all the test cases.
        """
        if not self._run_tests:
            return
        
        print "Test Suite '{0}'".format(self._name)
        print "=" * 80
        fails = 0
        for name, tc in self._future_tests.iteritems():
            for test in tc["sideaffects"]:
                test.pre_test()
            
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
    
    def register(self, name, method=False):
        """
        Creates a new test case, with the given name. The :class:`TestCase`
        object will be availible as an attribute of the :class:`TestSuite` with
        the same name as the new test case.
        
        >>> ts = TestSuite()
        >>> @ts.register("tc")
        ... def test():
        ...     return
        ...
        >>> ts.tc
        <dectest.suite.TestCase instance at 0xb71fcc2c>
        
        
        .. important:: If the decorated object is a method of a class, then the
           `method` argument must be true. This is because dectest cannot obtain
           a copy of an instance of the class untill runtime, so we need to know
           if to catch the `self` variable.
        """
        if name in self._future_tests:
            
            print("Cannot register the same test case twice.")
            return self._blank_decorator
        
        self._future_tests[name] = {}
        self._future_tests[name]["input"] = (), {}
        self._future_tests[name]["output"] = None
        self._future_tests[name]["sideaffects"] = []
        def decorator(func):
            """
            The decorator for the test function.
            """
            self._future_tests[name]["func"] = func
            
            self._future_tests[name]["method"] = method
            self._future_tests[name]["self"] = None
            
            func.tested = False
            
            @functools.wraps(func)
            def test_dec(*args, **kwargs):
                if method and not self._future_tests[name]["self"]:
                    self._future_tests[name]["self"] = args[0]
                
                if not func.tested and self._run_tests and \
                        self._config.get_bool("testing", "testasrun"):
                    self._setup_test(name)
                    
                    passed = self._test_func(name)
                    
                    self._teardown_test(name)
                    
                    self._log_result(name, passed)
                    
                    func.tested = True
                
                return func(*args, **kwargs)
            return test_dec
        
        return decorator
    
    def _setup_test(self, name):
        """
        Runs all the pre_test methods on all the registered sideaffect tests.
        Allso calls the pre test callback, which can be set at configuration 
        value `testing.pretest`.
        """
        pretest = self._config.get("testing", "pretest")
        if pretest:
           obj = self._config.get_python(pretest)
           if callable(obj):
               obj()
           else:
               self._logger.warning("Pre-test callback was not callable")
        
        tc = self._future_tests[name]
        for test in tc["sideaffects"]:
            test.pre_test()
    
    def _test_func(self, name):
        """
        Runs the test case with name `name`. Returns `True` if the test case
        passed, `False` otherwise.
        """
        tc = self._future_tests[name]
        
        args, kwargs = tc["input"]
        
        if tc["method"]:
            args = (tc["self"],) + args
        
        output = tc["func"](*args, **kwargs)
        
        failed = False
        failed = failed or not output == tc["output"]
        
        for test in tc["sideaffects"]:
            failed = failed or not test.test()
        
        return not failed
    
    def _teardown_test(self, name):
        """
        Tears down after the test has been run.
        
        This runs the post test callback, which can be set at confiuration value
        `testing.posttest`.
        """
        posttest = self._config.get("testing", "posttest")
        if posttest:
           obj = self._config.get_python(posttest)
           if callable(obj):
               obj()
           else:
               self._logger.warning("Post-test callback was not callable")
    
    def _log_result(self, name, passed):
        """
        Logs the result of a test of a function.
        """
        print "Test case {0} ".format(name) + ("passed" if passed else "failed")
    
    def __getattr__(self, name):
        if name in self._future_tests:
            return self.TestCase(name, self)
        else:
            raise AttributeError("No test case {0}".format(name))

