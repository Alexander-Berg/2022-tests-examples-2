import json
import pytest
from passport.infra.daemons.yasmsapi.tools.keys_generator.src.config import (
    Config,
)

CONFIG_FILE = 'test.conf'


def write_config(contents):
    with open(CONFIG_FILE, 'w') as f:
        f.write(contents)


def test_bad_config():
    with pytest.raises(FileNotFoundError):
        Config('non-existing-file')

    write_config('')
    with pytest.raises(json.decoder.JSONDecodeError):
        Config(CONFIG_FILE)

    write_config('config')
    with pytest.raises(json.decoder.JSONDecodeError):
        Config(CONFIG_FILE)

    write_config('}')
    with pytest.raises(json.decoder.JSONDecodeError):
        Config(CONFIG_FILE)


def test_good_config():
    write_config('{}')
    c = Config(CONFIG_FILE)

    assert c.keys_file == '/etc/yandex/yasms/encryption_keys/keys.json'
    assert c.max_keys == 72
    assert c.create_key_delay == 3600
    assert c.log_file == '/var/log/yandex/yasms/keys_generator.log'

    write_config('{"max_keys":100,"log_file": "/dev/null","funny_other_option":"yay!"}')
    c = Config(CONFIG_FILE)

    assert c.keys_file == '/etc/yandex/yasms/encryption_keys/keys.json'
    assert c.max_keys == 100
    assert c.create_key_delay == 3600
    assert c.log_file == '/dev/null'

    write_config('{"max_keys":1000,"keys_file": "foo","log_file": "bar","create_key_delay": 5}')
    c = Config(CONFIG_FILE)

    assert c.keys_file == 'foo'
    assert c.max_keys == 1000
    assert c.create_key_delay == 5
    assert c.log_file == 'bar'
