"""
The configurations system for dectest. Offers two different methods of
configuration; as a python file or from a dict. Each method is implemented in a
different class, but they all provide the same interface.
"""

import imp
import re

DEFAULTS = {
    'testing': {
        'testasrun': True,
        'sideaffects': [],
        'runtests': True,
        'pretest': None,
        'posttest': None,
        }
    }

class DummyLogger():
    """
    A dummy logger to allow quite degregation.
    """
    def __getattr__(self, _):
        """
        Return a callable that does nothing at all.
        """
        return lambda *args, **kwargs: None

class ConfigInterface():
    """
    An interface that all classes implementing config methods should inherit.
    
    Methods that implementing classes must provide the following
    methods/properties. More information on the required behaviour of each
    attribute can be found in their individual documentation in this class.
    
    * store
    * reload() (optional)
    """
    
    _logger = DummyLogger()
    
    @property
    def store(self):
        """
        This property must be implemented by all classes implementing the config
        interface. It should be a mapping of section names to a mapping of
        item names to values.
        If that dosn't make sense, this may help:
        
        >>> conf = DefaultConfig()
        >>> conf.store
        {'section': {'item1': True, 'item2': 3, 'item4': "foo"}}
        """
        raise NotImplementedError()
    
    def reload(self):
        """
        This method can be implemented by implementing classes, though it is
        optional. When called it should reload the config from it's source.
        """
        return
    
    def get(self, section_name, item_name):
        """
        Returns the config value in the given section with the given name.
        If the value does not exist, then we look in the DEFAULTS global, and
        if we can't find it there, we raise a warning, and return None.
        """
        values = self.store
        if section_name not in values:
            if section_name not in DEFAULTS:
                # Then we have a program error
                self._logger.warning(
                    "Config section " + section_name + 
                    " does not exist in config or as default")
                return

            section = DEFAULTS[section_name]
        else:
            section = values[section_name]
            
        if item_name not in section:
            if item_name not in DEFAULTS[section_name]:
                self._logger.warning(
                    "Config value {0}.{1}".format(
                        section_name, item_name) + 
                    " does not exist in config or as a default")
                return
            
            return DEFAULTS[section_name][item_name]
        return section[item_name]
    
    def get_bool(self, section_name, item_name):
        """
        Converts the config value into a boolean. If the value is a string, then
        a number of values will be checked. The mappings are:
        
        +-------+------+
        | str   | bool |
        +=======+======+
        |'yes'  |      |
        +-------+      |
        |'true' | True |
        +-------+      |
        |'y'    |      |
        +-------+------+
        |'no'   |      |
        +-------+      |
        |'false'| False|
        +-------+      |
        |'n'    |      |
        +-------+------+
        
        These values are not case sensitive. If the value is not a string or a
        boolean, then `None` will be returned.
        """
        value = self.get(section_name, item_name)
        if isinstance(value, (str, unicode)):
            bool_mapping = {
                'yes': True,
                'true': True,
                'y': True,
                'no': False,
                'false': False,
                'n': False,
                }
            if value.lower() in bool_mapping:
                return bool_mapping[value.lower()]
        elif isinstance(value, bool):
            return value
        else:
            return None
    
    def get_default(self, section_name, item_name):
        """
        Returns the default value.
        """
        return DEFAULTS[section_name][item_name]
    
    def get_list(self, section_name, item_name):
        """
        Returns the config value at the given section as a list.
        
        If the value is not a string, then it will be converted into a list by
        calling `list(value)`. If the value is a string, it will be treated as a
        CSV, and split then returned.
        
        If the value converted to a list is empty, or the value could not be
        converted, then `None` will be returned.
        """
        value = self.get(section_name, item_name)
        if isinstance(value, (str, unicode)):
            return value.split(",") or None
        else:
            try:
                return list(value) or None
            except TypeError:
                return None
    
    def get_python(self, name):
        """
        Tries to return the object at the given name. If the object cannot be
        found, then `None` is returned.
        
        The name of an object is it's module name and then the identifier that
        you would have to type to access the object. For example, in the module
        `dectest.suite`, there is the class `TestSuite`. The name for that item
        would be `dectest.suite.TestSuite`.
        
        If the `name` argument is not a `str` or `unicode`, then it will just be
        returned.
        """
        if not isinstance(name, (str, unicode)):
            return name
        
        path = name.split(".")
        if len(path) < 2:
            self._logger.warning("Invalid python path: " + name)
            return
        
        module_path = path[:-1]
        attribute_path = [path[-1]]
        module = self._import_module('.'.join(module_path))
        while not module:
            if not path:
                raise Warning("Could not find module for python path " +
                              name)
                return
            
            attribute_path.insert(0, module_path.pop())
            module = self._import_module('.'.join(module_path))
        
        current = module
        for attribute in attribute_path:
            current = getattr(current, attribute)
            if not current:
                self._logger.warning("Could not find attribute for python" +
                                     " path " + name)
                return
        
        return current
    
    def set_logger(self, logger):
        """
        Sets the logger that the config class can use to report any errors or
        warnings in ``get_foo`` methods.
        """
        self._logger = logger
    
    def _import_module(self, name):
        """
        Imports an arbitrarily named module, and returns the module object if
        the import succeeds, otherwise returns `None`.
        """
        try:
            module = __import__(name, fromlist=name.split(".")[:-1])
        except ImportError:
            return
        else:
            return module
    
    def __getattr__(self, section_name):
        """
        Allow us to do `config.section.item` instead of
        `config.get("section", "item")`
        """
        if re.match("__(\w*)__", section_name):
            raise AttributeError()
        
        class Section():
            """
            Just a little class to wrap a ConfigInterface.get call.
            """
            def __getattr__(_, item_name):
                """
                Return the actual value.
                """
                return self.get(section_name, item_name)
            
        return Section()


class DefaultConfig(ConfigInterface):
    """
    A config class that only provides the default values for every setting. Use
    this when no config file is provided.
    """
    
    store = DEFAULTS

class PythonFileConfig(ConfigInterface):
    """
    A config class that loads the dictionary from the global namespace of any 
    given python file.
    The file should define a class for each section, with attributes for each
    value. The class names and attribute names are not case sensitive
    
    For example::
    
        # dectest_config.py
        class section1:
            item1 = 0
            item2 = "one"
            item3 = True
    
        class section2:
            foo = "bar"
    """
    
    def __init__(self, filename):
        """
        Set the filename, and load it.
        """
        self.filename = filename
        # We set this as if the reload method fails, store may be unbound
        self.store = {}
        self.reload()
    
    def reload(self):
        """
        Reloads the configuration file, and populates the store attribute.
        """
        try:
            module = imp.load_source('config', self.filename)
        except Exception as e:
            self.store = DEFAULTS
            self._logger.warning("Could not load configuration file " +
                                 self.filename + ", raised exception " +
                                 str(e))
            return
        
        self.store = {}
        
        for s_name, s_value in module.__dict__.items():
            if s_name.startswith("_") or not type(s_value) == type:
                continue
            
            self.store[s_name] = {}
            for i_name, i_value in s_value.__dict__.items():
                self.store[s_name][i_name] = i_value

class DictConfig(ConfigInterface):
    """
    Provides a simple way of configuring dectest via a dictionary.
    Takes a dictionary as it's only argument.
    """
    
    def __init__(self, dictionary):
        self.store = dictionary
