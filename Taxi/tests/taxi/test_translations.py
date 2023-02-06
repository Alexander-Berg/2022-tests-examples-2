# pylint: disable=redefined-outer-name,protected-access,unused-variable
# pylint: disable=invalid-name
import collections
import datetime
import json
import uuid

import aiohttp
import pytest

from taxi import config
from taxi import settings
from taxi import translations
from taxi.clients import localizations


def patch_find(monkeypatch, db, translation, num_reads):
    collection = getattr(db.secondary, 'localization_{}'.format(translation))
    original_find = collection.find

    def find(*args, **kwargs):
        num_reads[translation] += 1
        return original_find(*args, **kwargs)

    monkeypatch.setattr(collection, 'find', find)


@pytest.fixture
async def translations_cache(monkeypatch, loop, db):
    _session = aiohttp.ClientSession()

    def _translations(
            keyset_list, localizations_config=None, force_use_service=False,
    ):
        _config = config.Config()
        _settings = settings.Settings()
        if localizations_config is not None:
            monkeypatch.setattr(
                _config, 'LOCALIZATIONS_DATA_SOURCE_PY3', localizations_config,
            )
            _localizations = localizations.Localizations(
                session=_session,
                service_url='http://localizations-replica.taxi.dev.yandex.net',
            )
        else:
            _localizations = None

        return translations.Translations(
            loop,
            db if not force_use_service else None,
            _config,
            _settings,
            keyset_list,
            _localizations,
        )

    yield _translations
    await _session.close()


@pytest.mark.now('2019-02-04T12:20:00.0')
@pytest.mark.mongodb_collections(
    'localization_color',
    'localization_notify',
    'localization_tariff',
    'localization_order',
    'localizations_meta',
)
async def test_refresh_cache(loop, db, monkeypatch):
    tested_translations = [
        'color',  # has record in meta and is updated
        'notify',  # has record in meta and is not updated
        'tariff',  # has not record in meta and is updated
        'order',  # has not record in meta and is not updated
    ]
    num_reads = collections.defaultdict(int)

    for translation in tested_translations:
        patch_find(monkeypatch, db, translation, num_reads)

    translations_obj = translations.Translations(
        loop, db, config.Config(), settings.Settings(), tested_translations,
    )

    await translations_obj.refresh_cache()

    assert (
        translations_obj.color.get_string(key='0000CC', language='ru')
        == 'синий'
    )
    with pytest.raises(translations.LanguageNotFoundError):
        translations_obj.color.get_string(key='0000CC', language='en')

    assert (
        translations_obj.tariff.get_string(
            key='service_name.bicycle', language='uk',
        )
        == 'Перевезення велосипеда, лиж'
    )
    with pytest.raises(translations.TranslationNotFoundError):
        translations_obj.tariff.get_string(
            key='service_name.childchair', language='uk',
        )

    await db.localization_color.update(
        {'_id': '0000CC'},
        {
            '$set': {
                'values': [
                    {
                        'conditions': {'locale': {'language': 'en'}},
                        'value': 'blue',
                    },
                    {'conditions': {}, 'value': 'синий'},
                ],
            },
        },
    )
    await db.localization_tariff.insert(
        {
            '_id': 'service_name.childchair',
            'values': [
                {
                    'conditions': {'locale': {'language': 'uk'}},
                    'value': 'Дитяче крісло',
                },
            ],
        },
    )
    await db.localizations_meta.update(
        {'_id': 'LAST_UPDATED_META_ID'},
        {
            'value': {
                'color': datetime.datetime(2019, 2, 4, 12, 15),
                'notify': datetime.datetime(2019, 2, 4, 12, 11),
                'tariff': datetime.datetime(2019, 2, 4, 12, 16),
            },
        },
    )

    await translations_obj.refresh_cache()

    assert (
        translations_obj.color.get_string(key='0000CC', language='ru')
        == 'синий'
    )
    assert (
        translations_obj.color.get_string(key='0000CC', language='en')
        == 'blue'
    )

    assert (
        translations_obj.tariff.get_string(
            key='service_name.bicycle', language='uk',
        )
        == 'Перевезення велосипеда, лиж'
    )
    assert (
        translations_obj.tariff.get_string(
            key='service_name.childchair', language='uk',
        )
        == 'Дитяче крісло'
    )

    expected_num_reads = {'color': 2, 'notify': 1, 'tariff': 2, 'order': 1}
    assert num_reads == expected_num_reads


async def test_use_service(
        load, patch_aiohttp_session, response_mock, translations_cache,
):
    @patch_aiohttp_session(
        'http://localizations-replica.taxi.dev.yandex.net/v1/keyset', 'GET',
    )
    def get_keyset_mock(*args, **kwargs):
        name = kwargs['params']['name']
        f_name = f'service_localization_{name}.json'
        return response_mock(read=load(f_name))

    tested_translations = ['color', 'tariff']

    translations_obj = translations_cache(
        tested_translations, {'source': 'service', 'verifications': False},
    )

    await translations_obj.refresh_cache()
    assert len(get_keyset_mock.calls) == 2
    assert (
        translations_obj.tariff._last_updated
        == datetime.datetime(2019, 6, 28, 13, 18, 33).isoformat()
    )


@pytest.mark.mongodb_collections('localization_color', 'localization_tariff')
async def test_use_service_with_diff(
        caplog, load, patch_aiohttp_session, response_mock, translations_cache,
):
    @patch_aiohttp_session(
        'http://localizations-replica.taxi.dev.yandex.net/v1/keyset', 'GET',
    )
    def get_keyset_mock(*args, **kwargs):
        name = kwargs['params']['name']
        f_name = f'service_localization_{name}_with_diff.json'
        return response_mock(read=load(f_name))

    tested_translations = ['color', 'tariff']
    translations_obj = translations_cache(
        tested_translations, {'source': 'service', 'verifications': True},
    )

    await translations_obj.refresh_cache()
    assert len(get_keyset_mock.calls) == 2

    records = [r for r in caplog.records if r.levelname == 'ERROR']
    assert len(records) == 4

    records_for_keys_errors = [
        r
        for r in records
        if r.message.startswith('Values for key')
        and 'are different' in r.message
    ]
    assert len(records_for_keys_errors) == 2
    assert (
        {
            (
                'Values for key (\'service_name.bicycle\', 1, \'uk\') '
                'from source and from verify_with_source are different',
                ('tariff', 'service', 'mongo'),
            ),
            (
                'Values for key (\'0000CC\', 1, \'ru\') '
                'from source and from verify_with_source are different',
                ('color', 'service', 'mongo'),
            ),
        }
        == {
            (
                r.message,
                (
                    r.extdict['keyset'],
                    r.extdict['source'],
                    r.extdict['verify_with_source'],
                ),
            )
            for r in records_for_keys_errors
        }
    )

    records_for_verification_results = [
        r for r in records if 'verification failed' in r.message
    ]
    assert len(records_for_verification_results) == 2
    assert {
        'tariff keyset verification failed. 1 keys differs',
        'color keyset verification failed. 1 keys differs',
    } == {r.message for r in records_for_verification_results}


@pytest.mark.mongodb_collections(
    'localization_color', 'localization_tariff', 'localizations_meta',
)
async def test_verifications_no_updates(
        caplog, patch_aiohttp_session, response_mock, translations_cache,
):
    @patch_aiohttp_session(
        'http://localizations-replica.taxi.dev.yandex.net/v1/keyset', 'GET',
    )
    def get_keyset_mock(*args, **kwargs):
        return response_mock(status=304)

    tested_translations = ['color', 'tariff']
    translations_obj = translations_cache(
        tested_translations, {'source': 'mongo', 'verifications': True},
    )
    await translations_obj.refresh_cache()
    assert len(get_keyset_mock.calls) == 2

    records = [r for r in caplog.records if r.levelname == 'WARNING']
    assert len(records) == 2

    assert {
        'Received no updates from service verify_with_source '
        'for tariff keyset',
        'Received no updates from service verify_with_source '
        'for color keyset',
    } == {r.message for r in records}


@pytest.mark.parametrize(
    'status_code,response_body_f_name,result_translations_in_block',
    [
        (
            200,
            'service_localization_color.json',
            {('0000CC', 1, 'ru'): 'синий'},
        ),
        (
            304,
            'service_localization_color_empty.json',
            {('0000CC', 1, 'ru'): 'син'},
        ),
    ],
)
async def test_localizations_usage(
        load,
        patch_aiohttp_session,
        response_mock,
        status_code,
        response_body_f_name,
        result_translations_in_block,
        translations_cache,
):
    @patch_aiohttp_session(
        'http://localizations-replica.taxi.dev.yandex.net/v1/keyset', 'GET',
    )
    def get_keyset_mock(*args, **kwargs):
        return response_mock(
            read=load(response_body_f_name), status=status_code,
        )

    init_translations = {
        '_id': '0000CC',
        'values': [
            {
                'conditions': {'locale': {'language': 'ru'}},
                'form': 1,
                'value': 'син',
            },
        ],
    }

    tested_translations = ['color']
    translations_obj = translations_cache(
        tested_translations, {'source': 'service', 'verifications': False},
    )

    translations_obj.color._process_item(init_translations)
    await translations_obj.color.check_and_refresh(None)
    assert translations_obj.color._translations == result_translations_in_block
    assert (
        translations_obj.color.get_string(key='0000CC', language='ru')
        == result_translations_in_block[('0000CC', 1, 'ru')]
    )


async def test_force_use_service(monkeypatch, patch, translations_cache):
    @patch('taxi.clients.localizations.Localizations.get_keyset')
    async def get_keyset_mock(keyset_name, last_update, log_extra=None):
        return {
            'name': keyset_name,
            'keys': [
                {
                    '_id': '0000CC',
                    'values': [
                        {
                            'conditions': {'locale': {'language': 'ru'}},
                            'form': 1,
                            'value': 'син',
                        },
                    ],
                },
            ],
        }

    class DummyUUID(uuid.UUID):
        @property
        def hex(self):
            return 'hex'

    monkeypatch.setattr('uuid.UUID', DummyUUID)

    translations_obj = translations_cache(
        ['color'],
        {'source': 'mongo', 'verifications': False},
        force_use_service=True,
    )

    await translations_obj.refresh_cache()
    assert get_keyset_mock.calls == [
        {
            'keyset_name': 'color',
            'last_update': None,
            'log_extra': {
                '_link': 'hex',
                'extdict': {'keyset': 'color', 'source': 'service'},
            },
        },
    ]


@pytest.mark.parametrize(
    'status,json_response,expected,expected_last_update_type',
    [
        (304, None, {('0000CC', 1, 'ru'): 'синий'}, datetime.datetime),
        (
            200,
            {
                'keyset_name': 'color',
                'keys': [
                    {
                        'key_id': '0000CC',
                        'values': [{'conditions': {}, 'value': 'син'}],
                    },
                ],
                'last_update': '2019-07-08T14:43:39.771872Z',
            },
            {('0000CC', 1, 'ru'): 'син'},
            str,
        ),
    ],
)
@pytest.mark.mongodb_collections('localization_color', 'localizations_meta')
async def test_service_usage_switch(
        patch_aiohttp_session,
        response_mock,
        translations_cache,
        status,
        json_response,
        expected,
        expected_last_update_type,
):
    @patch_aiohttp_session(
        'http://localizations-replica.taxi.dev.yandex.net/v1/keyset', 'GET',
    )
    def get_keyset_mock(*args, **kwargs):
        return response_mock(status=status, read=json.dumps(json_response))

    translations_obj = translations_cache(
        ['color'], {'source': 'mongo', 'verifications': False},
    )

    # initial call, using mongo
    assert translations_obj.color._translations == {}
    await translations_obj.refresh_cache()
    assert translations_obj.color._translations == {
        ('0000CC', 1, 'ru'): 'синий',
    }
    assert isinstance(translations_obj.color._last_updated, datetime.datetime)

    # change data source to service and call update
    translations_obj.config.LOCALIZATIONS_DATA_SOURCE_PY3['source'] = 'service'
    await translations_obj.refresh_cache()
    assert len(get_keyset_mock.calls) == 1
    assert translations_obj.color._translations == expected
    assert isinstance(
        translations_obj.color._last_updated, expected_last_update_type,
    )

    # check is every thing is ok with second service update call
    await translations_obj.refresh_cache()

    # change back to mongo and update
    translations_obj.config.LOCALIZATIONS_DATA_SOURCE_PY3['source'] = 'mongo'
    await translations_obj.refresh_cache()
    assert isinstance(translations_obj.color._last_updated, datetime.datetime)
    assert translations_obj.color._translations == {
        ('0000CC', 1, 'ru'): 'синий',
    }


@pytest.mark.mongodb_collections('localization_corp', 'localizations_meta')
async def test_service_source_no_localizations_client(monkeypatch, loop, db):
    _config = config.Config()
    monkeypatch.setattr(
        _config,
        'LOCALIZATIONS_DATA_SOURCE_PY3',
        {'source': 'service', 'verifications': True},
    )

    num_reads = collections.defaultdict(int)
    tested_translations = ['corp']
    for translation in tested_translations:
        patch_find(monkeypatch, db, translation, num_reads)
    await db.localizations_meta.update(
        {'_id': 'LAST_UPDATED_META_ID'},
        {'value': {'corp': datetime.datetime(2019, 2, 4, 12, 15)}},
    )

    _translations = translations.Translations(
        loop=loop,
        db=db,
        config=_config,
        settings=settings.Settings(),
        blocks=tested_translations,
    )

    await _translations.init_cache()
    assert _translations.corp._last_updated is not None
    await _translations.refresh_cache()

    assert num_reads['corp'] == 2


async def test_block_not_found_as_attribute(loop, db):
    tested_translations = ['color']

    translations_obj = translations.Translations(
        loop, db, config.Config(), settings.Settings(), tested_translations,
    )

    with pytest.raises(AttributeError):
        getattr(translations_obj, 'shape')

    assert hasattr(translations_obj, 'shape') is False
    assert hasattr(translations_obj, 'color') is True
