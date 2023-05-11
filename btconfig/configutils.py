from btconfig.logger import Logger
from functools import reduce

# Setup Logging
logger = Logger().init_logger(__name__)

class AttrDict(dict):
    """
    see: https://stackoverflow.com/questions/3797957/python-easily-access-deeply-nested-dict-get-and-set
    """
    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise(TypeError, 'expected dict')

    def __setitem__(self, key, value):
        if '.' in key:
            myKey, restOfKey = key.split('.', 1)
            target = self.setdefault(myKey, AttrDict())
            if not isinstance(target, AttrDict):
                raise(KeyError, 'cannot set "%s" in "%s" (%s)' % (restOfKey, myKey, repr(target)))
            target[restOfKey] = value
        else:
            if isinstance(value, dict) and not isinstance(value, AttrDict):
                value = AttrDict(value)
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if '.' not in key:
            return dict.__getitem__(self, key)
        myKey, restOfKey = key.split('.', 1)
        try:
            target = dict.__getitem__(self, myKey)
        except KeyError:
            return None
        return target[restOfKey]

    def __contains__(self, key):
        if '.' not in key:
            return dict.__contains__(self, key)
        myKey, restOfKey = key.split('.', 1)
        try:
            target = dict.__getitem__(self, myKey)
        except KeyError:
            return False
        return restOfKey in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    def get(self, k, default=None):
        if '.' not in k:
            return super(AttrDict, self).get(k, default)
        myKey, restOfKey = k.split('.', 1)
        target = super(AttrDict, self).get(myKey, default)
        if not isinstance(target, AttrDict):
            return default
        return target.get(restOfKey, default)

    @staticmethod
    def merge(a, b, path=None):
        """merges b into a"""

        if not all([a,b]):
            return AttrDict(a)
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    AttrDict.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    pass
            else:
                a[key] = b[key]
        return AttrDict(a)

    def update(self, dict_path, default=None):
        """Interpret wildcard paths for setting values in a dictionary object"""
        result = {}
        if isinstance(self.dict, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, dict_path.split('.'), self.dict)

        if isinstance(result, dict):
            return AttrDict(result)
        else:
            return result

    __setattr__ = __setitem__
    __getattr__ = __getitem__



       
