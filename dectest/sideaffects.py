"""
This module contains various side affect tests that can be registered with a
:class:`TestSuite`.
"""

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
    
    >>> ts = TestSuite("global state suite")
    >>> ts.activate_sideaffect_test(GlobalStateChange)
    >>> globalvar = 3
    >>> @ts.register("tc")
    ... @ts.tc.input(1)
    ... @ts.tc.globalstatechange({'globalvar': (lambda a, b: a + 1 == b)})
    ... def add(delta):
    ...     globalvar += delta
    ...
    >>> ts.test()
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
    
    >>> ts = TestSuite("class state suite")
    >>> ts.activate_sideaffect_test(ClassStateChange)
    >>> class TestedClass():
    ...     a = 3
    ...     
    ...     @ts.register("tc")
    ...     @ts.tc.in(4)
    ...     @ts.tc.classstatechange({'a': 4})
    ...     def change_state(self, new_a):
    ...         self.a = new_a
    ...
    """
    
    name = "classstatechange"
    
    def decorator(self, change):
        """
        Takes a dict of items that should be in the class' namespace, and
        stores them for use by the :class:`ClassStateChange` later.
        """
        self.change = change
        
        def dec(func):
            """
            Get the function, to make the class state accessible later.
            """
            self.func = func
            return func
        return dec
    
    def pre_test(self):
        """
        Checks that all the variables that need to be checked for changes
        are in the class state.
        """
        self.failed = False
        for varname in self.change:
            if not hasattr(self.func.__self__, varname):
                self.failed = True
    
    def test(self):
        """
        Checks that the state has changed as determined by the argument passed
        to the decorator function.
        """
        if self.failed:
            return False
        
        for varname, newval in self.change:
            if not getattr(self.func.__self__, varname) == newval:
                return False
        
        return True
