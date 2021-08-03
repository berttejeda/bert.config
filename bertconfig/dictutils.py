from functools import reduce
import sys

class DictUtils:

    def __init__(self):
        pass

    def Merge(self, dict1, dict2):
        if sys.version_info[0] >= 3:
            res = {**dict1, **dict2}
            return res
        else:
            return(dict2.update(dict1))

    def recurse(self, data_input, keys, default=None):
        """Recursively retrieve values from a dictionary object"""
        result = ''
        if isinstance(data_input, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, keys.split('.'), data_input)
        return(result)

class Struct(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [Struct(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, Struct(b) if isinstance(b, dict) else b)        

    def get(self, _key):
        return self.__dict__.get(_key)        
