# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import datetime
import json

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.core import translations
from taxi.core.db import classes
from taxi.internal import localization_update


def get_collection_test(keyset, secondary=False):
    con = classes.connections['localizations'][1 if secondary else 0]
    loc = con.localizations
    collection_name = "localization.taxi." + keyset
    collection = getattr(loc, collection_name)
    return collection


@pytest.yield_fixture(autouse=True)
def _clean_localizations():
    yield
    for name in ['color', 'notify', 'tariff', 'order']:
        collection = get_collection_test(name)
        collection.drop()


@async.inline_callbacks
def load_collection(load, keyset):
    try:
        obj = json.loads(load('db_localization_{}.json'.format(keyset)))
    except Exception:
        async.return_value()

    collection = yield localization_update.get_collection(keyset, True)
    for item in obj:
        yield collection.insert(item)


@async.inline_callbacks
def patch_find(monkeypatch, translation, num_reads):
    collection = yield localization_update.get_collection(translation, True)
    original_find = collection.find

    def find(*args, **kwargs):
        num_reads[translation] += 1
        return original_find(*args, **kwargs)

    monkeypatch.setattr(collection, 'find', find)


@pytest.mark.parametrize('lazy,expected_num_reads', [
    (
        False,
        {
            'color': 2,
            'notify': 1,
            'tariff': 2,
            'order': 1,
        },
    ),
    (
        True,
        {
            'color': 2,
            'tariff': 2,
        },
    ),
])
@pytest.mark.now('2019-02-04T12:20:00.0')
@pytest.inline_callbacks
def test_block_reads(load, lazy, expected_num_reads, patch, monkeypatch,
                     invalidate_cache):
    tested_translations = [
        'color',  # has record in meta and is updated
        'notify',  # has record in meta and is not updated
        'tariff',  # has not record in meta and is updated
        'order',  # has not record in meta and is not updated
    ]
    num_reads = collections.defaultdict(int)

    for translation in tested_translations:
        yield load_collection(load, translation)
        yield patch_find(monkeypatch, translation, num_reads)

    translations_obj = translations.Translations(tested_translations)

    if lazy:
        monkeypatch.setattr(settings, 'TRANSLATIONS_LAZY_INITIALIZATION', lazy)
    else:
        yield translations_obj.refresh_all()

    assert translations_obj.color.get_string(
        key='0000CC', language='ru'
    ) == 'синий'
    with pytest.raises(translations.LanguageNotFoundError):
        translations_obj.color.get_string(key='0000CC', language='en')

    assert translations_obj.tariff.get_string(
        key='service_name.bicycle', language='uk'
    ) == 'Перевезення велосипеда, лиж'
    with pytest.raises(translations.TranslationNotFoundError):
        translations_obj.tariff.get_string(
            key='service_name.childchair', language='uk'
        )

    collection_color = yield localization_update.get_collection("color")
    yield collection_color.update(
        {'_id': '0000CC'},
        {
            '$set': {
                'values': [
                    {
                        'conditions': {
                            'locale': {
                                'language': 'en',
                            },
                        },
                        'value': 'blue',
                    },
                    {
                        'conditions': {},
                        'value': 'синий',
                    },
                ],
            },
        },
    )

    collection_tariff = yield localization_update.get_collection("tariff")
    yield collection_tariff.insert(
        {
            '_id': 'service_name.childchair',
            'values': [
                {
                    'conditions': {
                        'locale': {
                            'language': 'uk',
                        }
                    },
                    'value': 'Дитяче крісло',
                },
            ],
        },
    )
    yield db.localizations_meta.update(
        {'_id': 'LAST_UPDATED_META_ID'},
        {
            'value': {
                'color': datetime.datetime(2019, 2, 4, 12, 15),
                'notify': datetime.datetime(2019, 2, 4, 12, 11),
                'tariff': datetime.datetime(2019, 2, 4, 12, 16),
            },
        },
    )

    invalidate_cache()
    if not lazy:
        yield translations_obj.refresh_all()

    assert translations_obj.color.get_string(
        key='0000CC', language='ru'
    ) == 'синий'
    assert translations_obj.color.get_string(
        key='0000CC', language='en'
    ) == 'blue'

    assert translations_obj.tariff.get_string(
        key='service_name.bicycle', language='uk'
    ) == 'Перевезення велосипеда, лиж'
    assert translations_obj.tariff.get_string(
        key='service_name.childchair', language='uk'
    ) == 'Дитяче крісло'

    assert num_reads == expected_num_reads
