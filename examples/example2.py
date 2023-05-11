from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig2.yaml').read()
value = config.get('section1.subsection1.item2')
print(value)