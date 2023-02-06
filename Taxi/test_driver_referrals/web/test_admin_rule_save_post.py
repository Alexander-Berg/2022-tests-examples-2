import datetime

import dateutil.parser
import dateutil.tz
import pytest

TZ_MSK = dateutil.tz.gettz('Europe/Moscow')


@pytest.mark.parametrize(
    ('response_code', 'new_rule', 'taxirate_ticket'),
    [
        [400, {}, None],
        [
            400,
            {
                'start_time': '2019-01-01 20:00:00',
                'end_time': '2019-10-01__',
                'tariff_zones': ['moscow', 'kaluga'],
                'referrer_bonus': 500,
                'currency': 'RUB',
                'referree_days': 21,
                'referree_rides': 50,
            },
            'TAXIRATE-1',
        ],
        [
            400,
            {
                'start_time': '2019-01-01 20:00:00',
                'end_time': '2019-10-01 20:00:00',
                'tariff_zones': ['moscow', 'kaluga'],
                'referrer_bonus': -500,
                'currency': 'RUB',
                'referree_days': 21,
                'referree_rides': 50,
            },
            'TAXIRATE-1',
        ],
        [
            400,
            {
                'start_time': '2019-01-01T00:00:00',
                'end_time': '2019-10-01T00:00:00',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
                'steps': [
                    {
                        'rides': 1,
                        'rewards': [
                            {
                                'type': 'payment',
                                'reason': 'invited_other_park',
                                'amount': 100,
                            },
                            {
                                'type': 'promocode',
                                'reason': 'invited_same_park',
                                'series': 'test_series',
                            },
                            {
                                'type': 'payment',
                                'reason': 'invited_selfemployed',
                                'amount': 100,
                            },
                        ],
                        'child_rewards': [
                            {
                                'type': 'payment',
                                'reason': 'invited_other_park',
                                'amount': 100,
                            },
                        ],
                    },
                ],
            },
            'TAXIRATE-1',
        ],
        [
            200,
            {
                'start_time': '2019-01-01T00:00:00',
                'end_time': '2019-10-01T00:00:00',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
                'steps': [
                    {
                        'rides': 10,
                        'rewards': [
                            {
                                'type': 'payment',
                                'reason': 'invited_other_park',
                                'amount': 100,
                            },
                            {
                                'type': 'promocode',
                                'reason': 'invited_same_park',
                                'series': 'test_series',
                            },
                            {
                                'type': 'payment',
                                'reason': 'invited_selfemployed',
                                'amount': 100,
                            },
                        ],
                        'child_rewards': [
                            {
                                'type': 'payment',
                                'reason': 'invited_other_park',
                                'amount': 100,
                            },
                        ],
                    },
                ],
            },
            'TAXIRATE-1',
        ],
        [
            200,
            {
                'start_time': '2019-01-01T00:00:00',
                'end_time': '2019-10-01T00:00:00',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
                'steps': [
                    {
                        'rides': 1,
                        'rewards': [
                            {
                                'type': 'payment',
                                'reason': 'invited_other_park',
                                'amount': 100,
                            },
                            {
                                'type': 'promocode',
                                'reason': 'invited_same_park',
                                'series': 'test_series',
                            },
                            {
                                'type': 'payment',
                                'reason': 'invited_selfemployed',
                                'amount': 100,
                            },
                        ],
                        'child_rewards': [],
                    },
                    {
                        'rides': 2,
                        'rewards': [
                            {
                                'type': 'promocode',
                                'reason': 'invited_same_park',
                                'series': 'test_series',
                            },
                        ],
                        'child_rewards': [
                            {
                                'type': 'promocode',
                                'reason': 'invited_other_park',
                                'series': 'test_series_2',
                            },
                        ],
                    },
                ],
            },
            'TAXIRATE-1',
        ],
        [
            200,
            {
                'start_time': '2019-01-01T00:00:00',
                'end_time': '2019-10-01T00:00:00',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
            },
            'TAXIRATE-1',
        ],
        [
            400,
            {
                'start_time': '2019-01-02T03:00:00+03',
                'end_time': '2019-10-02T00:00:00Z',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
                # 'steps': [],
            },
            'TAXIRATE-A',
        ],
        [
            200,
            {
                'start_time': '2019-01-01T00:00:00',
                'end_time': '2019-10-01T00:00:00',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
                'agglomerations': ['br_moscow_adm', 'br_saintpetersburg_adm'],
            },
            'TAXIRATE-1',
        ],
    ],
)
@pytest.mark.now('2018-12-31')
async def test_admin_rule_save_post(
        web_app_client,
        web_context,
        response_mock,
        patch_aiohttp_session,
        response_code,
        new_rule: dict,
        taxirate_ticket,
):
    @patch_aiohttp_session('http://startrack/')
    def _patch_taxirate(method, url, **kwargs):
        return response_mock(status=400, json={})

    headers = {'X-Yandex-Login': 'author'}
    if taxirate_ticket:
        headers['X-YaTaxi-Ticket'] = taxirate_ticket

    response = await web_app_client.post(
        '/admin/rule/save/', json=new_rule, headers=headers,
    )
    response_data = await response.json()
    assert (
        response.status == response_code
    ), f'Incorrect response {response_data}'

    if response_code == 200:
        rule_id = response_data['text']

        async with web_context.pg.master_pool.acquire() as conn:
            rows = await conn.fetch(
                'SELECT * FROM rules WHERE id = $1', rule_id,
            )

        assert len(rows) == 1
        db_rule = rows[0]
        for field_name in ('start_time', 'end_time'):
            assert (
                db_rule[field_name]
                == dateutil.parser.parse(new_rule[field_name])
                .replace(tzinfo=datetime.timezone.utc)
                .astimezone(TZ_MSK)
                .replace(tzinfo=None)
            )
        assert db_rule['taxirate_ticket'] == taxirate_ticket
        assert db_rule['author'] == 'author'
        for field_name in (
                'tariff_zones',
                'currency',
                'referrer_bonus',
                'referree_days',
                'referree_rides',
                'tariff_classes',
                'budget',
                'description',
                'orders_provider',
                'referrer_orders_providers',
                'tag',
                'agglomerations',
        ):
            assert db_rule[field_name] == new_rule.get(field_name)
