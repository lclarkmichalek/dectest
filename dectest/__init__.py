"""
The base dectest package. Provides a shortcut to several usefull classes. The
:class:`~.suite.TestSuite` class is imported, as it is vital to any use of
dectest. Two different config methods are imported: :class:`~.config.DictConfig`
and :class:`~.config.PythonFileConfig`, along with two side affect tests from
the :mod:`~.sideaffects` module: :class:`~.sideaffects.GlobalStateChange` and
:class:`~.sideaffects.ClassStateChange`.
"""
from .config import DictConfig, PythonFileConfig
from .suite import TestSuite
from .sideaffects import GlobalStateChange, ClassStateChange
