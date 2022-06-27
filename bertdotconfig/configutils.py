from bertdotconfig.logger import Logger
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
        target = dict.__getitem__(self, myKey)
        if not isinstance(target, AttrDict):
            raise(KeyError, 'cannot get "%s" in "%s" (%s)' % (restOfKey, myKey, repr(target)))
        return target[restOfKey]

    def __contains__(self, key):
        if '.' not in key:
            return dict.__contains__(self, key)
        myKey, restOfKey = key.split('.', 1)
        target = dict.__getitem__(self, myKey)
        if not isinstance(target, AttrDict):
            return False
        return restOfKey in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    def merge(self, incoming_dct, **kwargs):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``incoming_dct`` is merged into
        ``self.dict``.
        :param self.dict: dict onto which the merge is executed
        :param incoming_dct: self.dict merged into self.dict
        :return: merged_dict
        """
        new_dict = kwargs.get('source_dict', self)
        for k, v in incoming_dct.items():
            my_key = new_dict.get(k)
            source_is_dict = isinstance(my_key, dict)
            incoming_is_dict = isinstance(incoming_dct[k], dict)
            if (k in new_dict.keys() and source_is_dict
                    and incoming_is_dict):
                self.merge(my_key, source_dict=incoming_dct[k])
            else:
                new_dict[k] = incoming_dct[k]
        return new_dict

    def update(self, dict_path, default=None):
        """Interpret wildcard paths for setting values in a dictionary object"""
        result = {}
        if isinstance(self.dict, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, dict_path.split('.'), self.dict)
        return(result)

    __setattr__ = __setitem__
    __getattr__ = __getitem__



       
