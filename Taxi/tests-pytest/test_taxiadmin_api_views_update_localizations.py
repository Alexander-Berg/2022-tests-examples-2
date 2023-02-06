# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

import pytest
from django import test as django_test

from taxiadmin.api.views import update_localizations
from taxi.core import async
from taxi.core import db
from taxi.core import translations
from taxi.internal import localization_update

YANDEX_KEY = {
    'translations': {
        'ru': {
            'form': 'Yandex',
            'status': 'translated'
        },
        'en': {
            'form': 'Yandex',
            'status': 'require_translation'
        }
    },
    'info': {
        'is_plural': False
    }
}
MOSCOW_KEY = {
    'translations': {
        'ru': {
            'form': 'Москва',
            'status': 'translated'
        },
        'en': {
            'form': 'Moscow',
            'status': 'require_translation'
        }
    },
    'info': {
        'is_plural': False
    }
}


DEFAULT_KEYSETS = {
    'backend.geoareas': {
        'Yandex': YANDEX_KEY,
        'moscow': MOSCOW_KEY,
    }
}


@pytest.fixture(autouse=True)
def sample_tanker(monkeypatch):

    class Tanker(object):
        def __init__(self, keysets=None):
            if keysets is not None:
                self.keysets = keysets
            else:
                self.keysets = DEFAULT_KEYSETS

        def keys(self, keyset_id):
            return self.keysets[keyset_id]

        def set_keysets(self, keysets):
            self.keysets = keysets

    tanker = Tanker()

    def tanker_request(location, parameters):
        resp_data = {}
        if location == 'v2/keys/single':
            keys = tanker.keys(parameters['keyset'])
            key = parameters['key']
            data = {'translations': keys[key]['translations']}
            data.update(keys[key]['info'])
            resp_data.update(
                {'key': data}
            )
        elif location == 'keysets/tjson':
            keyset_id = parameters['keyset-id']
            keys = tanker.keys(keyset_id)
            keyset = {}
            for key, key_data in keys.iteritems():
                data = {
                    'translations': key_data['translations'],
                    'info': key_data['info'],
                }
                keyset[key] = data
            resp_data.update({
                'keysets': {keyset_id: {'keys': keyset}}
            })
        else:
            raise Exception('Invalid Location {0}'.format(location))
        return resp_data

    monkeypatch.setattr(
        'taxi.external.tanker._request',
        tanker_request
    )

    return tanker


@pytest.fixture
def replication_api_mocks(patch):
    @patch('taxi.external.localizations_replica.get_keysets')
    @async.inline_callbacks
    def get_keysets(verbose, log_extra):
        yield
        if not verbose:
            async.return_value({'keysets': [{'id': 'geoareas'}]})
        async.return_value({
            'keysets': [{
                'id': 'geoareas',
                'tanker_name': 'backend.geoareas',
                'project': 'taxi',
            }]
        })

    @patch('taxi.external.localizations_replica.get_keysets_diff')
    @async.inline_callbacks
    def get_keysets_diff(log_extra):
        yield
        async.return_value({
            'keysets': [{'id': 'geoareas'}]
        })

    return {
        'get_keysets': get_keysets,
        'get_keysets_diff': get_keysets_diff,
    }


@pytest.fixture
def update_keyset_mock(areq_request):
    def do_it(status, body):
        @areq_request
        def handler(method, url, *args, **kwargs):
            assert url == ('http://localizations-replica.taxi.dev.yandex.net'
                           '/v1/keysets/update')
            assert method == 'POST'
            return areq_request.response(status, body=json.dumps(body))

    return do_it


@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
)
@async.inline_callbacks
def test_get_translations_from_tanker():
    ya = yield update_localizations.get_translations_for_key_from_tanker(
        'Yandex', 'geoareas'
    )
    geoareas = yield (
        localization_update.get_translations_for_keyset_from_tanker(
            'geoareas'
        )
    )
    assert geoareas['Yandex'] == ya
    assert ya == {'ru': 'Yandex', 'en': 'Yandex'}


@async.inline_callbacks
def _get_last_updated_meta_doc():
    async.return_value((
        yield db.localizations_meta.find_one(
            {'_id': translations.LAST_UPDATED_META_ID},
        )
    ))


@pytest.mark.now('2019-01-15T00:00:00')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
)
@async.inline_callbacks
def test_save_keyset_to_db():
    data = yield (
        localization_update.get_translations_for_keyset_from_tanker(
            'geoareas'
        )
    )
    block = translations.translations.geoareas

    yield update_localizations.save_keyset_translations_to_db(
        'geoareas', data
    )
    yield block.do_check_and_refresh(None)
    assert block.get_string('Yandex', 'ru') == 'Yandex'

    last_updated_meta_doc = yield _get_last_updated_meta_doc()
    assert (
        last_updated_meta_doc['value']['geoareas'] ==
        datetime.datetime.utcnow()
    )


@pytest.mark.now('2019-01-16T00:00:00')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
)
@async.inline_callbacks
def test_save_key_to_db():
    data = yield (
        update_localizations.get_translations_for_key_from_tanker(
            'Yandex', 'geoareas'
        )
    )
    block = translations.translations.geoareas

    yield update_localizations.save_key_translations_to_db(
        'Yandex', 'geoareas', data
    )
    yield block.do_check_and_refresh(None)
    assert block.get_string('Yandex', 'ru') == 'Yandex'

    last_updated_meta_doc = yield _get_last_updated_meta_doc()
    assert (
        last_updated_meta_doc['value']['geoareas'] ==
        datetime.datetime.utcnow()
    )


def _test_update_localizations_keysets(verbose):
    response = django_test.Client().get(
        '/api/update_localizations/keysets/?verbose={}'.format(
            int(verbose)),
        '',
        content_type='application/json'
    )
    assert response.status_code == 200
    res = json.loads(response.content)
    if not verbose:
        assert 'geoareas' in res
        assert all([isinstance(x, (str, unicode)) for x in res])
    else:
        assert all([isinstance(x, dict) for x in res])
        assert 'geoareas' in [x['config_name'] for x in res]


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    LOCALIZATIONS_REPLICA_PY2_USAGE_SETTINGS={
        'get_keyset_info': False,
    },
)
@pytest.mark.parametrize(
    'verbose', (True, False),
)
def test_update_localizations_keysets_no_api(replication_api_mocks, verbose):
    _test_update_localizations_keysets(verbose)
    assert not replication_api_mocks['get_keysets'].calls


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    LOCALIZATIONS_REPLICA_PY2_USAGE_SETTINGS={
        'get_keyset_info': True,
        'request_settings': {
            'timeout': 0,
            'retries': 0,
            'retry_delay': 0,
        },
    },
)
@pytest.mark.parametrize(
    'verbose', (True, False),
)
def test_update_localizations_keysets_with_api(replication_api_mocks, verbose):
    _test_update_localizations_keysets(verbose)
    assert len(replication_api_mocks['get_keysets'].calls) == 1


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'},
    LOCALIZATIONS_REPLICA_PY2_USAGE_SETTINGS={
        'get_keyset_diff': False,
    },
)
def test_keysets_diff_no_api(replication_api_mocks):
    response = django_test.Client().get(
        '/api/update_localizations/keysets_diff/'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {'keysets': [{'id': 'geoareas'}]}
    assert not replication_api_mocks['get_keysets_diff'].calls


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'},
    LOCALIZATIONS_REPLICA_PY2_USAGE_SETTINGS={
        'get_keyset_diff': True,
        'request_settings': {
            'timeout': 0,
            'retries': 0,
            'retry_delay': 0,
        },
    },
)
def test_keysets_diff_with_api(replication_api_mocks):
    response = django_test.Client().get(
        '/api/update_localizations/keysets_diff/'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {'keysets': [{'id': 'geoareas'}]}
    assert len(replication_api_mocks['get_keysets_diff'].calls) == 1


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'}
)
def test_update_localizations_unknown_keyset(sample_tanker):
    response = django_test.Client().post(
        '/api/update_localizations/',
        json.dumps({'keyset': ['fooareas']}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        'status': 'error',
        'message': 'Unknown keyset: \'fooareas\'',
        'code': 'general',
    }


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'},
    LOCALIZATIONS_REPLICA_PY2_USAGE_SETTINGS={
        'update_keysets': True,
        'request_settings': {
            'timeout': 0,
            'retries': 0,
            'retry_delay': 0,
        },
    },
)
def test_update_localizations_unknown_keyset_with_api(
        sample_tanker,
        update_keyset_mock,
):
    update_keyset_mock(
        400,
        {
            'status': 'error',
            'message': 'Unknown keyset: fooareas',
            'code': 'general',
        },
    )
    response = django_test.Client().post(
        '/api/update_localizations/',
        json.dumps({'keyset': ['fooareas']}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        'status': 'error',
        'message': 'Unknown keyset: fooareas',
        'code': 'general',
    }


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'},
    LOCALES_AZ_OVERRIDE_KEYSETS={
    },
)
def test_update_localizations_no_az_override(sample_tanker):
    response = django_test.Client().post(
        '/api/update_localizations/',
        json.dumps({'keyset': ['geoareas']}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        'status': 'error',
        'message': (
            'Keyset \'geoareas\' has no override alternative. '
            'Add keyset name or "ignore" to '
            'LOCALES_AZ_OVERRIDE_KEYSETS in config.'
        ),
        'code': 'general',
    }


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'},
    LOCALES_AZ_OVERRIDE_KEYSETS={
        'geoareas': 'fooareas',
    },
)
def test_update_localizations_unknown_az_override(sample_tanker):
    response = django_test.Client().post(
        '/api/update_localizations/',
        json.dumps({'keyset': ['geoareas']}),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        'status': 'error',
        'message': (
            'Keyset \'geoareas\' has invalid override alternative. '
            'Unknown keyset \'fooareas\'.'
        ),
        'code': 'general',
    }


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={
        'geoareas': 'backend.geoareas',
        'override_az': 'backend.override.az',
        'notify': 'backend.notify',
    },
    LOCALES_AZ_OVERRIDE_KEYSETS={
        'geoareas': 'ignore',
        'notify': 'override_az',
    },
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[
        {
            'keyset_name': 'geoareas',
            'key': 'spb',
            'language': 'en',
        },
    ],
)
@pytest.mark.parametrize(
    'keysets,params,expected_code,expected_translations',
    [
        # Happy path
        (
            DEFAULT_KEYSETS,
            {'keyset': ['geoareas']},
            200,
            {
                ('geoareas', 'Yandex', 'en'): 'Yandex',
                ('geoareas', 'Yandex', 'ru'): 'Yandex',
            },
        ),
        # Test that keys with stopwords without an alternative are prohibited
        (
            {
                'backend.notify': {
                    'transporting': {
                        'translations': {
                            'ru': {
                                'form': 'Priehal Yandeks',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Yandex has arrived',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
                'backend.override.az': {}
            },
            {'keyset': ['notify']},
            400,
            None,
        ),
        # Test that keys with stopwords that have an alternative _with_
        # stopwords are prohibited
        (
            {
                'backend.notify': {
                    'transporting': {
                        'translations': {
                            'ru': {
                                'form': 'Priehal Yandeks',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Yandex has arrived',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
                'backend.override.az': {
                    'transporting': {
                        'translations': {
                            'ru': {
                                'form': 'Priehal Yandeks',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Yandex has arrived',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                }
            },
            {'keyset': ['notify']},
            400,
            None,
        ),
        # Test that keys with stopwords that have a stopwords-free alternative
        # are allowed
        (
            {
                'backend.notify': {
                    'transporting': {
                        'translations': {
                            'ru': {
                                'form': 'Priehal Yandeks',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Yandex has arrived',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
                'backend.override.az': {
                    'transporting': {
                        'translations': {
                            'ru': {
                                'form': 'Priehal Uber',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Uber has arrived',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                }
            },
            {'keyset': ['notify']},
            200,
            {
                ('notify', 'transporting', 'en'): 'Yandex has arrived',
                ('notify', 'transporting', 'ru'): 'Priehal Yandeks',
            },
        ),
        # Check that translations with unclosed curly braces are prohibited
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Moscow',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Moscow is the {0 of Great Britain',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            400,
            None,
        ),
        # Check that translations with curly braces closed to soon are
        # prohibited
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Москва - 0} Великобритании',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Moscow is the {0} of Great Britain',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            400,
            None,
        ),
        # Check that placeholders in translation are not required to match
        # placeholders in original text
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Москва - {0} {1}',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Moscow is the {0} of Great Britain',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            200,
            {
                ('geoareas', 'moscow', 'en'): (
                    'Moscow is the {0} of Great Britain'
                ),
                ('geoareas', 'moscow', 'ru'): 'Москва - {0} {1}',
            },
        ),
        # Check that ignored keys are ignored
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Москва - {0} {1}',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'Moscow is the {0} of {1}',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    },
                    'spb': {
                        'translations': {
                            'ru': {
                                'form': 'spb',
                                'status': 'translated'
                            },
                            'en': {
                                'form': 'spb - 0}',
                                'status': 'require_translation'
                            }
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            200,
            {
                ('geoareas', 'moscow', 'en'): 'Moscow is the {0} of {1}',
                ('geoareas', 'moscow', 'ru'): 'Москва - {0} {1}',
                ('geoareas', 'spb', 'en'): 'spb - 0}',
                ('geoareas', 'spb', 'ru'): 'spb',
            },
        ),
        # Check that skipped tail is prohibited
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Москва - %(capital) %(country)s',
                                'status': 'translated'
                            },
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            400,
            None,
        ),
        # Check that skipped parenthesis is prohibited
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Москва - %(capitals %(country)s',
                                'status': 'translated'
                            },
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            400,
            None,
        ),
        (
            {
                'backend.geoareas': {
                    'moscow': {
                        'translations': {
                            'ru': {
                                'form': 'Москва - %(capitals)s %(country).',
                                'status': 'translated'
                            },
                        },
                        'info': {
                            'is_plural': False
                        }
                    }
                },
            },
            {'keyset': ['geoareas']},
            400,
            None,
        ),
    ]
)
@pytest.inline_callbacks
def test_update_localizations(
        sample_tanker, keysets, params, expected_code, expected_translations):
    sample_tanker.set_keysets(keysets)
    response = django_test.Client().post(
        '/api/update_localizations/',
        json.dumps(params),
        content_type='application/json'
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        for key_spec, value in expected_translations.iteritems():
            keyset, key, language = key_spec
            block = getattr(translations.translations, keyset)
            yield block.do_check_and_refresh(None)
            assert block.get_string(key, language) == value


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    TANKER_KEYSETS={
        'geoareas': 'backend.geoareas',
    },
    LOCALIZATIONS_REPLICA_PY2_USAGE_SETTINGS={
        'get_keyset_info': True,
        'request_settings': {
            'timeout': 0,
            'retries': 0,
            'retry_delay': 0,
        },
    },
)
def test_get_keysets(replication_api_mocks):
    response = django_test.Client().get(
        '/api/update_localizations/keysets/')
    assert response.status_code == 200
    assert json.loads(response.content) == ['geoareas']

    response = django_test.Client().get(
        '/api/update_localizations/keysets/?verbose=0')
    assert response.status_code == 200
    assert json.loads(response.content) == ['geoareas']

    response = django_test.Client().get(
        '/api/update_localizations/keysets/?verbose=true')
    assert response.status_code == 200
    assert json.loads(response.content) == [
        {
            'config_name': 'geoareas',
            'tanker_name': 'backend.geoareas',
            'project': 'taxi'
        }
    ]
    assert len(replication_api_mocks['get_keysets'].calls) == 3
