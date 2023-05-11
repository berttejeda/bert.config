# Usage Examples

## Load a configuration file and retrieve specified key value

Given: 
- Config file at `myconfig1.yaml`
- with contents:<br />
```yaml
section1:
  key1: value1
  key2: value2
  key3: value3
```
- run `python example1.py`, where `example1.py` is<br />
```python
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig1.yaml').read()
value = config.get('section1.key1')
print(value)
```

The above should return `value1`

## Load a configuration file and retrieve a deeply nested value

Given:
- Config file at `/home/myuser/myconfig2.yaml`
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
- run `python example2.py`, where `example2.py` is<br />
```python
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig2.yaml').read()
value = config.get('section1.subsection1.item2')
print(value)
```

The above should return `value2`

## Load a configuration file and retrieve specified key value using wildcard notation

Given:
- Config file at `/home/myuser/myconfig3.yaml`
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
```
- run `python example3.py`, where `example3.py` is<br />
```python
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig3.yaml').read()
value = config.get('section2.*.item1')
print(value)
```

The above should return `[{'subitem1': 'value1'}, 'value1']`

**Note**: When retrieving values via wildcard, the return value is a list object.

## Retrieve values via propterties attribute

Given:
- Config file at `/home/myuser/myconfig4.yaml`
- with contents:<br />
```yaml
section1:
  item1: value1
  subsection1:
    item1:
      subitem1: value1
    item2: value2
    item3: value3
    subsubsection1:
      item1:
        subitem1: value1
      item2: value2
      item3: value3
```
- run `python example4.py`, where `example4.py` is<br />
```python
from btconfig import Config
# Initialize App Config
config = Config(config_file_uri='myconfig4.yaml').read()
value = config.properties.section1.subsection1.subsubsection1.item2
print(value)
```

The above should return `value2`

This is made possible because any object instantiated via the `Config()` 
class has a `properties` attribute, which is a _Struct_ 
object whose values can be retrieved via dot-notation

**Note**: This functionality does not support retrieving values via wildcard reference.
