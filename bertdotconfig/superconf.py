from bertdotconfig.logger import Logger
from bertdotconfig.configutils import ConfigUtils
import os
import sys
from jinja2 import Template
import yaml

# Setup Logging
logger = Logger().init_logger(__name__)

class SuperDuperConfig:

  def render(self, **kwargs):

    config_content = kwargs.get('config_content')
    config_file_uri = kwargs.get('uri')
    config_dict = {}
    config_is_valid = False
    invalid_keys = []

    try:
      if not config_content:
        ymlfile_content = open(config_file_uri).read()
      else:
        ymlfile_content = config_content
      if self.templatized:
        try:
          ymlfile_template = Template(ymlfile_content)
          ymlfile_data = ymlfile_template.render(
            session=self.initial_data
          )
        except Exception as e:
          logger.warning(
            f"I had trouble rendering the config, \
            error was {e}"
          )
          if self.failfast:
            sys.exit(1)
          else:
            ymlfile_data = ymlfile_content
      else:
        ymlfile_data = ymlfile_content
      cfg = yaml.safe_load(ymlfile_data)
      config_dict = cfg[self.data_key] if self.data_key is not None else cfg
      config_dict['config_file_uri'] = config_file_uri
      invalid_keys = [m[m.keys()[0]].get(k) for k in self.req_keys for m in config_dict if m[m.keys()[0]].get(k)]
      config_is_valid = len(invalid_keys) == 0
      self.logger.debug(f"Found config file - {config_file_uri}")
      if not config_is_valid:
        invalid_keys_string = ','.join(invalid_keys)
        self.logger.warning(
          f"The following required keys were not defined \
          in your input file {config_file_uri}: \
          {invalid_keys_string}"
        )
        self.logger.warning(
          "Review the available documentation or consult --help")
    except Exception as e:
      self.logger.warning(
      f"I encountered a problem reading your \
      input file: {config_file_uri}, error was {e}"
      )
    return config_dict, config_is_valid, invalid_keys

  def read(self, **kwargs):
    """Load specified config file"""
    
    config_found = False
    config_file_uris = []

    if self.config_file_uri.startswith('http'):

      if self.config_file_auth_username and self.config_file_auth_password:
        config_res = self.webadapter.get(
          self.config_file_uri,
          username=self.config_file_auth_username,
          password=self.config_file_auth_password
        )
      else:
        config_res = self.webadapter.get(self.config_file_uri)

      config_dict, config_is_valid, invalid_keys = self.render(
        uri=self.config.config_file_uri,
        config_content=config_res
      )

      return ConfigUtils(dict_input=config_dict)

    else:

      if not os.path.exists(self.config_file_uri):
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
            self.logger.error(
              'extra_config_search_paths must \
              be of type str or list'
            )
            sys.exit(1)

        config_file_uris = [
          os.path.expanduser(os.path.join(p, self.config_file_uri))
          for p in config_search_paths
        ]
      else:
        config_file_uris = [self.config_file_uri]
        config_found = True

    for cf_uri in config_file_uris:
      config_exists = config_found or os.path.exists(cf_uri)
      if config_exists:
        config_found = True
        config_dict, config_is_valid, invalid_keys = self.render(
          uri=cf_uri,
          templatized=self.templatized,
          failfast=self.failfast,
          data_key=self.data_key,
          initial_data=self.initial_data,
          req_keys=self.req_keys
        )
        break

    if not config_found and self.failfast:
      self.logger.error(
        "Could not find any config file in \
        specified search paths. Aborting."
      )
      sys.exit(1)

    if config_found and config_is_valid:
      config_data = config_dict
    else:
      if self.failfast:
        self.logger.error(
          "Aborting due to invalid or not found \
          config(s) [%s]" % ','.join(config_file_uris)
        )
        sys.exit(1)
      else:
        logger.warning('No settings could be derived, using defaults')
        config_data = self.default_value

    external_configs = config_data.get('external_configs', [])

    if len(external_configs) > 0:
      logger.info('Loading external configs')
      for external_config in external_configs:
        if isinstance(external_config, dict):
          config_uri = external_config.get('uri')
          if config_uri:
            config_uri_username = external_config.get('auth',{}).get('username')
            config_uri_password = external_config.get('auth',{}).get('password')
            external_settings = self.read(
              config_file_uri=config_uri,
              auth_username=config_uri_username,
              auth_password=config_uri_password,
              templatized=self.templatized,
              initial_data=self.initial_data
            )
            if external_settings:
              config_data = self.merge(config_data, external_settings)
    return ConfigUtils(dict_input=config_dict)