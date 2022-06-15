from bertdotconfig.logger import Logger
from functools import reduce
from bertdotconfig.struct import Struct

# Setup Logging
logger = Logger().init_logger(__name__)

class ConfigUtils:

    def __init__(self, **kwargs):

        self.dict = kwargs.get('dict_input', {})
        if isinstance(self.dict, ConfigUtils):
            self.struct = self.dict.struct
        else:
            self.struct = Struct(self.dict)
        self.logger = logger

    def __iter__(self):
        for key, item in self.dict.items():
            yield key, item

    def keys(self):
        if self.dict:
            return self.dict.keys()
        else:
            return []

    def items(self):
        if self.dict:
            return self.dict.items()
        else:
            return []

    def values(self):
        if self.dict:
            return self.dict.values()
        else:
            return []

    def __setitem__(self, key, value):
        if self.dict:
            if self.dict.get(key):
                self.dict[key] = value
            else:
                return None
        else:
            return None

    def __getitem__(self, key):
        if self.dict:
            if self.dict.get(key):
                self.dict.get(key)
            else:
                return None
        else:
            return None

    def merge(self, incoming_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``incoming_dct`` is merged into
        ``self.dict``.
        :param self.dict: dict onto which the merge is executed
        :param incoming_dct: self.dict merged into self.dict
        :return: None
        """
        for k, v in incoming_dct.items():
            source_is_dict = isinstance(self.dict[k], dict)
            incoming_is_dict = isinstance(incoming_dct[k], dict)
            if (k in self.dict and source_is_dict
                    and incoming_is_dict):
                self.merge(self.dict.dict[k], incoming_dct[k])
            else:
                self.dict.dict[k] = incoming_dct[k]
        return self.dict

    def update(self, dict_path, default=None):
        """Interpret wildcard paths for setting values in a dictionary object"""
        result = {}
        if isinstance(self.dict, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, dict_path.split('.'), self.dict)
        return(result)

    def get(self, dict_path, default=None):
        """Interpret wildcard paths for retrieving values from a dictionary object"""

        if isinstance(self.dict, dict):
            if '.*.' in dict_path:
                try:
                    ks = dict_path.split('.*.')
                    if len(ks) > 1:
                        data = []
                        path_string = ks[0]
                        ds = self.recurse(self.dict, path_string)
                        for d in ds:
                            sub_path_string = '{s}.{dd}.{dv}'.format(s=path_string, dd=d, dv=ks[1])
                            self.logger.debug('Path string is: %s' % sub_path_string)
                            result = self.recurse(self.dict, sub_path_string, default)
                            if result:
                                data.append(result)
                        return data
                    else:
                        data = self.recurse(self.dict, dict_path, default)
                        if not isinstance(data, dict):
                            return {}
                except Exception as e:
                    raise(e)
            else:
                data = self.recurse(self.dict, dict_path, default)
                return data
        else:
            self.logger.error('Input must be of type "dict"')
            return {}

    def recurse(self, data_input, keys, default=None):
        """Recursively retrieve values from a dictionary object"""
        result = ''
        if isinstance(data_input, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, keys.split('.'), data_input)
        return(result)

       
