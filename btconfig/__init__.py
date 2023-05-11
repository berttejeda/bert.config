from btconfig.logger import Logger
import os
from btconfig.superconf import SuperDuperConfig
from btweb import WebAdapter

# Setup Logging
logger = Logger(is_main_logger=True).init_logger(__name__)

class Config(SuperDuperConfig):

  def __init__(self, **kwargs):

    self.logger = logger
    self.initial_data = kwargs.get('initial_data', {'environment': os.environ})
    self.verify_tls = kwargs.get('verify_tls', False)
    self.webadapter = WebAdapter(verify_tls=self.verify_tls)
    self.args = kwargs.get('args', {})
    self.config_is_templatized = self.args.get('is_template', False) or kwargs.get('is_template', False)
    self.extra_config_search_paths = kwargs.get('extra_config_search_paths', '')
    config_file_uri = kwargs.get('config_file_uri')
    if config_file_uri:
      self.config_file_uri = os.path.expanduser(config_file_uri)
    self.req_keys = kwargs.get('req_keys', [])
    self.failfast = kwargs.get('failfast',False)
    self.data_key = kwargs.get('data_key')
    self.templatized = kwargs.get('templatized')
    self.config_file_auth_username = kwargs.get('auth_username')
    self.config_file_auth_password = kwargs.get('auth_password')
    self.configs_already_processed = []
    self.default_value = kwargs.get('default_value', {})

