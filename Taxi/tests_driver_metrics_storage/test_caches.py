# -*- coding: utf-8 -*-

import asyncio
import datetime

import pytest

from tests_driver_metrics_storage import util


async def test_64(pgsql):

    cursor = pgsql['drivermetrics'].conn.cursor()
    cursor.execute(
        'select setval(\'events.queue_event_id_seq\'::regclass,2147483647)',
    )
    cursor.execute(
        'INSERT INTO events.queue_64 (udid_id,event_type_id,created,deadline)'
        'VALUES'
        '(1000,1,\'2000-01-01T00:00:00+0000\',\'2999-01-01T00:00:00+0000\'),'
        '(1000,1,\'2000-01-01T00:00:00+0000\',\'2999-01-01T00:00:00+0000\'),'
        '(1000,1,\'2000-01-01T00:00:00+0000\',\'2999-01-01T00:00:00+0000\'),'
        '(2000,1,\'2000-01-01T00:00:00+0000\',\'2999-01-01T00:00:00+0000\'),'
        '(2000,1,\'2000-01-01T00:00:00+0000\',\'2999-01-01T00:00:00+0000\'),'
        '(2000,1,\'2000-01-01T00:00:00+0000\',\'2999-01-01T00:00:00+0000\');',
    )

    for table in ['queue_64']:
        assert (
            util.select_named(
                'SELECT event_id,udid_id FROM events.' + table, pgsql,
            )
            == [
                {'event_id': 2147483648, 'udid_id': 1000},
                {'event_id': 2147483649, 'udid_id': 1000},
                {'event_id': 2147483650, 'udid_id': 1000},
                {'event_id': 2147483651, 'udid_id': 2000},
                {'event_id': 2147483652, 'udid_id': 2000},
                {'event_id': 2147483653, 'udid_id': 2000},
            ]
        )


@pytest.mark.now('2000-12-31T23:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_caches(taxi_driver_metrics_storage, pgsql):

    await taxi_driver_metrics_storage.invalidate_caches()
    await asyncio.sleep(2)

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert 'items' in body
    assert (
        util.to_map(body['items'], 'unique_driver_id', util.hide_ticket)
        == {
            '100000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '100000000000000000000000',
            },
        }
    )

    cursor = pgsql['drivermetrics'].conn.cursor()
    cursor.execute(
        'update common.udids set udid=concat(\'udid =\',udid_id,\'=\')',
    )
    cursor.execute(
        'update common.event_types'
        ' set event_type=concat(\'type =\',event_type_id,\'=\')',
    )
    cursor.execute('delete from events.tickets_64')

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert 'items' in body
    assert (
        util.to_map(body['items'], 'unique_driver_id', util.hide_ticket)
        == {
            '100000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '100000000000000000000000',
            },
        }
    )

    await taxi_driver_metrics_storage.invalidate_caches()
    await asyncio.sleep(2)

    cursor.execute('delete from events.tickets_64')

    await taxi_driver_metrics_storage.invalidate_caches()
    await asyncio.sleep(2)
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 1},
    )
    body = response.json()
    assert 'items' in body
    assert (
        util.to_map(body['items'], 'unique_driver_id', util.hide_ticket)
        == {
            'udid =1001=': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'type': 'type =1=',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': 'udid =1001=',
            },
        }
    )


@pytest.mark.now('2000-12-31T23:00:00+0000')
@pytest.mark.parametrize('cache_name', ['postgres-cache-merged-udids'])
async def test_merged_udids_cache(
        taxi_driver_metrics_storage,
        cache_name,
        read_latest_dump,
        mocked_time,
        pgsql,
):
    await taxi_driver_metrics_storage.write_cache_dumps(names=[cache_name])
    dump = read_latest_dump(cache_name)
    assert dump == b'\x00'

    response = await taxi_driver_metrics_storage.post(
        '/internal/v1/unique_drivers/merge_ids',
        json={
            'events': [
                {
                    # internal ids: 1, 2
                    'unique_driver': {'id': 'target_udid1'},
                    'merged_unique_driver': {'id': 'source_udid1'},
                },
                {
                    # internal ids: 3, 4
                    'unique_driver': {'id': 'target_udid2'},
                    'merged_unique_driver': {'id': 'source_udid2'},
                },
                {
                    # internal ids 1, 5
                    'unique_driver': {'id': 'target_udid1'},
                    'merged_unique_driver': {'id': 'source_udid3'},
                },
            ],
        },
    )
    assert response.status_code == 200

    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))
    await taxi_driver_metrics_storage.invalidate_caches(
        clean_update=True, cache_names=[cache_name],
    )

    await taxi_driver_metrics_storage.write_cache_dumps(names=[cache_name])
    dump = read_latest_dump(cache_name)
    assert dump == (
        # format:  total cache count, pairs of key-value
        b'\x02'
        # format:  keyN, udid_idN,
        #          merged_count, (merged_udid_idM, optional erasure_at)...
        + (b'\x03' + b'\x03' + (b'\x01' + b'\x04\x00'))
        + (b'\x01' + b'\x01' + (b'\x02' + b'\x02\x00' + b'\x05\x00'))
    )
    await taxi_driver_metrics_storage.read_cache_dumps(names=[cache_name])
