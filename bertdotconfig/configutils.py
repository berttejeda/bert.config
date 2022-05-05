from bertdotconfig.logger import Logger
from functools import reduce
import collections
from bertdotconfig.struct import Struct

# Setup Logging
logger = Logger().init_logger(__name__)

class ConfigUtils:

    def __init__(self, **kwargs):

        self.as_object = kwargs.get('as_object')
        if self.as_object:
            self.obj = Struct(kwargs.get('dict_input', {}))
        else:
            self.obj = kwargs.get('dict_input', {})
        self.logger = logger

    def merge(self, merge_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``self.obj``.
        :param self.obj: dict onto which the merge is executed
        :param merge_dct: self.obj merged into self.obj
        :return: None
        """
        for k, v in merge_dct.items():
            if (k in self.obj and isinstance(self.obj[k], dict)
                    and isinstance(merge_dct[k], collections.Mapping)):
                self.Merge(self.obj[k], merge_dct[k])
            else:
                self.obj[k] = merge_dct[k]
        return self.obj

    def update(self, dict_path, default=None):
        """Interpret wildcard paths for setting values in a dictionary object"""
        result = {}
        if isinstance(self.obj, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, dict_path.split('.'), self.obj)
        return(result)

    def get(self, dict_path, default=None):
        """Interpret wildcard paths for retrieving values from a dictionary object"""

        if isinstance(self.obj, dict):
            if '.*.' in dict_path:
                try:
                    ks = dict_path.split('.*.')
                    if len(ks) > 1:
                        data = []
                        path_string = ks[0]
                        ds = self.recurse(self.obj, path_string)
                        for d in ds:
                            sub_path_string = '{s}.{dd}.{dv}'.format(s=path_string, dd=d, dv=ks[1])
                            self.logger.debug('Path string is: %s' % sub_path_string)
                            result = self.recurse(self.obj, sub_path_string, default)
                            if result:
                                data.append(result)
                        if self.as_object:
                            return Struct(data)
                        else:
                            return data
                    else:
                        data = self.recurse(self.obj, dict_path, default)
                        if not isinstance(data, dict):
                            return {}
                except Exception as e:
                    raise(e)
            else:
                data = self.recurse(self.obj, dict_path, default)
                if self.as_object:
                    return Struct(data)
                else:
                    return(data)
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

       
