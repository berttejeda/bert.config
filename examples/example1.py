from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig1.yaml').read()
value = config.get('section1.key1')
print(value)