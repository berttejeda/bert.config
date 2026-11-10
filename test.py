"""Run with: pytest test.py"""
import os
import pytest
from btconfig import Config
from btconfig.configutils import AttrDict

EXAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')


def example(name):
    return os.path.join(EXAMPLES, name)


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_simple_key():
    config = Config(config_file_uri=example('myconfig1.yaml')).read()
    assert config.get('section1.key1') == 'value1'


def test_nested_key():
    config = Config(config_file_uri=example('myconfig2.yaml')).read()
    assert config.get('section1.subsection1.item2') == 'value2'
    assert config.get('section1.nope.item2', 'fallback') == 'fallback'


def test_wildcard():
    config = Config(config_file_uri=example('myconfig3.yaml')).read()
    assert config.get('section2.*.item1') == [{'subitem1': 'value1'}, 'value1']
    assert config.get('section2.*.nope', 'fallback') == 'fallback'


def test_properties_and_attribute_access():
    config = Config(config_file_uri=example('myconfig4.yaml')).read()
    assert config.properties.section1.subsection1.subsubsection1.item2 == 'value2'
    assert config.section1.item1 == 'value1'
    assert not hasattr(config, 'does_not_exist')
    assert getattr(config, 'does_not_exist', 'x') == 'x'


def test_read_twice_returns_same_data():
    c = Config(config_file_uri=example('myconfig1.yaml'))
    assert c.read() == c.read() != None


def test_missing_config_returns_default(tmp_path):
    c = Config(config_file_uri=str(tmp_path / 'nope.yaml'), default_value={'a': 1},
               warn_if_config_not_found=True)
    assert c.read() == {'a': 1}


def test_missing_config_failfast(tmp_path):
    with pytest.raises(SystemExit):
        Config(config_file_uri=str(tmp_path / 'nope.yaml'), failfast=True).read()


def test_no_config_uri():
    with pytest.raises(ValueError):
        Config().read()


def test_empty_and_non_string_keys(tmp_path):
    assert Config(config_file_uri=write(tmp_path, 'e.yaml', '')).read().get('a') is None
    config = Config(config_file_uri=write(tmp_path, 'i.yaml', '1: one\nports:\n  80: http\n')).read()
    assert config[1] == 'one'
    assert config['ports'][80] == 'http'


def test_req_keys(tmp_path):
    f = write(tmp_path, 'r.yaml', 'a:\n  b: 1\n')
    assert Config(config_file_uri=f, req_keys=['a.b']).read().get('a.b') == 1
    assert Config(config_file_uri=f, req_keys=['a.c'], default_value={'d': 1}).read() == {'d': 1}
    with pytest.raises(SystemExit):
        Config(config_file_uri=f, req_keys=['a.c'], failfast=True).read()


def test_data_key_and_list_config(tmp_path):
    f = write(tmp_path, 'd.yaml', 'app:\n  x: 1\nother: 2\n')
    assert Config(config_file_uri=f, data_key='app').read().get('x') == 1
    f = write(tmp_path, 'l.yaml', '- just a string\n- x: 1\n')
    assert Config(config_file_uri=f).read().get('x') == 1


def test_templating(tmp_path, monkeypatch):
    monkeypatch.setenv('BTCONFIG_TEST_VAR', 'fromenv')
    f = write(tmp_path, 't.yaml', 'a: $BTCONFIG_TEST_VAR\nb: "{{ name }}"\nc: "{{ 1 + 1 }}"\n')
    raw = Config(config_file_uri=f).read()
    assert raw.get('a') == '$BTCONFIG_TEST_VAR'
    for kw in ({'templatized': True}, {'is_template': True}, {'args': {'is_template': True}}):
        config = Config(config_file_uri=f, initial_data={'name': 'bert'}, **kw).read()
        assert (config.get('a'), config.get('b'), config.get('c')) == ('fromenv', 'bert', '2')


def test_external_configs(tmp_path):
    write(tmp_path, 'ext1.yaml', 'shared:\n  a: ext1\n  b: ext1\none: 1\n')
    write(tmp_path, 'ext2.yaml', 'two: "{{ 1 + 1 }}"\nexternal_configs:\n  - uri: %s\n' % (tmp_path / 'main.yaml'))
    main = write(tmp_path, 'main.yaml', (
        'shared:\n  a: main\n'
        'external_configs:\n'
        '  - uri: {d}/ext1.yaml\n'
        '  - uri: {d}/missing.yaml\n'
        '  - uri: {d}/ext2.yaml\n'
        '    templatized: true\n'
    ).format(d=tmp_path))
    config = Config(config_file_uri=main).read()
    # main wins, externals fill in the gaps, all externals are processed,
    # and circular references do not recurse forever
    assert config.get('shared.a') == 'main'
    assert config.get('shared.b') == 'ext1'
    assert config.get('one') == 1
    assert config.get('two') == '2'
    assert config.config_file_uri == main


def test_external_configs_null(tmp_path):
    f = write(tmp_path, 'n.yaml', 'a: 1\nexternal_configs:\n')
    assert Config(config_file_uri=f).read().get('a') == 1


def test_search_paths(tmp_path):
    write(tmp_path, 'btconfig-test-searched.yaml', 'a: 1\n')
    c = Config(config_file_uri='btconfig-test-searched.yaml', extra_config_search_paths=str(tmp_path))
    assert c.read().get('a') == 1


class FakeWeb:
    def __init__(self, responses):
        self.responses = responses

    def get(self, url, **kwargs):
        r = self.responses[url]
        if isinstance(r, Exception):
            raise r
        return r


def test_web_configs():
    c = Config(config_file_uri='https://example.test/main.yaml')
    c.webadapter = FakeWeb({
        'https://example.test/main.yaml':
            'a: 1\nexternal_configs:\n  - uri: https://example.test/404.yaml\n  - uri: https://example.test/ext.yaml\n',
        'https://example.test/404.yaml':
            'Error: Call to https://example.test/404.yaml failed with error code 404',
        'https://example.test/ext.yaml': 'b: 2\n',
    })
    config = c.read()
    assert (config.get('a'), config.get('b')) == (1, 2)
    assert 'Error' not in config
    c.webadapter = FakeWeb({'https://example.test/main.yaml': None})
    assert c.read() == {}


def test_attrdict():
    with pytest.raises(TypeError):
        AttrDict('nope')
    d = AttrDict({'a': {'b': 1}})
    d.update({'c': {'d': 2}}, e=3)
    assert d.c.d == 2 and d.e == 3
    d['x.y.z'] = 1
    assert d.get('x.y.z') == 1 and 'x.y.z' in d and 'a.b.c' not in d
    assert d['a.b.c'] is None
    with pytest.raises(KeyError):
        d['e.f'] = 1
    merged = AttrDict.merge(AttrDict({'a': {'b': 1}}), {'a': {'b': 2, 'c': 3}, 'z': 1})
    assert merged == {'a': {'b': 1, 'c': 3}, 'z': 1}


def test_verify_tls_default():
    assert Config().webadapter.verify_tls is True
    assert Config(verify_tls=False).webadapter.verify_tls is False
