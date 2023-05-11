from btconfig import SuperDuperConfig
# Initialize Config Module
superconf = SuperDuperConfig()
# Initialize App Config
config = superconf.load_config('~/myconfig.yaml')
settings = superconf.get(config, 'section1.subsection1.item2')
print(settings)