import os
import sys
import yaml

from btconfig.logger import Logger
from btconfig.configutils import AttrDict
from btconfig.configloader import ConfigLoader
from jinja2 import Template as JinjaTemplate
from collections import defaultdict
from string import Template

# Setup Logging
logger = Logger().init_logger(__name__)

class SuperDuperConfig(ConfigLoader):

  def render(self, **kwargs):

    config_content = kwargs.get('config_content')
    config_file_uri = kwargs.get('uri')
    templatized = kwargs.get('templatized')
    if templatized is None:
      templatized = self.templatized
    failfast = kwargs.get('failfast', self.failfast)
    data_key = kwargs.get('data_key', self.data_key)
    initial_data = kwargs.get('initial_data') or self.initial_data or {}
    req_keys = kwargs.get('req_keys') or self.req_keys or []
    config_dict = {}
    config_is_valid = False
    invalid_keys = []

    try:
      if not config_content:
        with open(config_file_uri) as ymlfile:
          ymlfile_content = ymlfile.read()
      else:
        ymlfile_content = config_content
      if templatized:
        initial_template_data = defaultdict(str, {**initial_data, **os.environ})
        ymlfile_content = Template(ymlfile_content).substitute(initial_template_data)
        try:
          ymlfile_template = JinjaTemplate(ymlfile_content)
          ymlfile_data = ymlfile_template.render(
            initial_data
          )
        except Exception as e:
          logger.warning(
            f"I had trouble rendering the config, error was {e}"
          )
          if failfast:
            sys.exit(1)
          else:
            ymlfile_data = ymlfile_content
      else:
        ymlfile_data = ymlfile_content
      cfg = yaml.safe_load(ymlfile_data)
      config_dict = cfg[data_key] if data_key is not None else cfg
      if config_dict is None:
        # Empty file/section
        config_dict = {}
      if not isinstance(config_dict, dict):
        # e.g. a list of mappings: use the first mapping found
        _config_dicts = []
        if isinstance(config_dict, (list, tuple)):
          _config_dicts = [e for e in config_dict if isinstance(e, dict)]
        if not _config_dicts:
          raise ValueError(
            'expected a mapping, got %s' % type(config_dict).__name__
          )
        config_dict = _config_dicts[0]
      config_dict['config_file_uri'] = config_file_uri
      # Required keys (dot-notation supported) that are missing from the config
      config_lookup = AttrDict(config_dict)
      invalid_keys = [k for k in req_keys if k not in config_lookup]
      config_is_valid = len(invalid_keys) == 0
      logger.debug(f"Found config file - {config_file_uri}")
      if not config_is_valid:
        invalid_keys_string = ','.join(invalid_keys)
        logger.warning(
          "The following required keys were not defined "
          f"in your input file {config_file_uri}: {invalid_keys_string}"
        )
        logger.warning(
          "Review the available documentation or consult --help")
    except Exception as e:
      config_dict = {}
      config_is_valid = False
      logger.warning(
        "I encountered a problem reading your "
        f"input file: {config_file_uri}, error was {e}"
      )
    return config_dict, config_is_valid, invalid_keys

  def read(self, **kwargs):
    """Load specified config file"""

    is_external_config = 'pre_existing_config_data' in kwargs
    pre_existing_config_data = kwargs.get('pre_existing_config_data')
    config_file_uri = kwargs.get('config_file_uri') or getattr(self, 'config_file_uri', None)
    config_file_auth_username = kwargs.get('config_file_auth_username')
    config_file_auth_password = kwargs.get('config_file_auth_password')
    templatized = kwargs.get('templatized')

    if not config_file_uri:
      raise ValueError('No config file specified, please provide config_file_uri')

    if not is_external_config:
      # Top-level call: start with a clean slate so repeated reads work
      self.configs_already_processed = []

    if config_file_uri in self.configs_already_processed:
      logger.debug(f'Already processed {config_file_uri}, skipping ...')
      return

    # Guards against configs that reference each other
    self.configs_already_processed.append(config_file_uri)

    if config_file_uri.lower().startswith(('http://', 'https://')):
      load_kwargs = {'templatized': templatized}
      # Only override the instance-level credentials if some were given
      if config_file_auth_username and config_file_auth_password:
        load_kwargs['config_file_auth_username'] = config_file_auth_username
        load_kwargs['config_file_auth_password'] = config_file_auth_password
      config_data = self.load_from_web(config_file_uri, **load_kwargs)
    else:
      config_data = self.load(config_file_uri, templatized=templatized)

    if is_external_config and not config_data:
      return pre_existing_config_data

    if not isinstance(config_data, dict):
      # e.g. a non-dict default_value
      return config_data

    config_data = AttrDict(config_data)

    external_configs = config_data.get('external_configs') or []
    if isinstance(external_configs, (str, dict)):
      external_configs = [external_configs]

    if len(external_configs) > 0:
      logger.debug(f'External configs are being referenced in {config_file_uri}')
      for external_config in external_configs:
        if isinstance(external_config, str):
          external_config = {'uri': external_config}
        if isinstance(external_config, dict):
          config_uri = external_config.get('uri')
          if config_uri:
            logger.debug(f'Loading {config_uri} ...')
            auth = external_config.get('auth') or {}
            external_settings = self.read(
              config_file_uri=os.path.expanduser(config_uri),
              config_file_auth_username=auth.get('username'),
              config_file_auth_password=auth.get('password'),
              templatized=external_config.get('templatized'),
              pre_existing_config_data=config_data
            )
            if isinstance(external_settings, dict) and external_settings is not config_data:
              config_data = AttrDict.merge(config_data, external_settings)

    return config_data
