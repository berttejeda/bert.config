from functools import reduce
import collections
import sys

class DictUtils:

    def __init__(self):
        pass

    def Merge(self, dct, merge_dct):
      """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
      updating only top-level keys, dict_merge recurses down into dicts nested
      to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
      ``dct``.
      :param dct: dict onto which the merge is executed
      :param merge_dct: dct merged into dct
      :return: None
      """
      for k, v in merge_dct.items():
          if (k in dct and isinstance(dct[k], dict)
                  and isinstance(merge_dct[k], collections.Mapping)):
              self.Merge(dct[k], merge_dct[k])
          else:
              dct[k] = merge_dct[k]
      return dct

    def get(self, yaml_input, dict_path, default=None):
      """Interpret wildcard paths for retrieving values from a dictionary object"""
      if '.*.' in dict_path:
        try:
          ks = dict_path.split('.*.')
          if len(ks) > 1:
            data = []
            path_string = ks[0]
            ds = self.recurse(yaml_input, path_string)
            for d in ds:
              sub_path_string = '{s}.{dd}.{dv}'.format(s=path_string, dd=d, dv=ks[1])
              self.logger.debug('Path string is: %s' % sub_path_string)
              result = self.recurse(yaml_input, sub_path_string, default)
              if result:
                data.append(result)
            return data
          else:
            data = self.recurse(yaml_input, dict_path, default)
            if not isinstance(data, dict):
              return {}
        except Exception as e:
          raise(e)
      else:
        return self.recurse(yaml_input, dict_path, default)

    def recurse(self, data_input, keys, default=None):
        """Recursively retrieve values from a dictionary object"""
        result = ''
        if isinstance(data_input, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, keys.split('.'), data_input)
        return(result)

       
