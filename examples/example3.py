from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig3.yaml').read()
value = config.get('section2.*.item1')
print(value)