from bertdotconfig.logger import Logger
from functools import reduce

# Setup Logging
logger = Logger().init_logger(__name__)

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

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

       
