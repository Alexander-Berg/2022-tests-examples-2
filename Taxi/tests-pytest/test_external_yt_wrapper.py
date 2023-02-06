import pytest

from taxi.conf import settings
from taxi.external import yt_wrapper


class DummyYtClient(object):
    def __init__(self, **kwargs):
        assert 'config' in kwargs
        assert len(kwargs) == 1
        self.config = kwargs['config']


@pytest.mark.filldb(_fill=False)
def test_create_environments(monkeypatch, patch):
    monkeypatch.setattr('yt.wrapper.client.Yt', DummyYtClient)
    monkeypatch.setattr(yt_wrapper, 'YtMapReduceClient', DummyYtClient)
    monkeypatch.setattr(settings, 'YT_MAPREDUCE_USE_CACHE_IN_JOBS', False)

    yt_client = yt_wrapper.create_client_with_config({'prefix': 'test_prefix'})
    assert yt_client.config['prefix'] == 'test_prefix'

    hahn_fraud = yt_wrapper.get_client(
        'hahn-fraud', new=True, environment=False
    )
    assert hahn_fraud.config['prefix'] == '//home/taxi-fraud/'

    environments = yt_wrapper._create_environments(dyntable=False)
    for yt_client in environments.itervalues():
        assert 'prefix' in yt_client.config

    dyntable_environments = yt_wrapper._create_environments(dyntable=True)
    for yt_client in dyntable_environments.itervalues():
        assert 'prefix' in yt_client.config
        assert yt_client.config['proxy']['retries'] == (
            settings.YT_DYNTABLE_CONFIG_OVERRIDES[('proxy', 'retries')]
        )
    monkeypatch.setattr(
        settings, 'YT_MAPREDUCE_CONFIG_OVERRIDES',
        {'spec_defaults': {'owners': ['test_owners']}},
    )

    monkeypatch.setattr(
        settings, 'YT_MAPREDUCE_CONFIG_OVERRIDES',
        {'spec_defaults': {'owners': ['test_owners']}},
    )

    hahn_billing = yt_wrapper.get_client(
        'hahn', new=True, extra_config_overrides={'pool': 'taxi_billing'},
    )
    assert hahn_billing.config['pool'] == 'taxi_billing'
    assert hahn_billing.config['spec_defaults'] == {'owners': ['test_owners']}


@pytest.mark.parametrize('config_overrides,expected_config', [
    (
        {'test_option': {'new_option': 'new_value'}},
        {
            'hahn': {
                'prefix': 'some',
                'test_option': {
                    'new_option': 'new_value',
                    'test_option_2': 0,
                    'test_option_3': {
                        'test_option_4': 0,
                    }
                },
            },
        },
    ),
    (
        {('test_option', 'test_option_2'): 1},
        {
            'hahn': {
                'prefix': 'some',
                'test_option': {
                    'test_option_2': 1,
                    'test_option_3': {
                        'test_option_4': 0,
                    },
                },
            },
        },
    ),
    (
        {('test_option', 'test_option_3'): {'new_option': 'new_value'}},
        {
            'hahn': {
                'prefix': 'some',
                'test_option': {
                    'test_option_2': 0,
                    'test_option_3': {
                        'test_option_4': 0,
                        'new_option': 'new_value',
                    },
                },
            },
        },
    )
]
)
@pytest.mark.filldb(_fill=False)
def test_get_patched_config(config_overrides, expected_config,
                            monkeypatch):
    monkeypatch.setattr(settings, 'YT_CONFIG', {
        'hahn': {
            'prefix': 'some',
            'test_option': {
                'test_option_2': 0,
                'test_option_3': {
                    'test_option_4': 0,
                }
            }
        },
    })
    config = yt_wrapper._get_patched_config(config_overrides=config_overrides,
                                            environment=False)
    assert config == expected_config
