import datetime

import pytest

from tests_driver_metrics_storage import util


@pytest.mark.parametrize('non_transactional_polling', [True, False])
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_oldest(
        taxi_driver_metrics_storage,
        taxi_config,
        non_transactional_polling,
        pgsql,
):
    taxi_config.set_values(
        {
            'DRIVER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS': {
                'new_event_age_limit_mins': 720,
                'idempotency_token_ttl_mins': 1440,
                'default_event_ttl_hours': 168,
                'processing_ticket_ttl_secs': 60,
                'processing_lag_msecs': 200,
                'default_unprocessed_list_limit': 100,
                'round_robin_process': False,
                'non_transactional_polling': non_transactional_polling,
                'polling_max_passes': 3,
            },
        },
    )
    await taxi_driver_metrics_storage.invalidate_caches()
    results = [
        {
            '100000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '100000000000000000000000',
            },
            '200000000000000000000000': {
                'current_activity': 222,
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 4,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '200000000000000000000000',
            },
            '300000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 7,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '300000000000000000000000',
            },
        },
        {
            '400000000000000000000000': {
                'current_activity': 444,
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 10,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '400000000000000000000000',
            },
            '500000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 13,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '500000000000000000000000',
            },
            '600000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 16,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '600000000000000000000000',
            },
        },
        {},
    ]
    assert util.select_named('select * from events.tickets_64', pgsql) == []
    for result in results:
        response = await taxi_driver_metrics_storage.post(
            'v3/events/unprocessed/list',
            json={'consumer': {'index': 0, 'total': 1}, 'limit': 3},
        )
        assert response.status_code == 200
        assert (
            util.to_map(
                response.json()['items'], 'unique_driver_id', util.hide_ticket,
            )
            == result
        )
    assert (
        util.to_map(
            util.select_named('select * from events.tickets_64', pgsql),
            'udid_id',
            util.hide_ticket,
        )
        == {
            1001: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 1,
                'ticket_id': '*',
                'udid_id': 1001,
            },
            1002: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 1,
                'ticket_id': '*',
                'udid_id': 1002,
            },
            1003: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 1,
                'ticket_id': '*',
                'udid_id': 1003,
            },
            1004: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 1,
                'ticket_id': '*',
                'udid_id': 1004,
            },
            1005: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 1,
                'ticket_id': '*',
                'udid_id': 1005,
            },
            1006: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 1,
                'ticket_id': '*',
                'udid_id': 1006,
            },
        }
    )


@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_consumer_oldest(
        taxi_driver_metrics_storage, taxi_config, pgsql,
):
    taxi_config.set_values(
        {
            'DRIVER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS': {
                'new_event_age_limit_mins': 720,
                'idempotency_token_ttl_mins': 1440,
                'default_event_ttl_hours': 168,
                'processing_ticket_ttl_secs': 60,
                'processing_lag_msecs': 200,
                'default_unprocessed_list_limit': 100,
                'round_robin_process': False,
                'non_transactional_polling': True,
                'polling_max_passes': 3,
            },
        },
    )
    await taxi_driver_metrics_storage.invalidate_caches()
    results = [
        {
            '200000000000000000000000': {
                'current_activity': 222,
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 4,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:01+00:00',
                        'event_id': 5,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:02+00:00',
                        'event_id': 6,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '200000000000000000000000',
            },
            '500000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 13,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:01+00:00',
                        'event_id': 14,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:02+00:00',
                        'event_id': 15,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '500000000000000000000000',
            },
        },
        {
            '300000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 7,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:01+00:00',
                        'event_id': 8,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:02+00:00',
                        'event_id': 9,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '300000000000000000000000',
            },
            '600000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 16,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:01+00:00',
                        'event_id': 17,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:02+00:00',
                        'event_id': 18,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '600000000000000000000000',
            },
        },
        {
            '100000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:01+00:00',
                        'event_id': 2,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:02+00:00',
                        'event_id': 3,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '100000000000000000000000',
            },
            '400000000000000000000000': {
                'current_activity': 444,
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 10,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:01+00:00',
                        'event_id': 11,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:00:02+00:00',
                        'event_id': 12,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': '400000000000000000000000',
            },
        },
    ]
    tickets = [
        {
            1002: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1002,
            },
            1005: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1005,
            },
        },
        {
            1002: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1002,
            },
            1003: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1003,
            },
            1005: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1005,
            },
            1006: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1006,
            },
        },
        {
            1001: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1001,
            },
            1002: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1002,
            },
            1003: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1003,
            },
            1004: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1004,
            },
            1005: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1005,
            },
            1006: {
                'deadline': datetime.datetime(2019, 1, 1, 0, 1),
                'down_counter': 3,
                'ticket_id': '*',
                'udid_id': 1006,
            },
        },
    ]
    assert (
        util.to_map(
            util.select_named('select * from events.tickets_64', pgsql),
            'udid_id',
            util.hide_ticket,
        )
        == {}
    )
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 3}, 'limit': 1000},
    )
    assert response.status_code == 200
    assert (
        util.to_map(
            response.json()['items'], 'unique_driver_id', util.hide_ticket,
        ),
        util.to_map(
            util.select_named('select * from events.tickets_64', pgsql),
            'udid_id',
            util.hide_ticket,
        ),
    ) == (results[0], tickets[0])
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 1, 'total': 3}, 'limit': 1000},
    )
    assert response.status_code == 200
    assert (
        util.to_map(
            response.json()['items'], 'unique_driver_id', util.hide_ticket,
        ),
        util.to_map(
            util.select_named('select * from events.tickets_64', pgsql),
            'udid_id',
            util.hide_ticket,
        ),
    ) == (results[1], tickets[1])
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 2, 'total': 3}, 'limit': 1000},
    )
    assert response.status_code == 200
    assert (
        util.to_map(
            response.json()['items'], 'unique_driver_id', util.hide_ticket,
        ),
        util.to_map(
            util.select_named('select * from events.tickets_64', pgsql),
            'udid_id',
            util.hide_ticket,
        ),
    ) == (results[2], tickets[2])
