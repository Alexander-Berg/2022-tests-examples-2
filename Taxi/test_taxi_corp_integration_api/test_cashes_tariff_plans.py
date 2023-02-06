# pylint: disable=redefined-outer-name,protected-access

import datetime

import pytest

from taxi.util import dates

from taxi_corp_integration_api.generated.service.config import (
    plugin as config_plugin,
)  # noqa:  E501


@pytest.fixture
def cache_plugin(db):
    class ContextStub:
        def __init__(self, db, config):
            self.mongo = db
            self.config = config

    from plugins.corp_tariff_plans_cache import plugin as ctpc_plugin
    plugin = ctpc_plugin.CorpTariffPlansCache(
        ContextStub(db, config_plugin.Config),
    )
    plugin.on_startup()
    return plugin


async def test_base(db, cache_plugin):
    now = dates.utcnow()

    # empty
    await cache_plugin.refresh_cache()
    assert not cache_plugin.cache._tariff_plans
    assert not cache_plugin.cache._tariff_plans_ids

    # insert few tariffs plans
    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': now - datetime.timedelta(days=2),
            'date_to': now - datetime.timedelta(days=1),
        },
    )

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_2',
            'tariff_plan_series_id': 'series_id_2',
            'date_from': now - datetime.timedelta(days=1),
            'date_to': None,
        },
    )

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_3',
            'tariff_plan_series_id': 'series_id_3',
            'date_from': now - datetime.timedelta(days=1),
            'date_to': None,
        },
    )

    await cache_plugin.refresh_cache()
    assert cache_plugin.cache._tariff_plans.keys() == {'_id_2', '_id_3'}
    assert cache_plugin.cache._tariff_plans_ids.keys() == {
        'series_id_2',
        'series_id_3',
    }

    # insert one, remove other
    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_4',
            'tariff_plan_series_id': 'series_id_4',
            'date_from': now - datetime.timedelta(days=1),
            'date_to': None,
        },
    )

    await db.corp_tariff_plans.delete_one({'_id': '_id_3'})

    await cache_plugin.refresh_cache()
    assert cache_plugin.cache._tariff_plans.keys() == {'_id_2', '_id_4'}
    assert cache_plugin.cache._tariff_plans_ids.keys() == {
        'series_id_2',
        'series_id_4',
    }

    # modify one
    await db.corp_tariff_plans.update_one(
        {'tariff_plan_series_id': 'series_id_4'},
        {'$set': {'date_to': now - datetime.timedelta(seconds=1)}},
    )
    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_5',
            'tariff_plan_series_id': 'series_id_5',
            'date_from': now - datetime.timedelta(seconds=1),
            'date_to': None,
        },
    )

    await cache_plugin.refresh_cache()
    assert cache_plugin.cache._tariff_plans.keys() == {'_id_2', '_id_5'}
    assert cache_plugin.cache._tariff_plans_ids.keys() == {
        'series_id_2',
        'series_id_5',
    }
