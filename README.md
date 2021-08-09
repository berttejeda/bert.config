<a name="top"></a>
<a name="overview"></a>

# Overview

This is a module for reading configuration files.

Currently, the module only support YAML-formatted files.

Features:
- Retrieve deeply nested values using dot notation, e.g. `section1.key1`
- Retrieve values using wildcards, e.g. `section1.*.key2`

# Prerequisites:

- Python 2.7+
- pyaml

# Installation

* From pypi: `pip3 install bertdotconfig`
* From this git repo: `pip3 install git+https://github.com/berttejeda/bert.config.git`<br />
  Note: To install a specific version of the library from this git repo, <br />
  suffix the git URL in the above command with @{ tag name }, e.g.: <br />
  git+https://github.com/berttejeda/bert.config.git@1.0.0

# Usage Examples

## Load a configuration file and retrieve specified key value

Given:
- Config file at `/home/myuser/myconfig.yaml`
- with contents:<br />
```yaml
section1:
  key1: value1
  key2: value2
  key3: value3
```

```python
from bertdotconfig import SuperDuperConfig
# Initialize Config Module
superconf = SuperDuperConfig()
# Initialize App Config
config = superconf.load_config('~/myconfig.yaml')
key1 = superconf.get(config, 'section1.key1')
print(key1)
```

## Load a configuration file and retrieve a deeply nested value

Given:
- Config file at `/home/myuser/myconfig.yaml`
- with contents:<br />
```yaml
section1:
  subsection1:
    item1:
      subitem1: value1
    item2: value2
    item3: value3
  subsection2:
    item1: value1
    item2: value2
    item3: value3
  key1: value1
  key2: value2
  key3: value3
section2:
  item1: value1
```

```python
from bertdotconfig import SuperDuperConfig
# Initialize Config Module
superconf = SuperDuperConfig()
# Initialize App Config
config = superconf.load_config('~/myconfig.yaml')
settings = superconf.get(config, 'section1.subsection1.item2')
print(settings)
```

The above should return `value2`

## Load a configuration file and retrieve specified key value using wildcard notation

Given:
- Config file at `/home/myuser/myconfig.yaml`
- with contents:<br />
```yaml
section1:
  subsection1:
    item1:
      subitem1: value1
    item2: value2
    item3: value3
  subsection2:
    item1: value1
    item2: value2
    item3: value3
  key1: value1
  key2: value2
  key3: value3
section2:
  item1: value1
```

```python
from bertdotconfig import SuperDuperConfig
# Initialize Config Module
superconf = SuperDuperConfig()
# Initialize App Config
config = superconf.load_config('~/myconfig.yaml')
settings = superconf.get(config, 'section1.*.item1')
print(settings)
```

The above should return `[{'subitem1': 'value1'}, 'value1']`

Note: When retrieving values via wildcard, the return value is a list object.

## Load a configuration file as a python object

Same as the above examples, just call the 
load_config method with as_object=True, as with `superconf.load_config('~/myconfig.yaml', as_object=True)`

Retrieving values from the object would require dot-notation, as with: `print(settings.section1.subsection1.item2)`

Note: This approach does not support retrieving values via wildcard reference.