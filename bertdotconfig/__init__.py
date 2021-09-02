from bertdotconfig.logger import Logger
from bertdotconfig.dictutils import DictUtils
import os
import re
from bertdotconfig.struct import Struct
import sys
from jinja2 import Template
from bertdotwebadapter import WebAdapter
import yaml

# Setup Logging
logger = Logger().init_logger(__name__)

class SuperDuperConfig(DictUtils):

  def __init__(self, **kwargs):
    self.config_name = kwargs.get('config_name', '')
    self.logger = logger
    self.DictUtils = DictUtils()
    self.extra_config_search_paths = kwargs.get('extra_config_search_paths', '')
    self.verify_tls = kwargs.get('verify_tls', True)
    self.webadapter = WebAdapter(verify_tls=self.verify_tls)

  def render_config(self, **kwargs):

    config_file_uri = kwargs.get('uri')
    templatized = kwargs.get('templatized')
    failfast = kwargs.get('failfast')
    data_key = kwargs.get('data_key')
    req_keys = kwargs.get('req_keys')
    config_content = kwargs.get('config_content')
    initial_data = kwargs.get('initial_data')
    config_dict = None
    config_is_valid = False

    try:
      if not config_content:
        ymlfile_content = open(config_file_uri).read()
      else:
        ymlfile_content = config_content
      if templatized:
        try:
          ymlfile_template = Template(ymlfile_content)
          ymlfile_data = ymlfile_template.render(
            session=initial_data
          )
        except Exception as e:
          logger.warning("I had trouble rendering the config, error was %s" % e)
          if failfast:
            sys.exit(1)
          else:
            ymlfile_data = ymlfile_content
      else:
        ymlfile_data = ymlfile_content    
      cfg = yaml.safe_load(ymlfile_data)
      config_dict = cfg[data_key] if data_key is not None else cfg    
      config_dict['config_file_uri'] = config_file_uri
      config_is_valid = all([m[m.keys()[0]].get(k) for k in req_keys for m in config_dict])
      self.logger.debug(
        "Found input file - {cf}".format(cf=config_file_uri))
      if not config_is_valid:
        self.logger.warning(
          """At least one required key was not defined in your input file: {cf}.""".format(
          cf=config_file_uri)
        )
        self.logger.warning(
          "Review the available documentation or consult --help")
    except Exception as e:
      self.logger.warning(
      "I encountered a problem reading your input file: {cp}, error was {err}".format(
      cp=config_file_uri, err=str(e))
      )
    return config_dict, config_is_valid
         
  def load_config(self, **kwargs):
    """Load specified config file"""

    config_file_name = kwargs.get('config_file_name')
    config_file_uri = kwargs.get('config_file_uri', '')
    req_keys = kwargs.get('req_keys', []) 
    failfast = kwargs.get('failfast',False) 
    data_key = kwargs.get('data_key')
    debug = kwargs.get('debug', False)
    as_object = kwargs.get('as_object', False)
    templatized = kwargs.get('templatized')
    initial_data = kwargs.get('initial_data', {})
    config_file_auth_username = kwargs.get('auth_username')
    config_file_auth_password = kwargs.get('auth_password')

    if config_file_uri.startswith('http'):
      if config_file_auth_username and config_file_auth_password:
        config_res = self.webadapter.get(config_file_uri,
                    username=config_file_auth_username,
                    password=config_file_auth_password)
      else:
        config_res = self.webadapter.get(config_file_uri)
      config_dict, config_is_valid = self.render_config(
      uri = config_file_uri,
      templatized = templatized,
      failfast = failfast,
      data_key = data_key,
      req_keys = req_keys,
      initial_data = initial_data,
      config_content = config_res)
      return config_dict
    elif not config_file_uri:
      config_search_paths = [
        os.path.realpath(os.path.expanduser('~')),
        '.',
        os.path.join(os.path.abspath(os.sep), 'etc')
      ]
      if self.extra_config_search_paths:
        if isinstance(self.extra_config_search_paths, list):
          config_search_paths += self.extra_config_search_paths
        elif isinstance(self.extra_config_search_paths, str):
          config_search_paths += [self.extra_config_search_paths]
        else:
          self.logger.error('extra_config_search_paths must be of type str or list')
          sys.exit(1)
      if config_file_name:
        config_file_uris = [
        os.path.expanduser(os.path.join(p, config_file_name))
          for p in config_search_paths
          ]
    else:
      config_file_uris = [config_file_uri]
    
    config_found = False
    
    for config_file_uri in config_file_uris:
      config_exists = os.path.exists(config_file_uri)
      if config_exists:
        config_found = True
        config_dict, config_is_valid = self.render_config(
        uri = config_file_uri,
        templatized = templatized,
        failfast = failfast,
        data_key = data_key,
        initial_data = initial_data,
        req_keys = req_keys)
        break

    if not config_found:
      if failfast:
        self.logger.error("Could not find %s. Aborting." % config_file_uri)
        sys.exit(1)
      else:
        self.logger.debug(
        "Could not find %s, not loading values" % config_file_uri)

    if config_found and config_is_valid:
      if as_object:
        config_data = Struct(config_dict)
      else:
        config_data = config_dict
    else:
      if failfast:
        self.logger.error(
        "Config %s is invalid. Aborting." % config_file_uri)
        sys.exit(1)
      else:
        if as_object:
          config_data = Struct({})
        else:
          config_data = {}

    return config_data