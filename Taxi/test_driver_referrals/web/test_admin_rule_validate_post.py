import pytest


@pytest.mark.parametrize(
    ('response_code', 'new_rule'),
    [
        [400, {}],
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
        ],
        [
            200,
            {
                'start_time': '2019-01-01T07:00:00+07',
                'end_time': '2019-10-01T00:00:00Z',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Text',
            },
        ],
        [
            400,
            {
                'start_time': '2019-01-01T07:00:00+07',
                'end_time': '2019-10-01T00:00:00Z',
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'No tariff zones or agglomerations',
            },
        ],
        [
            200,
            {
                'start_time': '2019-01-01T07:00:00+07',
                'end_time': '2019-10-01T00:00:00Z',
                'tariff_zones': ['moscow', 'kaluga'],
                'currency': 'RUB',
                'referree_days': 21,
                'tariff_classes': ['econom', 'comfort'],
                'budget': 500,
                'description': 'Both tariff zones and agglomerations',
                'agglomerations': ['br_moscow_adm', 'br_saintpetersburg_adm'],
            },
        ],
        [
            200,
            {
                'start_time': '2019-01-01T07:00:00+07',
                'end_time': '2019-10-01T00:00:00Z',
                'currency': 'RUB',
                'referree_days': 21,
                'budget': 500,
                'description': 'Only agglomerations',
                'agglomerations': ['br_moscow_adm', 'br_saintpetersburg_adm'],
            },
        ],
    ],
)
@pytest.mark.now('2018-12-31')
async def test_admin_rule_validate_post(
        web_app_client, response_code, new_rule,
):
    headers = {'X-Yandex-Login': 'author'}

    response = await web_app_client.post(
        '/admin/rule/validate/', json=new_rule, headers=headers,
    )
    response_data = await response.json()
    assert (
        response.status == response_code
    ), f'Incorrect response {response_data}'
