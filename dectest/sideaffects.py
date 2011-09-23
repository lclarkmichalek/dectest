"""
This module contains various side affect tests that can be registered with a
:class:`TestSuite`.
"""

import functools

class SideAffectTest():
    """
    A base class for other side affect tests.
    """
    name = ""
    
    def pre_test(self):
        """
        Called before the function that is being tested is run. An optional
        callback.
        """
        return
    
    def test(self):
        """
        The actuall test that will be run. Should return `True` for success,
        and `False` for fail.
        """
        raise NotImplementedError()
    
    def decorator(self, *args, **kwargs):
        """
        Is the decorator that is accessed at the attribute with the same name
        as the side affect test. As this is a decorator, it must return a
        function. If only the arguments are going to be used, and the function
        does not need to be modified, return
        :method:`SideAffectTest.blank_decorator`.
        """
        return self.blank_decorator
    
    @staticmethod
    def blank_decoratr(func):
        """
        A decorator that does nothing.
        """
        return func

class GlobalStateChange(SideAffectTest):
    """
    A side affect test for changes in global state.
    
    >>> ts = TestSuite("global state suite",
    ...     DictConfig({'testing':
    ...         {'sideaffects': ['dectest.sideaffects.GlobalStateChange']}}))
    >>> globalvar = 3
    >>> @ts.register("tc")
    ... @ts.tc.input(1)
    ... @ts.tc.globalstatechange({'globalvar': (lambda a, b: a + 1 == b)})
    ... def add(delta):
    ...     globalvar += delta
    ...
    >>> @ts.register("tc2")
    ... @ts.tc2.input(1)
    ... @ts.tc2.globalstatechange({'globalvar': 1})
    ... def set(i):
    ...     global globalvar
    ...     globalvar = i
    ...
    """
    name = "globalstatechange"
    
    func = None
    pre_call = {}
    tests = {}
    
    def pre_test(self):
        """
        Called before the tested function is called, so we use this to capture
        the global variables' state before the function is called.
        """
        for varname in self.tests:
            self.pre_call[varname] = self.func.__globals__[varname]
    
    def test(self):
        """
        Returns true if the `self.func.__globals__` is equal to 
        `self.initglobal.update(self.expectedglobal)`.
        """
        glob = self.func.__globals__
        for varname, test in self.tests.iteritems():
            if callable(test):
                if not test(self.pre_call[varname], glob[varname]):
                    return False
            else:
                if test != glob[varname]:
                    return False
        return True
    
    def decorator(self, tests):
        """
        Takes a dictionary mapping variable names to tester functions. Each
        variable given as a key will be retreived before and after the function
        is run, and both are then passed to the tester function. If the tester
        function returns `True`, then the test has passed.
        
        The dictionary may also have keys that are non callable values. If a
        value is found that isn't callable, it will just be compared for
        equality with the value of the associated variable after the tested
        function has been called.
        """
        self.tests = tests
        def dec(func):
            """
            Get the function, so as to retrieve the global state later.
            """
            self.func = func
            return func
        
        return dec

class ClassStateChange(SideAffectTest):
    """
    A side affect test for changes in a class' state.
    
    >>> ts = TestSuite("class state suite", DictConfig({'testing':
                {'sideaffects': ['dectest.sideaffects.ClassStateChange']}}))
    >>> class TestedClass():
    ...     a = 3
    ...     
    ...     @ts.register("tc", method=True)
    ...     @ts.tc.in(4)
    ...     @ts.tc.classstatechange({'a': 4})
    ...     def change_state(self, new_a):
    ...         self.a = new_a
    ...
    """
    
    name = "classstatechange"
    
    def decorator(self, tests):
        """
        Takes a dict of items that should be in the class' namespace, and
        stores them for use by the :class:`ClassStateChange` later.
        """
        self.tests = tests
        self.f_state = {}
        self.s_state = {}
        
        def dec(func):
            """
            Get the function, to make the class state accessible later.
            """
            # We need to get the states like this as we can't get them from
            # the func object, as it is unbound, so has no __self__ attribute.
            @functools.wraps(func)
            def inner(*args, **kwargs):
                if not self.f_state:
                    for varname in self.tests:
                        self.f_state[varname] = getattr(args[0], varname)
                out = func(*args, **kwargs)
                if not self.s_state:
                    for varname in self.tests:
                        self.s_state[varname] = getattr(args[0], varname)
                return out
            
            return inner
        return dec
    
    def test(self):
        """
        Checks that the state has changed as determined by the argument passed
        to the decorator function.
        """
        for varname, tester in self.tests.items():
            if callable(tester):
                if not tester(self.f_state[varname], self.s_state[varname]):
                    return False
            else:
                if not tester == self.s_state[varname]:
                    return False
        
        return True
