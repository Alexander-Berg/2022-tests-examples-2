# pylint: disable=protected-access
import typing

import pytest

from mia.crontasks import user_phone_wrapper
from mia.crontasks.extra_fetcher import extra_fetcher
from mia.crontasks.extra_fetcher import extra_fetcher_taxi
from mia.crontasks.request_parser import request_parser_taxi
from test_mia.cron import timezone_dummy
from test_mia.cron import user_phone_dummy
from test_mia.cron import yt_dummy

USER_PHONE_WRAPPER_DUMMY = typing.cast(
    user_phone_wrapper.UserPhoneWrapper,
    user_phone_dummy.UserPhoneWrapperDummy(
        {
            'test_phone_0': [],
            'test_phone_1': ['id_1_1'],
            'test_phone_2': ['id_2_1', 'id_2_2'],
            'test_phone_3': ['id_3_1', 'id_3_2', 'id_3_3'],
        },
    ),
)


@pytest.fixture(name='fetcher')
def create_fetcher(yt_client):
    return extra_fetcher_taxi.ExtraFetcherTaxi(
        yt_dummy.YtLocalDummy(yt_client),
        timezone_dummy.TimezoneWrapperDummy(
            {
                'test_nearest_zone_2': 'test_zone_2',
                'test_nearest_zone_3': 'test_zone_3',
            },
        ),
        USER_PHONE_WRAPPER_DUMMY,
    )


@pytest.mark.parametrize(
    'rows, config, expected',
    [
        (
            [
                {
                    'order_id': 'test_order_id_2',
                    'created_idx': 1578225700,
                    'user_phone_id': 'id_1_1',
                },
                {
                    'order_id': 'test_order_id_3',
                    'created_idx': 1581681600,
                    'request_source': {'contact_phone_id': 'id_2_1'},
                    'request_destinations': [
                        {'contact_phone_id': 'id_2_2'},
                        {'contact_phone_id': 'id_3_1'},
                    ],
                },
            ],
            request_parser_taxi.ProcessorsConfigTaxi(False, True),
            [
                extra_fetcher_taxi.RowWithExtraTaxi(
                    row={
                        'order_id': 'test_order_id_2',
                        'created_idx': 1578225700,
                        'user_phone_id': 'id_1_1',
                        'user_phone': 'test_phone_1',
                    },
                    order={
                        'id': 'test_order_id_2',
                        'performer_clid': 'test_park_id_2',
                        'nearest_zone': 'test_nearest_zone_2',
                        'status': 'test_status_2',
                        'taxi_status': 'test_taxi_status_2',
                        'performer_db_id': 'test_pda_park_id_2',
                        'performer_taxi_alias_id': (
                            'test_performer_taxi_alias_id_2'
                        ),
                        'statistics': 'test_statistics_2',
                        'feedback': 'test_feedback_2',
                        'cost': 2.2,
                        'order_events': 'test_order_events_2',
                        'request_source': 'test_request_source_2',
                        'request_destinations': 'test_request_destinations_2',
                        'payment_tech_type': 'test_payment_tech_type_2',
                        'chat_id': 'chat_id_2',
                    },
                    park={
                        'id': 'test_park_id_2',
                        'name': 'test_park_name_2',
                        'phone': 'test_park_phone_2',
                    },
                    pda_park={
                        'id': 'test_pda_park_id_2',
                        'name': 'test_pda_park_name_2',
                        'contacts': 'test_pda_park_contacts_2',
                    },
                    timezone='test_zone_2',
                    chat_updates=[
                        {
                            'chat_id': 'chat_id_2',
                            'update_id': 'update_1',
                            'data': {
                                'created_date': '2020-01-01T00:00:00.000000Z',
                                'message': {
                                    'sender': {'role': 'driver'},
                                    'text': 'text 1',
                                },
                            },
                        },
                        {
                            'chat_id': 'chat_id_2',
                            'update_id': 'update_2',
                            'data': {
                                'created_date': '2020-01-01T00:00:01.000000Z',
                                'message': {
                                    'sender': {'role': 'client'},
                                    'text': 'text 2',
                                },
                            },
                        },
                    ],
                    chat_translations=[
                        {
                            'chat_id': 'chat_id_2',
                            'update_id': 'update_1',
                            'text': 'translation 1',
                        },
                        {
                            'chat_id': 'chat_id_2',
                            'update_id': 'update_2',
                            'text': 'translation 2',
                        },
                    ],
                ),
                extra_fetcher_taxi.RowWithExtraTaxi(
                    row={
                        'order_id': 'test_order_id_3',
                        'created_idx': 1581681600,
                        'request_source': {
                            'contact_phone_id': 'id_2_1',
                            'contact_phone': 'test_phone_2',
                        },
                        'request_destinations': [
                            {
                                'contact_phone_id': 'id_2_2',
                                'contact_phone': 'test_phone_2',
                            },
                            {
                                'contact_phone_id': 'id_3_1',
                                'contact_phone': 'test_phone_3',
                            },
                        ],
                    },
                    order={
                        'id': 'test_order_id_3',
                        'performer_clid': 'test_park_id_3',
                        'nearest_zone': 'test_nearest_zone_3',
                        'status': 'test_status_3',
                        'taxi_status': 'test_taxi_status_3',
                        'performer_db_id': 'test_pda_park_id_3',
                        'performer_taxi_alias_id': (
                            'test_performer_taxi_alias_id_3'
                        ),
                        'statistics': 'test_statistics_3',
                        'feedback': 'test_feedback_3',
                        'cost': 3.3,
                        'order_events': 'test_order_events_3',
                        'request_source': 'test_request_source_3',
                        'request_destinations': 'test_request_destinations_3',
                        'payment_tech_type': 'test_payment_tech_type_3',
                        'chat_id': None,
                    },
                    park={
                        'id': 'test_park_id_3',
                        'name': 'test_park_name_3',
                        'phone': 'test_park_phone_3',
                    },
                    pda_park={
                        'id': 'test_pda_park_id_3',
                        'name': 'test_pda_park_name_3',
                        'contacts': 'test_pda_park_contacts_3',
                    },
                    timezone='test_zone_3',
                    chat_updates=[],
                    chat_translations=[],
                ),
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_parks.yaml',
        'yt_pda_parks.yaml',
        'yt_taxi_orders_monthly_2020_01.yaml',
        'yt_taxi_orders_monthly_2020_02.yaml',
        'yt_taxi_chat_updates.yaml',
        'yt_taxi_chat_translations.yaml',
    ],
)
async def test_fetch_extra(
        rows, config, expected, yt_apply, yt_client, fetcher,
):
    assert await fetcher.fetch_extra(rows, config) == expected


DEFAULT_PROCESSORS_CONFIG = request_parser_taxi.ProcessorsConfigTaxi(
    False, False,
)


@pytest.mark.parametrize(
    'rows', [[{'order_id': 'test_order_id_4', 'created_idx': 1581681600}]],
)
@pytest.mark.yt(dyn_table_data=['yt_taxi_orders_monthly_2020_02.yaml'])
async def test_fetch_extra_order_not_found(rows, yt_apply, yt_client, fetcher):
    try:
        await fetcher.fetch_extra(rows, DEFAULT_PROCESSORS_CONFIG)
    except extra_fetcher.OrderNotFound:
        return
    assert False


@pytest.mark.parametrize(
    'rows', [[{'order_id': 'test_order_id_1', 'created_idx': 1578225600}]],
)
@pytest.mark.yt(dyn_table_data=['yt_taxi_orders_monthly_2020_01.yaml'])
async def test_fetch_extra_unknown_timezone(
        rows, yt_apply, yt_client, fetcher,
):
    try:
        await fetcher.fetch_extra(rows, DEFAULT_PROCESSORS_CONFIG)
    except extra_fetcher_taxi.UnknownTimeZone:
        return
    assert False


@pytest.mark.parametrize(
    'orders, expected',
    [
        ([], []),
        (
            [{'performer_clid': 'test_park_id_1'}],
            [
                {
                    'id': 'test_park_id_1',
                    'name': 'test_park_name_1',
                    'phone': 'test_park_phone_1',
                },
            ],
        ),
        (
            [
                {'performer_clid': 'test_park_id_1'},
                {'performer_clid': 'test_park_id_2'},
                {'performer_clid': 'test_park_id_3'},
            ],
            [
                {
                    'id': 'test_park_id_1',
                    'name': 'test_park_name_1',
                    'phone': 'test_park_phone_1',
                },
                {
                    'id': 'test_park_id_2',
                    'name': 'test_park_name_2',
                    'phone': 'test_park_phone_2',
                },
                {
                    'id': 'test_park_id_3',
                    'name': 'test_park_name_3',
                    'phone': 'test_park_phone_3',
                },
            ],
        ),
        ([{'performer_clid': 'test_park_id_4'}], []),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_parks.yaml'])
async def test_fetch_parks(orders, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_parks(orders)

    assert result == expected


@pytest.mark.parametrize(
    'orders, expected',
    [
        ([], []),
        (
            [{'performer_db_id': 'test_pda_park_id_1'}],
            [
                {
                    'id': 'test_pda_park_id_1',
                    'name': 'test_pda_park_name_1',
                    'contacts': 'test_pda_park_contacts_1',
                },
            ],
        ),
        (
            [
                {'performer_db_id': 'test_pda_park_id_1'},
                {'performer_db_id': 'test_pda_park_id_2'},
                {'performer_db_id': 'test_pda_park_id_3'},
            ],
            [
                {
                    'id': 'test_pda_park_id_1',
                    'name': 'test_pda_park_name_1',
                    'contacts': 'test_pda_park_contacts_1',
                },
                {
                    'id': 'test_pda_park_id_2',
                    'name': 'test_pda_park_name_2',
                    'contacts': 'test_pda_park_contacts_2',
                },
                {
                    'id': 'test_pda_park_id_3',
                    'name': 'test_pda_park_name_3',
                    'contacts': 'test_pda_park_contacts_3',
                },
            ],
        ),
        ([{'performer_db_id': 'test_pda_park_id_4'}], []),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_pda_parks.yaml'])
async def test_fetch_pda_parks(orders, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_pda_parks(orders)

    assert result == expected


@pytest.mark.parametrize(
    'rows, expected',
    [
        ([], []),
        ([{'order_id': 'test_order_id_1', 'created_idx': 1581681601}], []),
        ([{'order_id': 'test_order_id_3', 'created_idx': 1578225600}], []),
        (
            [{'order_id': 'test_order_id_1', 'created_idx': 1578225600}],
            [
                {
                    'id': 'test_order_id_1',
                    'performer_clid': 'test_park_id_1',
                    'nearest_zone': 'test_nearest_zone_1',
                    'status': 'test_status_1',
                    'taxi_status': 'test_taxi_status_1',
                    'performer_db_id': 'test_pda_park_id_1',
                    'performer_taxi_alias_id': (
                        'test_performer_taxi_alias_id_1'
                    ),
                    'statistics': 'test_statistics_1',
                    'feedback': 'test_feedback_1',
                    'cost': 1.1,
                    'order_events': 'test_order_events_1',
                    'request_source': 'test_request_source_1',
                    'request_destinations': 'test_request_destinations_1',
                    'payment_tech_type': 'test_payment_tech_type_1',
                    'chat_id': 'chat_id_1',
                },
            ],
        ),
        (
            [
                {'order_id': 'test_order_id_1', 'created_idx': 1578225600},
                {'order_id': 'test_order_id_2', 'created_idx': 1578225700},
                {'order_id': 'test_order_id_3', 'created_idx': 1581681600},
            ],
            [
                {
                    'id': 'test_order_id_1',
                    'performer_clid': 'test_park_id_1',
                    'nearest_zone': 'test_nearest_zone_1',
                    'status': 'test_status_1',
                    'taxi_status': 'test_taxi_status_1',
                    'performer_db_id': 'test_pda_park_id_1',
                    'performer_taxi_alias_id': (
                        'test_performer_taxi_alias_id_1'
                    ),
                    'statistics': 'test_statistics_1',
                    'feedback': 'test_feedback_1',
                    'cost': 1.1,
                    'order_events': 'test_order_events_1',
                    'request_source': 'test_request_source_1',
                    'request_destinations': 'test_request_destinations_1',
                    'payment_tech_type': 'test_payment_tech_type_1',
                    'chat_id': 'chat_id_1',
                },
                {
                    'id': 'test_order_id_2',
                    'performer_clid': 'test_park_id_2',
                    'nearest_zone': 'test_nearest_zone_2',
                    'status': 'test_status_2',
                    'taxi_status': 'test_taxi_status_2',
                    'performer_db_id': 'test_pda_park_id_2',
                    'performer_taxi_alias_id': (
                        'test_performer_taxi_alias_id_2'
                    ),
                    'statistics': 'test_statistics_2',
                    'feedback': 'test_feedback_2',
                    'cost': 2.2,
                    'order_events': 'test_order_events_2',
                    'request_source': 'test_request_source_2',
                    'request_destinations': 'test_request_destinations_2',
                    'payment_tech_type': 'test_payment_tech_type_2',
                    'chat_id': 'chat_id_2',
                },
                {
                    'id': 'test_order_id_3',
                    'performer_clid': 'test_park_id_3',
                    'nearest_zone': 'test_nearest_zone_3',
                    'status': 'test_status_3',
                    'taxi_status': 'test_taxi_status_3',
                    'performer_db_id': 'test_pda_park_id_3',
                    'performer_taxi_alias_id': (
                        'test_performer_taxi_alias_id_3'
                    ),
                    'statistics': 'test_statistics_3',
                    'feedback': 'test_feedback_3',
                    'cost': 3.3,
                    'order_events': 'test_order_events_3',
                    'request_source': 'test_request_source_3',
                    'request_destinations': 'test_request_destinations_3',
                    'payment_tech_type': 'test_payment_tech_type_3',
                    'chat_id': None,
                },
            ],
        ),
    ],
)
@pytest.mark.yt(
    dyn_table_data=[
        'yt_taxi_orders_monthly_2020_01.yaml',
        'yt_taxi_orders_monthly_2020_02.yaml',
    ],
)
async def test_fetch_orders(rows, expected, yt_apply, yt_client, fetcher):
    result = await fetcher._fetch_orders(rows)

    assert result == expected


@pytest.mark.parametrize(
    'chat_ids, expected',
    [
        (
            ['\'chat_id_1\'', '\'chat_id_2\''],
            {
                'chat_id_1': [
                    {
                        'chat_id': 'chat_id_1',
                        'update_id': 'update_1',
                        'data': {
                            'created_date': '2020-01-01T00:00:00.000000Z',
                            'message': {
                                'sender': {'role': 'driver'},
                                'text': 'text 1',
                            },
                        },
                    },
                    {
                        'chat_id': 'chat_id_1',
                        'update_id': 'update_2',
                        'data': {
                            'created_date': '2020-01-01T00:00:01.000000Z',
                            'message': {
                                'sender': {'role': 'client'},
                                'text': 'text 2',
                            },
                        },
                    },
                    {
                        'chat_id': 'chat_id_1',
                        'update_id': 'update_3',
                        'data': {
                            'created_date': '2020-01-01T00:00:02.000000Z',
                            'message': {
                                'sender': {'role': 'driver'},
                                'text': 'text 3',
                            },
                        },
                    },
                ],
                'chat_id_2': [
                    {
                        'chat_id': 'chat_id_2',
                        'update_id': 'update_1',
                        'data': {
                            'created_date': '2020-01-01T00:00:00.000000Z',
                            'message': {
                                'sender': {'role': 'driver'},
                                'text': 'text 1',
                            },
                        },
                    },
                    {
                        'chat_id': 'chat_id_2',
                        'update_id': 'update_2',
                        'data': {
                            'created_date': '2020-01-01T00:00:01.000000Z',
                            'message': {
                                'sender': {'role': 'client'},
                                'text': 'text 2',
                            },
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_taxi_chat_updates.yaml'])
async def test_fetch_chat_updates(
        chat_ids, expected, yt_apply, yt_client, fetcher,
):
    rows = await fetcher._fetch_chat_updates(chat_ids)
    for k in rows:
        rows[k] = sorted(rows[k], key=lambda x: x['update_id'])
    assert rows == expected


@pytest.mark.parametrize(
    'chat_ids, expected',
    [
        (
            ['\'chat_id_1\'', '\'chat_id_2\''],
            {
                'chat_id_2': [
                    {
                        'chat_id': 'chat_id_2',
                        'update_id': 'update_1',
                        'text': 'translation 1',
                    },
                    {
                        'chat_id': 'chat_id_2',
                        'update_id': 'update_2',
                        'text': 'translation 2',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_taxi_chat_translations.yaml'])
async def test_fetch_chat_translations(
        chat_ids, expected, yt_apply, yt_client, fetcher,
):
    rows = await fetcher._fetch_chat_translations(chat_ids)
    for k in rows:
        rows[k] = sorted(rows[k], key=lambda x: x['update_id'])
    assert rows == expected
