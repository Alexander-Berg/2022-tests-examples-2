import typing

import aiohttp
import pytest

STOCK_OFFER_DATA = {
    'service': 'contractor-marketplace',
    'name': 'priority',
    'payload': {
        'partner': {'name': 'Yandex Pro'},
        'categories': ['other'],
        'title': 'Приоритет +10000',
        'actions': [{'type': 'copy', 'text': 'Приоритет', 'data': '----'}],
        'offer_id': 'priority',
        'place_id': 120,
        'balance_payment': True,
        'meta_info': {},
        'slider': False,
        'sale_offer': {
            'sale_amount': 90,
            'sticker_color': 'yellow',
            'old_price': '100',
        },
        'price': '10',
        'media_id': 'cdbd88bd52ca6f7679a56b9dc770db9262f1e8e7',
    },
    'ticket': '',
    'author': 'lohmat',
    'created': '2022-02-01T12:26:20+0300',
    'updated': '2022-04-05T13:01:20+0300',
    'status': 'published',
    'schedule': {
        'start_at': '2022-02-01T00:00:00+0300',
        'finish_at': '2022-06-29T00:00:00+0300',
    },
    'recipients': {'type': 'country', 'recipients_ids': ['rus']},
}

OFFER_DATA_BY_ID: typing.Dict[str, typing.Any] = {
    'feeds-admin-id-1': {'id': 'feeds-admin-id-1', **STOCK_OFFER_DATA},
    'feeds-admin-id-2': {'id': 'feeds-admin-id-2', **STOCK_OFFER_DATA},
    'feeds-admin-id-3': {'id': 'feeds-admin-id-3', **STOCK_OFFER_DATA},
    'feeds-admin-id-10': {'id': 'feeds-admin-id-10', **STOCK_OFFER_DATA},
    'feeds-admin-id-team_offer': {
        'id': 'feeds-admin-id-team_offer',
        'service': 'contractor-marketplace',
        'name': 'priority',
        'payload': {
            'partner': {'name': 'Yandex Pro'},
            'categories': ['other'],
            'title': 'Приоритет +10000',
            'actions': [{'type': 'copy', 'text': 'Приоритет', 'data': '----'}],
            'offer_id': 'priority',
            'place_id': 120,
            'balance_payment': True,
            'meta_info': {},
            'slider': False,
            'sale_offer': {
                'sale_amount': 90,
                'sticker_color': 'yellow',
                'old_price': '100',
            },
            'price': '10',
            'media_id': 'cdbd88bd52ca6f7679a56b9dc770db9262f1e8e7',
        },
        'ticket': '',
        'author': 'lohmat',
        'created': '2022-02-01T12:26:20+0300',
        'updated': '2022-04-05T13:01:20+0300',
        'status': 'published',
        'schedule': {
            'start_at': '2022-02-01T00:00:00+0300',
            'finish_at': '2022-06-29T00:00:00+0300',
        },
        'recipients': {'type': 'tag', 'recipients_ids': ['marketplace_test']},
    },
    'feeds-admin-id-not_balance': {
        'id': 'feeds-admin-id-not_balance',
        'service': 'contractor-marketplace',
        'name': 'priority',
        'payload': {
            'partner': {'name': 'Yandex Pro'},
            'categories': ['other'],
            'title': 'Приоритет +10000',
            'actions': [{'type': 'copy', 'text': 'Приоритет', 'data': '----'}],
            'offer_id': 'priority',
            'place_id': 120,
            'balance_payment': False,
            'meta_info': {},
            'slider': False,
            'sale_offer': {
                'sale_amount': 90,
                'sticker_color': 'yellow',
                'old_price': '100',
            },
            'price': '10',
            'media_id': 'cdbd88bd52ca6f7679a56b9dc770db9262f1e8e7',
        },
        'ticket': '',
        'author': 'lohmat',
        'created': '2022-02-01T12:26:20+0300',
        'updated': '2022-04-05T13:01:20+0300',
        'status': 'published',
        'schedule': {
            'start_at': '2022-02-01T00:00:00+0300',
            'finish_at': '2022-06-29T00:00:00+0300',
        },
        'recipients': {'type': 'country', 'recipients_ids': ['rus']},
    },
    'feeds_admin_expired': {
        'id': 'feeds_admin_expired',
        'service': 'contractor-marketplace',
        'name': 'priority',
        'payload': {
            'partner': {'name': 'Yandex Pro'},
            'categories': ['other'],
            'title': 'Приоритет +10000',
            'actions': [{'type': 'copy', 'text': 'Приоритет', 'data': '----'}],
            'offer_id': 'priority',
            'place_id': 120,
            'balance_payment': False,
            'meta_info': {},
            'slider': False,
            'sale_offer': {
                'sale_amount': 90,
                'sticker_color': 'yellow',
                'old_price': '100',
            },
            'price': '10',
            'media_id': 'cdbd88bd52ca6f7679a56b9dc770db9262f1e8e7',
        },
        'ticket': '',
        'author': 'lohmat',
        'created': '2022-02-01T12:26:20+0300',
        'updated': '2022-04-05T13:01:20+0300',
        'status': 'published',
        'schedule': {
            'start_at': '2021-02-01T00:00:00+0300',
            'finish_at': '2021-03-10T00:00:00+0300',
        },
        'recipients': {'type': 'country', 'recipients_ids': ['rus']},
    },
    'to_exclude': {
        'id': 'to_exclude',
        'service': 'contractor-marketplace',
        'name': 'priority',
        'payload': {
            'partner': {'name': 'Yandex Pro'},
            'categories': ['other'],
            'title': 'Приоритет +10000',
            'actions': [{'type': 'copy', 'text': 'Приоритет', 'data': '----'}],
            'offer_id': 'priority',
            'place_id': 120,
            'balance_payment': False,
            'meta_info': {
                'priority_params': {
                    'tag_name': 'gold',
                    'duration_minutes': 200,
                },
            },
            'slider': False,
            'sale_offer': {
                'sale_amount': 90,
                'sticker_color': 'yellow',
                'old_price': '100',
            },
            'price': '10',
            'media_id': 'cdbd88bd52ca6f7679a56b9dc770db9262f1e8e7',
        },
        'ticket': '',
        'author': 'lohmat',
        'created': '2022-02-01T12:26:20+0300',
        'updated': '2022-04-05T13:01:20+0300',
        'status': 'published',
        'schedule': {
            'start_at': '2021-02-01T00:00:00+0300',
            'finish_at': '2021-03-10T00:00:00+0300',
        },
        'recipients': {'type': 'country', 'recipients_ids': ['rus']},
    },
}

FEEDS_ADMIN_OFFERS = [
    {
        'id': 'feeds-admin-id-1',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'fedoseeva-ds',
        'slider': False,
        'place_id': 111,
        'name': 'dasha1',
        'partner_name': '11',
        'created': '2022-05-16T17:11:43+0300',
        'updated': '2022-05-16T17:11:43+0300',
        'categories': ['food'],
    },
    {
        'id': 'feeds-admin-id-not_balance',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'nearxjob',
        'slider': False,
        'place_id': 1,
        'name': 'NEARXJOBTEST1',
        'partner_name': 'NEARXJOBTEST1',
        'created': '2022-05-16T12:52:20+0300',
        'updated': '2022-05-16T12:52:20+0300',
        'categories': ['groceries'],
    },
    {
        'id': 'feeds-admin-id-2',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'fedoseeva-ds',
        'slider': False,
        'place_id': 111,
        'name': 'dasha',
        'partner_name': '11',
        'created': '2022-05-16T17:10:22+0300',
        'updated': '2022-05-16T17:11:24+0300',
        'categories': ['food'],
    },
    {
        'id': 'feeds-admin-id-3',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'nearxjob',
        'slider': False,
        'place_id': 1,
        'name': 'NEARXJOBTEST1',
        'partner_name': 'NEARXJOBTEST1',
        'created': '2022-05-16T12:52:20+0300',
        'updated': '2022-05-16T12:52:20+0300',
        'categories': ['groceries'],
    },
    {
        'id': 'feeds-admin-id-team_offer',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'nearxjob',
        'slider': False,
        'place_id': 1,
        'name': 'NEARXJOBTEST1',
        'partner_name': 'NEARXJOBTEST1',
        'created': '2022-05-16T12:52:20+0300',
        'updated': '2022-05-16T12:52:20+0300',
        'categories': ['groceries'],
    },
    {
        'id': 'feeds_admin_expired',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'nearxjob',
        'slider': False,
        'place_id': 1,
        'name': 'NEARXJOBTEST1',
        'partner_name': 'NEARXJOBTEST1',
        'created': '2021-05-16T12:52:20+0300',
        'updated': '2021-05-16T12:55:20+0300',
        'categories': ['groceries'],
    },
    {
        'id': 'to_exclude',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'nearxjob',
        'slider': False,
        'place_id': 1,
        'name': 'NEARXJOBTEST1',
        'partner_name': 'NEARXJOBTEST1',
        'created': '2021-05-16T12:52:20+0300',
        'updated': '2021-05-16T12:55:20+0300',
        'categories': ['groceries'],
    },
    {
        'id': 'feeds-admin-id-10',
        'service': 'contractor-marketplace',
        'status': 'created',
        'author': 'nearxjob',
        'slider': False,
        'place_id': 1,
        'name': 'NEARXJOBTEST1',
        'partner_name': 'NEARXJOBTEST1',
        'created': '2022-05-16T12:52:20+0300',
        'updated': '2022-05-16T12:52:20+0300',
        'categories': ['groceries'],
    },
]

EXPECTED_DATABASE_RESULT = [
    (
        'feeds-admin-id-1',
        2,
        '2021-11-12T16:10:00+03:00',
        '2021-11-22T16:00:00+03:00',
        1,
        20,
    ),
    ('feeds-admin-id-10', 0, None, '2021-11-22T16:00:00+03:00', 0, 20),
    ('feeds-admin-id-2', 2, None, '2021-11-22T16:00:00+03:00', 0, 20),
    (
        'feeds-admin-id-3',
        0,
        '2021-11-12T16:22:00+03:00',
        '2021-11-22T16:00:00+03:00',
        2,
        20,
    ),
]


@pytest.mark.pgsql('contractor_merch', files=['promocodes_left.sql'])
@pytest.mark.now('2021-11-22T13:00:00+00:00')
@pytest.mark.config(
    CONTRACTOR_MERCH_PROMOCODE_CRAWLER_SETTINGS={
        'feeds_admin_chunk_size': 4,
        'sleep_time_sec': 600,
        'num_vouchers_for_estimation': 20,
    },
)
@pytest.mark.parametrize('failed_feeds_admin', [False, True])
async def test_crawler(
        mockserver,
        testpoint,
        taxi_contractor_merch,
        taxi_contractor_merch_monitor,
        pgsql,
        failed_feeds_admin,
):
    @testpoint('promocode-crawler-testpoint')
    def promocode_crawler_testpoint(arg):
        pass

    @mockserver.json_handler('/feeds-admin/v1/contractor-marketplace/list')
    async def _mock_feeds_admin_list(request):
        if not failed_feeds_admin:
            if request.json['offset'] == 0:
                assert request.json == {
                    'service': 'contractor-marketplace',
                    'status': 'published',
                    'offset': 0,
                    'limit': 4,
                    'order_by': 'created',
                }
                return aiohttp.web.json_response(
                    status=200,
                    data={
                        'items': FEEDS_ADMIN_OFFERS[:4],
                        'total': 8,
                        'offset': 0,
                        'limit': 4,
                    },
                )
            assert request.json == {
                'service': 'contractor-marketplace',
                'status': 'published',
                'offset': 4,
                'limit': 4,
                'order_by': 'created',
            }
            return aiohttp.web.json_response(
                status=200,
                data={
                    'items': FEEDS_ADMIN_OFFERS[4:],
                    'total': 8,
                    'offset': 4,
                    'limit': 4,
                },
            )
        return aiohttp.web.json_response(status=500)

    @mockserver.json_handler('/feeds-admin/v1/contractor-marketplace/get')
    async def _mock_feeds_admin_get(request):
        return aiohttp.web.json_response(
            status=200, data=OFFER_DATA_BY_ID[request.args['id']],
        )

    cursor = pgsql['contractor_merch'].cursor()

    async with taxi_contractor_merch.spawn_task('workers/promocode-crawler'):
        result = await promocode_crawler_testpoint.wait_call()
        assert result == {'arg': None}
        cursor.execute(
            """
            SELECT * FROM contractor_merch.promocodes_info;
            """,
        )
        if not failed_feeds_admin:
            assert _mock_feeds_admin_list.times_called == 2
            ans = list(cursor)
            for i, value in enumerate(ans):
                ans[i] = (
                    value[0],
                    value[1],
                    value[2].isoformat() if value[2] else None,
                    value[3].isoformat() if value[3] else None,
                    *ans[i][4:],
                )
            assert ans == EXPECTED_DATABASE_RESULT
        else:
            assert _mock_feeds_admin_list.times_called == 3
            assert list(cursor) == []
