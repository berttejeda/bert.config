from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig4.yaml').read()
value = config.properties.section1.subsection1.subsubsection1.item2
print(value)