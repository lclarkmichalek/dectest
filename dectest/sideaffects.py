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
