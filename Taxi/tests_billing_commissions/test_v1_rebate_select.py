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
                        'fees': {'percent': '42'},
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'matcher': {
                            'starts_at': '2019-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'moscow',
                        },
                    },
                    {
                        'fees': {'percent': '42.0002'},
                        'id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
                        },
                    },
                    {
                        'fees': {'percent': '42.42'},
                        'id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa1f',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
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
                        'fees': {'percent': '42'},
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'matcher': {
                            'starts_at': '2019-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'moscow',
                        },
                    },
                    {
                        'fees': {'percent': '42.0002'},
                        'id': 'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
                        },
                    },
                    {
                        'fees': {'percent': '42.42'},
                        'id': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa1f',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'spb',
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
                        'fees': {'percent': '42'},
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'matcher': {
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
                        'fees': {'percent': '42'},
                        'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                        'matcher': {
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
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'econom',
                            'zone': 'ekb',
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
                'cursor': 'f3a0603d-3f30-4a43-8e30-71d77ebcaa3f',
            },
            200,
            {
                'next_cursor': 'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f',
                'rules': [
                    {
                        'fees': {'percent': '0.13'},
                        'id': 'f3a1603d-3f30-4a43-8e30-71d77ebcaa3f',
                        'matcher': {
                            'ends_at': '2030-01-01T21:00:00+00:00',
                            'starts_at': '2024-01-01T21:00:00+00:00',
                            'tariff': 'comfortplus',
                            'zone': 'ekb',
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
    files=['defaults.sql', 'test_rules_v1_rebate_select.sql'],
)
async def test_select(taxi_billing_commissions, query, status, expected):
    response = await taxi_billing_commissions.post(
        'v1/rebate/select', json=query,
    )
    assert response.status_code == status
    assert expected == response.json()


@pytest.mark.pgsql(
    'billing_commissions',
    files=['defaults.sql', 'test_rules_v1_rebate_select.sql'],
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
        'v1/rebate/select', json=query,
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
        'v1/rebate/select', json=query,
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'INCORRECT_PARAMETERS',
        'message': '"tariff" must be set to use "include_all_tariff_rules"',
    }
