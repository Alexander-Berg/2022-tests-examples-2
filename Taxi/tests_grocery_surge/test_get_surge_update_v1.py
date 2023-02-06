import datetime

import pytest

from . import consts

INIT_RECORDS = []
for ts in consts.TIMESTAMPS:
    INIT_RECORDS.append(
        consts.insert_surge_query(ts, '100', delivery_types=['yandex_taxi']),
    )
    INIT_RECORDS.append(
        consts.insert_surge_query(
            ts, '101', delivery_types=['pedestrian', 'yandex_taxi_remote'],
        ),
    )
    INIT_RECORDS.append(
        consts.insert_surge_query(ts, '102', delivery_types=[]),
    )
LONG_TIME_AGO = consts.NOW - datetime.timedelta(hours=30)


@pytest.mark.now(consts.NOW.isoformat())
@pytest.mark.config(
    GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
        'calculated_surge_info_ttl': consts.CALCULATED_SURGE_INFO_TTL,
    },
)
@pytest.mark.parametrize('use_surge_cache_component', [False, True])
@pytest.mark.pgsql(
    'grocery-surge',
    queries=[
        consts.insert_surge_query(
            consts.TIMESTAMPS[0],
            '1',
            delivery_types=['pedestrian', 'yandex_taxi'],
        ),
        consts.insert_surge_query(consts.TIMESTAMPS[0], '2'),
        consts.insert_surge_query(consts.TIMESTAMPS[0], '4'),
        consts.insert_surge_query(consts.TIMESTAMPS[0], '3'),
    ],
)
async def test_get_surge_update_sorted_by_seq(
        taxi_grocery_surge, taxi_config, use_surge_cache_component,
):
    taxi_config.set(
        GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
            'calculated_surge_info_ttl': consts.CALCULATED_SURGE_INFO_TTL,
            'use_surge_cache_component': use_surge_cache_component,
        },
    )
    await taxi_grocery_surge.invalidate_caches()

    data = {'cursor': '0', 'limit': 4, 'active_only': False}
    response = await taxi_grocery_surge.post(
        '/internal/v1/surge/update', json=data,
    )
    assert response.status_code == 200
    update = response.json()
    assert update['cursor'] == '4'
    data = update['data']
    assert data[0] == {
        'delivery_types': ['pedestrian', 'yandex_taxi'],
        'depot_id': '1',
        'pipeline': 'pipeline_1',
        'surge_info': {'load_level': 777.0},
        'timestamp': consts.TIMESTAMPS[0].isoformat(),
    }
    assert [record['depot_id'] for record in data] == ['1', '2', '4', '3']


@pytest.mark.now(consts.NOW.isoformat())
@pytest.mark.config(
    GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
        'calculated_surge_info_ttl': consts.CALCULATED_SURGE_INFO_TTL,
    },
)
@pytest.mark.pgsql('grocery-surge', queries=INIT_RECORDS)
@pytest.mark.parametrize('use_surge_cache_component', [False, True])
@pytest.mark.parametrize(
    'limit, active_only, cursor, time_from, expected_size, expected_cursor',
    [
        (1, False, 0, consts.NOW + datetime.timedelta(seconds=1), 0, 0),
        (5, False, len(INIT_RECORDS), LONG_TIME_AGO, 0, len(INIT_RECORDS)),
        (5, False, len(INIT_RECORDS) - 2, LONG_TIME_AGO, 2, len(INIT_RECORDS)),
        (5, False, 0, LONG_TIME_AGO, 5, 5),
        (5, True, 0, LONG_TIME_AGO, 5, 7),
    ],
)
async def test_get_surge_update(
        taxi_grocery_surge,
        taxi_config,
        use_surge_cache_component,
        limit,
        active_only,
        cursor,
        time_from,
        expected_size,
        expected_cursor,
):
    taxi_config.set(
        GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
            'calculated_surge_info_ttl': consts.CALCULATED_SURGE_INFO_TTL,
            'use_surge_cache_component': use_surge_cache_component,
        },
    )
    await taxi_grocery_surge.invalidate_caches()

    data = {
        'cursor': str(cursor),
        'time_from': time_from.isoformat(timespec='milliseconds'),
        'limit': limit,
        'active_only': active_only,
    }
    response = await taxi_grocery_surge.post(
        '/internal/v1/surge/update', json=data,
    )
    assert response.status_code == 200
    update = response.json()

    data = update['data']
    assert len(data) == expected_size
    assert update['cursor'] == str(expected_cursor)

    if expected_size == 0:
        return  # nothing left to check

    if active_only:
        contains_nonactive = any(
            not (record['delivery_types']) for record in data
        )
        assert contains_nonactive is False


CALCULATED_SURGE_INFO_TTL_SMALL = 5


@pytest.mark.now(consts.NOW.isoformat())
@pytest.mark.config(
    GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
        'calculated_surge_info_ttl': CALCULATED_SURGE_INFO_TTL_SMALL,
    },
)
@pytest.mark.parametrize('use_surge_cache_component', [False, True])
@pytest.mark.pgsql('grocery-surge', queries=INIT_RECORDS)
async def test_get_surge_update_ttl(
        taxi_grocery_surge, taxi_config, use_surge_cache_component,
):
    taxi_config.set(
        GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
            'calculated_surge_info_ttl': CALCULATED_SURGE_INFO_TTL_SMALL,
            'use_surge_cache_component': use_surge_cache_component,
        },
    )
    await taxi_grocery_surge.invalidate_caches()

    data = {'limit': 100, 'active_only': False}
    response = await taxi_grocery_surge.post(
        '/internal/v1/surge/update', json=data,
    )
    assert response.status_code == 200
    data = response.json()['data']

    assert len(data) == 15  # ttl * 3. See INIT_RECORDS
    earliest_created = min(
        datetime.datetime.fromisoformat(record['timestamp']) for record in data
    )
    assert earliest_created >= consts.NOW - datetime.timedelta(
        seconds=CALCULATED_SURGE_INFO_TTL_SMALL,
    )


@pytest.mark.now(consts.NOW.isoformat())
@pytest.mark.config(
    GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
        'calculated_surge_info_ttl': consts.CALCULATED_SURGE_INFO_TTL,
    },
)
@pytest.mark.parametrize('use_surge_cache_component', [False, True])
@pytest.mark.pgsql('grocery-surge', queries=INIT_RECORDS)
async def test_get_surge_bad_request(
        taxi_grocery_surge, taxi_config, use_surge_cache_component,
):
    taxi_config.set(
        GROCERY_SURGE_CALCULATION_CACHE_SETTINGS={
            'calculated_surge_info_ttl': consts.CALCULATED_SURGE_INFO_TTL,
            'use_surge_cache_component': use_surge_cache_component,
        },
    )
    await taxi_grocery_surge.invalidate_caches()

    data = {'cursor': '0xdeadbeef', 'limit': 100, 'active_only': False}
    response = await taxi_grocery_surge.post(
        '/internal/v1/surge/update', json=data,
    )
    assert response.status_code == 400
