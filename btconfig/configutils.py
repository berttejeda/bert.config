from btconfig.logger import Logger

# Setup Logging
logger = Logger().init_logger(__name__)

WILDCARD = '*'

def _is_dotted(key):
    return isinstance(key, str) and '.' in key

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
            raise TypeError('expected dict')

    def __setitem__(self, key, value):
        if _is_dotted(key):
            myKey, restOfKey = key.split('.', 1)
            target = self.setdefault(myKey, AttrDict())
            if not isinstance(target, AttrDict):
                raise KeyError('cannot set "%s" in "%s" (%s)' % (restOfKey, myKey, repr(target)))
            target[restOfKey] = value
        else:
            if isinstance(value, dict) and not isinstance(value, AttrDict):
                value = AttrDict(value)
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if not _is_dotted(key):
            return dict.__getitem__(self, key)
        myKey, restOfKey = key.split('.', 1)
        try:
            target = dict.__getitem__(self, myKey)
        except KeyError:
            return None
        if not isinstance(target, dict):
            return None
        return target[restOfKey]

    def __contains__(self, key):
        if not _is_dotted(key):
            return dict.__contains__(self, key)
        myKey, restOfKey = key.split('.', 1)
        try:
            target = dict.__getitem__(self, myKey)
        except KeyError:
            return False
        if not isinstance(target, dict):
            return False
        return restOfKey in target

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            if key == 'properties':
                # Allows for config.properties.section.key
                return self
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def get(self, k, default=None):
        if not _is_dotted(k):
            return super(AttrDict, self).get(k, default)
        if WILDCARD in k.split('.'):
            matches = self._get_wildcard(self, k.split('.'))
            return matches if matches else default
        myKey, restOfKey = k.split('.', 1)
        target = super(AttrDict, self).get(myKey, default)
        if not isinstance(target, AttrDict):
            return default
        return target.get(restOfKey, default)

    @staticmethod
    def _get_wildcard(obj, keys):
        """Collect every value matching a key path containing wildcards"""
        if not keys:
            return [obj]
        if not isinstance(obj, dict):
            return []
        key, rest = keys[0], keys[1:]
        if key == WILDCARD:
            children = [dict.__getitem__(obj, c) for c in obj]
        elif dict.__contains__(obj, key):
            children = [dict.__getitem__(obj, key)]
        else:
            children = []
        matches = []
        for child in children:
            matches += AttrDict._get_wildcard(child, rest)
        return matches

    def update(self, *args, **kwargs):
        """Same as dict.update, but nested dictionaries are converted"""
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    @staticmethod
    def merge(a, b, path=None):
        """merges b into a, values already present in a take precedence"""

        if not all([a,b]):
            return AttrDict(a)
        if path is None: path = []
        for key in b:
            if dict.__contains__(a, key):
                a_value, b_value = dict.__getitem__(a, key), dict.__getitem__(b, key)
                if isinstance(a_value, dict) and isinstance(b_value, dict):
                    dict.__setitem__(a, key, AttrDict.merge(a_value, b_value, path + [str(key)]))
            else:
                dict.__setitem__(a, key, dict.__getitem__(b, key))
        return AttrDict(a)
