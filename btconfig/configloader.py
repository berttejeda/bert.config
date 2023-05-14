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

        if config_file_auth_username and config_file_auth_password:
            config_res = self.webadapter.get(
                config_file_uri,
                username=config_file_auth_username,
                password=config_file_auth_password
            )
        else:
            config_res = self.webadapter.get(config_file_uri)

        if not config_res:
            return {}

        config_dict, config_is_valid, invalid_keys = self.render(
            uri=config_file_uri,
            config_content=config_res
        )

        self.configs_already_processed.append(config_file_uri)

        if config_dict:
            return AttrDict(config_dict)
        else:
            return {}

    def load(self, config_file_uri):
        """Load specified config file from filesystem"""

        config_found = False

        if not os.path.exists(config_file_uri):
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
                    logger.error(
                        'extra_config_search_paths must \
                        be of type str or list'
                    )
                    sys.exit(1)

            config_file_uris = [
                os.path.expanduser(os.path.join(p, config_file_uri))
                for p in config_search_paths
            ]
        else:
            config_file_uris = [config_file_uri]
            config_found = True
            logger.debug(f'Found config at {config_file_uri}')

        for cf_uri in config_file_uris:
            config_exists = config_found or os.path.exists(cf_uri)
            if config_exists:
                config_found = True
                self.configs_already_processed.append(cf_uri)
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
                logger.debug('No settings could be derived, using defaults')
                config_data = self.default_value

        return config_data