import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'query, status, expected',
    [
        (
            {
                'zone': ['moscow', 'spb'],
                'starts_at': '2020-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
            },
            200,
            {
                'rules': [
                    {
                        'fees': [
                            {'fee': '42.0001', 'subscription_level': 'level'},
                        ],
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'kind': 'software_subscription',
                        'matcher': {
                            'ends_at': '2120-01-01T21:00:00+00:00',
                            'starts_at': '2019-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'moscow',
                        },
                    },
                    {
                        'fees': [
                            {'fee': '42.0002', 'subscription_level': 'level'},
                        ],
                        'id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                        'kind': 'software_subscription',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
                            'tag': 'tag',
                        },
                    },
                    {
                        'fees': {'percent': '42.42'},
                        'id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa1f',
                        'kind': 'reposition',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
                            'payment_type': 'card',
                        },
                    },
                ],
            },
        ),
        (
            {
                'zone': ['moscow', 'spb'],
                'starts_at': '2020-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
            },
            200,
            {
                'rules': [
                    {
                        'fees': [
                            {'fee': '42.0001', 'subscription_level': 'level'},
                        ],
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'kind': 'software_subscription',
                        'matcher': {
                            'ends_at': '2120-01-01T21:00:00+00:00',
                            'starts_at': '2019-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'moscow',
                        },
                    },
                    {
                        'fees': [
                            {'fee': '42.0002', 'subscription_level': 'level'},
                        ],
                        'id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                        'kind': 'software_subscription',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
                            'tag': 'tag',
                        },
                    },
                    {
                        'fees': {'percent': '42.42'},
                        'id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa1f',
                        'kind': 'reposition',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
                            'payment_type': 'card',
                        },
                    },
                ],
            },
        ),
        (
            {
                'zone': ['moscow', 'spb'],
                'starts_at': '2031-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
            },
            200,
            {
                'rules': [
                    {
                        'fees': [
                            {'fee': '42.0001', 'subscription_level': 'level'},
                        ],
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'kind': 'software_subscription',
                        'matcher': {
                            'ends_at': '2120-01-01T21:00:00+00:00',
                            'starts_at': '2019-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'moscow',
                        },
                    },
                ],
            },
        ),
        (
            {
                'zone': ['moscow', 'spb'],
                'starts_at': '2020-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
                'limit': 1,
            },
            200,
            {
                'next_cursor': '2abf062a-b607-11ea-998e-07e60204cbcf',
                'rules': [
                    {
                        'fees': [
                            {'fee': '42.0001', 'subscription_level': 'level'},
                        ],
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'kind': 'software_subscription',
                        'matcher': {
                            'ends_at': '2120-01-01T21:00:00+00:00',
                            'starts_at': '2019-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'moscow',
                        },
                    },
                ],
            },
        ),
        (
            {
                'zone': ['ekb'],
                'starts_at': '2020-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
                'limit': 1,
            },
            200,
            {
                'next_cursor': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f',
                'rules': [
                    {
                        'fees': {'percent': '0.13'},
                        'id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f',
                        'kind': 'hiring_kind',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'hiring_type': 'commercial_returned',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'ekb',
                        },
                        'settings': {'hiring_age': 180},
                    },
                ],
            },
        ),
        (
            {
                'zone': ['ekb'],
                'starts_at': '2020-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
                'limit': 1,
                'cursor': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f',
            },
            200,
            {
                'next_cursor': 'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f',
                'rules': [
                    {
                        'fees': {'fee': '0.13'},
                        'id': 'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f',
                        'kind': 'fine_kind',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'fine_code': 'fine!!!',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'comfortplus',
                            'zone': 'ekb',
                        },
                    },
                ],
            },
        ),
        (
            {
                'zone': ['test_unrealized_fee'],
                'starts_at': '2020-01-01T21:00:01+00:00',
                'ends_at': '2050-01-01T21:00:01+00:00',
            },
            200,
            {
                'rules': [
                    {
                        'fees': {'fee': '0.13', 'unrealized_fee': '0.14'},
                        'id': '703bffab-b3d0-426f-9f40-137847d480d2',
                        'kind': 'taximeter',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'comfortplus',
                            'zone': 'test_unrealized_fee',
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2020-01-10T00:00:00Z')
@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v2_rules_select.sql', 'taximeter.sql'],
)
async def test_select(
        taxi_billing_commissions,
        load_json,
        query,
        status,
        expected,
        billing_commissions_postgres_db,
):
    response = await taxi_billing_commissions.post(
        'v2/rules/select', json=query,
    )
    assert response.status_code == status
    assert expected == response.json()


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v2_rules_select.sql', 'taximeter.sql'],
)
@pytest.mark.parametrize(
    'query_args,expected',
    (
        (
            {},
            [
                '5804fd71-c9a7-46c6-bba4-353ab6a2294a',
                '703bffab-b3d0-426e-9f40-137847d480d2',
            ],
        ),
        (
            {'tariff': ['comfortplus']},
            ['703bffab-b3d0-426e-9f40-137847d480d2'],
        ),
        (
            {'tariff': ['comfortplus'], 'include_all_tariff_rules': True},
            [
                '5804fd71-c9a7-46c6-bba4-353ab6a2294a',
                '703bffab-b3d0-426e-9f40-137847d480d2',
            ],
        ),
        (
            {'tariff': [], 'include_all_tariff_rules': True},
            ['5804fd71-c9a7-46c6-bba4-353ab6a2294a'],
        ),
        ({'tariff': ['econom']}, []),
        (
            {'tariff': ['econom'], 'include_all_tariff_rules': True},
            ['5804fd71-c9a7-46c6-bba4-353ab6a2294a'],
        ),
    ),
)
async def test_select_by_tariff(
        taxi_billing_commissions, query_args, expected,
):
    query = dict(
        zone=['test_tariff_filter'],
        starts_at='2020-01-01T21:00:01+00:00',
        ends_at='2050-01-01T21:00:01+00:00',
        **query_args,
    )
    response = await taxi_billing_commissions.post(
        'v2/rules/select', json=query,
    )
    ordered_object.assert_eq(
        [rule['id'] for rule in response.json()['rules']], expected, '',
    )


async def test_forbid_include_all_tariffs_flag_without_tariff(
        taxi_billing_commissions,
):
    query = dict(
        zone=['test_tariff_filter'],
        starts_at='2020-01-01T21:00:01+00:00',
        ends_at='2050-01-01T21:00:01+00:00',
        include_all_tariff_rules=True,
    )
    response = await taxi_billing_commissions.post(
        'v2/rules/select', json=query,
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'INCORRECT_PARAMETERS',
        'message': '"tariff" must be set to use "include_all_tariff_rules"',
    }
