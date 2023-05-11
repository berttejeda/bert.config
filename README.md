<a name="top"></a>
<a name="overview"></a>

# Overview

This is a module for reading configuration files.

Currently, the module only supports YAML-formatted files.

Features:
- Retrieve deeply nested values using dot notation, e.g. `section1.key1`
- Retrieve values using wildcards, e.g. `section1.*.key2`
- Configuration files can be templated (Jinja)

# Prerequisites:

- Python 3.4+

# Installation

* From pypi: `pip3 install btconfig`
* From this git repo: `pip3 install git+https://github.com/berttejeda/bert.config.git`<br />
  Note: To install a specific version of the library from this git repo, <br />
  suffix the git URL in the above command with @{ tag name }, e.g.: <br />
  git+https://github.com/berttejeda/bert.config.git@3.0.0

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
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='~/myconfig.yaml').read()
value = config.get('section1.key')
print(value)
```

The above should return `value1`

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
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='~/myconfig.yaml').read()
value = config.get('section1.subsection1.item2')
print(value)
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
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='~/myconfig.yaml').read()
value = config.get('section1.*.item1')
print(value)
```

The above should return `[{'subitem1': 'value1'}, 'value1']`

Note: When retrieving values via wildcard, the return value is a list object.

## Load a configuration file as a python object

Same as the above examples, just invoke the Config object
with `as_object=True`, as with 
`config = Config('~/myconfig.yaml', as_object=True).read()`

In this case, retrieving values from the object can be done via dot-notation, 
as with: `print(config.section1.subsection1.item2)`, or via `get` method, as with
`print(settings.section1.subsection1.item2)`

Note: This approach does not support retrieving values via wildcard reference.