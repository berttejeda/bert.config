from btconfig.configutils import AttrDict
from btconfig.logger import Logger
import os
import sys

# Setup Logging
logger = Logger().init_logger(__name__)

class ConfigLoader:

    def load_from_web(self, config_file_uri, **kwargs):
        """Load specified config file from http URI"""

        config_file_auth_username = kwargs.get('config_file_auth_username', self.config_file_auth_username)
        config_file_auth_password = kwargs.get('config_file_auth_password', self.config_file_auth_password)
        templatized = kwargs.get('templatized')

        config_res = None
        try:
            if config_file_auth_username and config_file_auth_password:
                config_res = self.webadapter.get(
                    config_file_uri,
                    username=config_file_auth_username,
                    password=config_file_auth_password
                )
            else:
                config_res = self.webadapter.get(config_file_uri)
        except Exception as e:
            logger.warning(f'Failed to retrieve {config_file_uri}, error was {e}')

        # The web adapter returns an error message instead of
        # raising when the response status is not OK
        if isinstance(config_res, str) and config_res.startswith('Error: Call to '):
            logger.warning(config_res)
            config_res = None

        config_dict, config_is_valid = {}, False
        if config_res:
            config_dict, config_is_valid, invalid_keys = self.render(
                uri=config_file_uri,
                config_content=config_res,
                templatized=templatized
            )

        if config_dict and config_is_valid:
            return AttrDict(config_dict)

        if self.failfast:
            logger.error(
                f"Aborting due to invalid or unreachable config [{config_file_uri}]"
            )
            sys.exit(1)

        return {}

    def load(self, config_file_uri, **kwargs):
        """Load specified config file from filesystem"""

        templatized = kwargs.get('templatized')
        config_found = False
        config_is_valid = False
        config_dict = {}
        config_file_uri = os.path.expanduser(config_file_uri)

        if not os.path.exists(config_file_uri):
            config_search_paths = [
                os.path.realpath(os.path.expanduser('~')),
                '.',
                os.path.dirname(os.path.abspath(sys.argv[0])),
                os.path.join(os.path.abspath(os.sep), 'etc')
            ]
            if self.extra_config_search_paths:
                if isinstance(self.extra_config_search_paths, (list, tuple)):
                    config_search_paths += list(self.extra_config_search_paths)
                elif isinstance(self.extra_config_search_paths, str):
                    config_search_paths += [self.extra_config_search_paths]
                else:
                    logger.error(
                        'extra_config_search_paths must '
                        'be of type str or list'
                    )
                    sys.exit(1)

            config_file_uris = [
                os.path.join(os.path.expanduser(p), config_file_uri)
                for p in config_search_paths
            ]
        else:
            config_file_uris = [config_file_uri]
            logger.debug(f'Found config at {config_file_uri}')

        for cf_uri in config_file_uris:
            if os.path.isfile(cf_uri):
                config_found = True
                if cf_uri not in self.configs_already_processed:
                    self.configs_already_processed.append(cf_uri)
                config_dict, config_is_valid, invalid_keys = self.render(
                    uri=cf_uri,
                    templatized=templatized,
                    failfast=self.failfast,
                    data_key=self.data_key,
                    initial_data=self.initial_data,
                    req_keys=self.req_keys
                )
                break

        if not config_found and self.failfast:
            logger.error(
                "Could not find any config file in "
                "specified search paths. Aborting."
            )
            sys.exit(1)

        if config_found and config_is_valid:
            config_data = config_dict
        else:
            if self.failfast:
                logger.error(
                    "Aborting due to invalid or not found "
                    "config(s) [%s]" % ','.join(config_file_uris)
                )
                sys.exit(1)
            else:
                if self.warn_if_config_not_found:
                    logger.warning('No settings could be derived, using defaults')
                else:
                    logger.debug('No settings could be derived, using defaults')
                config_data = self.default_value

        return config_data
