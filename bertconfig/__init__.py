from bertconfig.logger import Logger
from bertconfig.dictutils import DictUtils
from bertconfig.struct import Struct
import os
import re
import sys
from collections import OrderedDict 
import yaml

# Setup Logging
logger = Logger().init_logger(__name__)

class SuperDuperConfig():

  def __init__(self, **kwargs):
    self.config_name = kwargs.get('config_name', '')
    self.config_path = kwargs.get('config_path', '')
    self.logger = logger
    self.DictUtils = DictUtils()

  def ordered_load(self, stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
      pass
    def construct_mapping(loader, node):
      loader.flatten_mapping(node)
      return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
      yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
      construct_mapping)
    return yaml.load(stream, OrderedLoader)            

  def load_config(self, config_file=None, req_keys=[], failfast=False, data_key=None, debug=False, as_object=False):
    """Load specified config file"""
    config_path_strings = [
      os.path.realpath(os.path.expanduser('~')),
      '.',
      os.path.join(os.path.abspath(os.sep), 'etc')
    ]
    config_paths = [self.config_path]
    if config_file:
      config_paths += [os.path.join(p, config_file)
        for p in config_path_strings]
      config_paths.append(os.path.expanduser(config_file))
    config_found = False
    config_is_valid = False
    for config_path in config_paths:
      config_exists = os.path.exists(config_path)
      if config_exists:
        config_found = True
        self.config_path = config_path
        try:
          with open(config_path, 'r') as ymlfile:
            # Preserve dictionary order for python 2
            # https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
            if sys.version_info[0] < 3:
              cfg = self.ordered_load(ymlfile, yaml.Loader)
            else:
              cfg = yaml.load(ymlfile, yaml.Loader)
          config_dict = cfg[data_key] if data_key is not None else cfg
          config_dict['config_path'] = self.config_path
          config_is_valid = all([m[m.keys()[0]].get(k) for k in req_keys for m in config_dict])
          self.logger.debug(
            "Found input file - {cf}".format(cf=config_path))
          if not config_is_valid:
            logger.warning(
              """At least one required key was not defined in your input file: {cf}.""".format(
              cf=config_path)
            )
            self.logger.warning(
              "Review the available documentation or consult --help")
          config_file = config_path
          break
        except Exception as e:
          self.logger.warning(
          "I encountered a problem reading your input file: {cp}, error was {err}".format(
          cp=config_path, err=str(e))
          )
    if not config_found:
      if failfast:
        self.logger.error("Could not find %s. Aborting." % config_file)
        sys.exit(1)
      else:
        self.logger.debug(
        "Could not find %s, not loading values" % config_file)

    if config_found and config_is_valid:
      if as_object:
        return Struct(config_dict)
      else:
        return config_dict
    else:
      if failfast:
        self.logger.error(
        "Config %s is invalid. Aborting." % config_file)
        sys.exit(1)
      else:
        if as_object:
          return Struct({})
        else:
          return {}
              
  def get(self, yaml_input, dict_path):
    """Interpret wildcard paths for retrieving values from a dictionary object"""
    if '.*.' in dict_path:
      try:
        ks = dict_path.split('.*.')
        if len(ks) > 1:
          data = []
          path_string = ks[0]
          ds = self.DictUtils.recurse(yaml_input, path_string)
          for d in ds:
            sub_path_string = '{s}.{dd}.{dv}'.format(s=path_string, dd=d, dv=ks[1])
            self.logger.debug('Path string is: %s' % sub_path_string)
            result = self.DictUtils.recurse(yaml_input, sub_path_string)
            if result:
              data.append(result)
          return data
        else:
          data = self.DictUtils.recurse(yaml_input, dict_path)
          if not isinstance(data, dict):
            return {}
      except Exception as e:
        raise(e)
    else:
      return self.DictUtils.recurse(yaml_input, dict_path)
