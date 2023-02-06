import pytest

from taxi import config
from taxi.core import db
from taxi.config import params
from taxi.config import validator


@pytest.inline_callbacks
def test_updated(monkeypatch, stub):
    test_param = params.Param(
        group='test',
        description='test',
        default='default_test_value',
        validators=[validator.string]
    )
    test_param.set_name('FOO')

    yield test_param.save('bar')
    doc = yield db.config.find_one({'_id': 'FOO'})

    assert doc['v'] == 'bar'
    assert 'updated' in doc

    params.Param.all_names.remove('FOO')


@pytest.inline_callbacks
def test_hosts_override(monkeypatch, stub):
    p = config.HOSTS_OVERRIDE
    # validate does not raise
    yield p.validate(p.default)
    v = [{
        "countries": [
            "en"
        ],
        "hosts": [{
            "ID": "en_id",
            "TAXI_TEST": {
                "host": "en_host",
                "ips": [],
                "url": ""
            }
        }]
    }, {
        "countries": [
            "us",
            "ru"
        ],
        "hosts": [{
            "ID": "us_ru_id",
            "TAXI_TEST": {
                "host": "us_ru_host",
                "ips": [],
                "url": ""
            }
        }]
    }]
    yield p.validate(v)
