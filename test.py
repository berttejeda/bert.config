from bertconfig import SuperDuperConfig
# Initialize Config Module
superconf = SuperDuperConfig(config_name='myconfig')
# Initialize App Config
config = superconf.load_config('~/myconfig.yaml')
settings = superconf.get(config, 'section1.subsection1.item2')
print(settings)