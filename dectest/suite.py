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
        self._config.set_logger(logger)
        self._logger = logger
        self._name = name
        
        self._testcases = {}
        self._tests = {}
        
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
        
        
        .. warning:: If the decorated object is a method of a class, then the
           ``method`` argument **must** be true. This is because dectest cannot
           obtain a copy of an instance of the class untill runtime, so we need
           to know if to catch the `self` variable.
        """
        if name in self._testcases:
            self._logger.warning("Cannot register the same test case twice.")
            return self._blank_decorator
        
        tc = TestCase(self._config, self._logger, 
                      self._sideaffect_tests, method, name)
        
        def decorator(func):
            """
            The decorator for the test function.
            """
            # If we've seen this function before
            if hasattr(func, "_original_function"):
                actuall_func = func._original_function
            # or if it's brand new
            else:
                actuall_func = func
                actuall_func.tested = False
            
            tc.set_func(actuall_func)
            
            if not actuall_func in self._tests:
                self._tests[actuall_func] = [tc]
            else:
                self._tests[actuall_func].append(tc)
            
            @functools.wraps(func)
            def test_dec(*args, **kwargs):
                if not actuall_func.tested and self._run_tests and \
                        self._config.get_bool("testing", "testasrun"):

                    if self._tests[actuall_func][0].needs_self():
                        for tc in self._tests[actuall_func]:
                            if tc.needs_self():
                                tc.set_self(args[0])
                    
                    self._test_function(actuall_func)
                    
                    actuall_func.tested = True
                
                return func(*args, **kwargs)
            test_dec._original_function = actuall_func
            
            return test_dec
        
        self._testcases[name] = tc
        return decorator
    
    def _test_function(self, func):
        """
        Runs all of the test cases associated with the given function.
        """
        testcases = self._tests[func]
        
        for tc in testcases:
            out = tc.test()
            self._log_result(tc.name, out)
    
    def _log_result(self, name, passed):
        """
        Logs the result of a test of a function.
        """
        print "Test case {0} ".format(name) + ("passed" if passed else "failed")
    
    def __getattr__(self, name):
        if name in self._testcases:
            return self._testcases[name]
        else:
            raise AttributeError("No test case {0}".format(name))


class TestCase():
    """
    An invididual test case, containing all the information it needs to be
    tested.
    """
    
    def __init__(self, config, logger, activated_sideaffects, method, name):
        self._raw_func = None
        self._method = method
        self._self = None
        self._input = (), {}
        self._output = None
        self._sideaffects = []
        self._activated_sideaffects = activated_sideaffects
        self.name = name
        
        self._config = config
        self._logger = logger
    
    def input(self, *args, **kwargs):
        """
        Sets the input to the function in the test case.
        """
        self._input = args, kwargs
        
        return self._blank_decorator
    
    def out(self, output=None):
        """
        Sets the expected/predicted output of the function in the test case.
        """
        self._output = output
        
        return self._blank_decorator
    
    def set_func(self, func):
        """
        Sets the function that is being tested.
        """
        self._raw_func = func

    def needs_self(self):
        """
        Returns ``True`` if the test case needs a value for self, and does not
        have one set. Returns ``False`` otherwise.
        """
        return self._method and not self._self
    
    def set_self(self, self_):
        """
        Sets the "self" of the method that is being tested.
        """
        self._self = self_
    
    def test(self):
        """
        Runs the test case and returns ``True`` if the test case passed,
        otherwise ``False``.
        """
        self._pre_test()
        
        out = self._run_test()
        
        self._post_test()
        
        return out
    
    def _pre_test(self):
        """
        Runs any global pre test functions, along with the
        :meth:`~dectest.sideaffects.SideAffectTest.pre_test` method on every
        side affect test in use.
        """
        pretest = self._config.get("testing", "pretest")
        if pretest:
           obj = self._config.get_python(pretest)
           if callable(obj):
               obj()
           else:
               self._logger.warning("Pre-test callback was not callable")
        
        for test in self._sideaffects:
            test.pre_test()
    
    def _run_test(self):
        """
        Runs the actuall test. Returns ``True`` on pass, otherwise ``False``.
        """
        args, kwargs = self._input
        
        if self._method:
            args = (self._self,) + args
        
        output = self._raw_func(*args, **kwargs)
        
        passed = True
        passed = passed and output == self._output
        
        for test in self._sideaffects:
            passed = passed and test.test()
        
        return passed
    
    def _post_test(self):
        """
        Runs any global post test functions.
        """
        posttest = self._config.get("testing", "posttest")
        if posttest:
           obj = self._config.get_python(posttest)
           if callable(obj):
               obj()
           else:
               self._logger.warning("Post-test callback was not callable")
    
    def __getattr__(self, name):
        """
        Make the side affect tests accessable at their given names.
        """
        if name in self._activated_sideaffects:
            sat = self._activated_sideaffects[name](self._logger)
            self._sideaffects.append(sat)
            return sat.decorator
        raise AttributeError()
    
    @staticmethod
    def _blank_decorator(func):
        """
        Just a decorator that does nothing.
        """
        return func
