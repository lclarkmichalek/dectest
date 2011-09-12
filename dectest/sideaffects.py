"""
This module contains various side affect tests that can be registered with a
:class:`TestSuite`.
"""

class SideAffectTest():
    """
    A base class for other side affect tests.
    """
    name = ""
    
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
    """
    name = "globalstatechange"
    
    func = None
    change = {}
    
    def test(self):
        """
        Returns true if the `self.func.__globals__` is equal to 
        `self.initglobal.update(self.expectedglobal)`.
        """
        glob = self.func.__globals__
        for key in self.change:
            if self.change[key] != glob[key]:
                return False
        return True
    
    def decorator(self, change):
        """
        Takes a dict of items that should be in the global state, and stores
        them for the :method:`test` to check.
        """
        self.change = change
        def dec(func):
            """
            Get the function, so as to retrieve the global state later.
            """
            self.func = func
            return func
        
        return dec
