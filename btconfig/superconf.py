from btconfig.logger import Logger
from btconfig.configutils import AttrDict
from btconfig.configloader import ConfigLoader
import sys
from jinja2 import Template
import yaml
from pyaml_env import parse_config

# Setup Logging
logger = Logger().init_logger(__name__)

class SuperDuperConfig(ConfigLoader):

  def render(self, **kwargs):

    config_content = kwargs.get('config_content')
    config_file_uri = kwargs.get('uri')
    config_dict = {}
    config_is_valid = False
    invalid_keys = []

    try:
      if not config_content:
        ymlfile_content = parse_config(config_file_uri)
      else:
        ymlfile_content = parse_config(data=config_content)
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
      config_dict = ymlfile_data[self.data_key] if self.data_key is not None else ymlfile_data
      if isinstance(config_dict, dict):
        config_dict['config_file_uri'] = config_file_uri
      else:
        _config_dict = [e for e in config_dict if isinstance(e, dict)]
        if len(_config_dict) >= 0:
          config_dict = config_dict[0]
          config_dict['config_file_uri'] = config_file_uri
        else:
          logger.warning("Got unexpected data structure from config dictionary, not setting 'config_file_uri' key")
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

    pre_existing_config_data = kwargs.get('pre_existing_config_data')
    config_file_uri = kwargs.get('config_file_uri', self.config_file_uri)
    config_file_auth_username = kwargs.get('config_file_auth_username')
    config_file_auth_password = kwargs.get('config_file_auth_password')

    if config_file_uri in self.configs_already_processed:
      logger.debug(f'Already processed {config_file_uri}, skipping ...')
      return

    if config_file_uri.startswith('http'):
      config_data = self.load_from_web(
      config_file_uri,
      config_file_auth_username=config_file_auth_username,
      config_file_auth_password=config_file_auth_password
      )
    else:
      config_data = self.load(config_file_uri)

    if pre_existing_config_data and not config_data:
      return pre_existing_config_data

    external_configs = config_data.get('external_configs', [])

    if len(external_configs) > 0:
      logger.debug(f'External configs are being referenced in {config_file_uri}')
      for external_config in external_configs:
        if isinstance(external_config, dict):
          config_uri = external_config.get('uri')
          logger.debug(f'Loading {config_uri} ...')
          if config_uri:
            config_uri_username = external_config.get('auth',{}).get('username')
            config_uri_password = external_config.get('auth',{}).get('password')
            templatized = external_config.get('templatized')
            external_settings = self.read(
              config_file_uri=config_uri,
              config_file_auth_username=config_uri_username,
              config_file_auth_password=config_uri_password,
              templatized=templatized,
              initial_data=self.initial_data,
              pre_existing_config_data=config_data
            )
            if isinstance(external_settings, dict):
              config_data = AttrDict.merge(config_data, external_settings)
              return config_data
    else:
      config_data = AttrDict(config_data)
      return config_data