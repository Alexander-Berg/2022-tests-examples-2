# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)
SETTINGS = {'get_by_id_memoize_time': 0, 'get_by_series_id_memoize_time': 0}


@pytest.fixture
def cache_handler(web_context):
    from corp_tariffs.caches import tariff_plans
    return tariff_plans.TariffPlansHandler(web_context, SETTINGS)


async def test_empty(db, cache_handler):
    await cache_handler.refresh_cache()
    assert not cache_handler._cache.tariff_plans
    assert not cache_handler._cache.tariff_plans_ids


@pytest.mark.parametrize(
    'disabled',
    [
        pytest.param(False, id='cache_enabled'),
        pytest.param(True, id='cache_disabled'),
    ],
)
@pytest.mark.parametrize(
    'refresh_disabled',
    [
        pytest.param(False, id='refresh_enabled'),
        pytest.param(True, id='refresh_disabled'),
    ],
)
async def test_refresh_disabled(
        web_context, db, cache_handler, disabled, refresh_disabled,
):
    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'corp_tariff_plans': {
            'disabled': disabled,
            'refresh_disabled': refresh_disabled,
        },
    }

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_0',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=5),
            'date_to': None,
        },
    )
    await cache_handler.refresh_cache()

    assert bool(cache_handler._cache.tariff_plans) != refresh_disabled
    assert bool(cache_handler._cache.tariff_plans_ids) != refresh_disabled


@pytest.mark.parametrize(
    'disabled',
    [
        pytest.param(False, id='cache_enabled'),
        pytest.param(True, id='cache_disabled'),
    ],
)
@pytest.mark.parametrize(
    'refresh_disabled',
    [
        pytest.param(False, id='refresh_enabled'),
        pytest.param(True, id='refresh_disabled'),
    ],
)
async def test_get_by_id(
        web_context, db, cache_handler, disabled, refresh_disabled,
):

    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'corp_tariff_plans': {
            'disabled': disabled,
            'refresh_disabled': refresh_disabled,
        },
    }

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=5),
            'date_to': None,
        },
    )
    await cache_handler.refresh_cache()

    tariff_plan = await cache_handler.get_by_id('_id_1')
    assert tariff_plan == {
        '_id': '_id_1',
        'tariff_plan_series_id': 'series_id_1',
    }


@pytest.mark.parametrize('refresh_disabled', [False, True])
async def test_get_by_series_id(
        web_context, db, cache_handler, refresh_disabled,
):

    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'corp_tariff_plans': {'refresh_disabled': refresh_disabled},
    }

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_0',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=5),
            'date_to': NOW - datetime.timedelta(days=4),
        },
    )
    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=4),
            'date_to': None,
        },
    )
    await cache_handler.refresh_cache()

    tariff_plan = await cache_handler.get_by_series_id('series_id_1')
    assert tariff_plan == {
        '_id': '_id_1',
        'tariff_plan_series_id': 'series_id_1',
    }


@pytest.mark.now(NOW.isoformat())
async def test_base(db, cache_handler):

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=5),
            'date_to': NOW - datetime.timedelta(days=4),
        },
    )

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_2',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=4),
            'date_to': NOW - datetime.timedelta(days=1),
        },
    )

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_3',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=1),
            'date_to': None,
        },
    )

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_4',
            'tariff_plan_series_id': 'series_id_2',
            'date_from': NOW - datetime.timedelta(days=1),
            'date_to': NOW - datetime.timedelta(seconds=1),
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_plans.keys() == {
        '_id_2',
        '_id_3',
        '_id_4',
    }
    assert cache_handler._cache.tariff_plans_ids == {'series_id_1': '_id_3'}


@pytest.mark.now(NOW.isoformat())
async def test_modified(db, cache_handler):

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=2),
            'date_to': None,
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_plans.keys() == {'_id_1'}
    assert cache_handler._cache.tariff_plans_ids == {'series_id_1': '_id_1'}

    await db.corp_tariff_plans.update_one(
        {'_id': '_id_1'},
        {'$set': {'date_to': NOW - datetime.timedelta(seconds=1)}},
    )

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_2',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=1),
            'date_to': None,
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_plans.keys() == {'_id_1', '_id_2'}
    assert cache_handler._cache.tariff_plans_ids == {'series_id_1': '_id_2'}


@pytest.mark.now(NOW.isoformat())
async def test_partially_modified(db, cache_handler):

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=2),
            'date_to': None,
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_plans.keys() == {'_id_1'}
    assert cache_handler._cache.tariff_plans_ids == {'series_id_1': '_id_1'}

    await db.corp_tariff_plans.update_one(
        {'_id': '_id_1'},
        {'$set': {'date_to': NOW - datetime.timedelta(seconds=1)}},
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_plans.keys() == {'_id_1'}
    assert cache_handler._cache.tariff_plans_ids == {}


@pytest.mark.now(NOW.isoformat())
async def test_tariff_lifetime(db, cache_handler):

    await db.corp_tariff_plans.insert_one(
        {
            '_id': '_id_1',
            'tariff_plan_series_id': 'series_id_1',
            'date_from': NOW - datetime.timedelta(days=2),
            'date_to': NOW - datetime.timedelta(seconds=61),
        },
    )

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_plans.keys() == {'_id_1'}
    assert cache_handler._cache.tariff_plans_ids == {}
