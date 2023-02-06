import pytest


@pytest.mark.parametrize(
    'query_params, expected',
    [
        (
            {'1id': 123, '2type': 'first', 'x2type': 'second_second'},
            {'1id': 123, '2is_first': True, 'x2is_first': False},
        ),
        (
            {'1id': 321, '2type': 'second', 'x2type': 'first_first'},
            {'1id': 321, '2is_first': False, 'x2is_first': True},
        ),
    ],
)
async def test_numeric(taxi_userver_sample, query_params, expected):
    response = await taxi_userver_sample.get(
        'autogen/numeric', params=query_params,
    )

    assert response.status_code == 200
    assert response.json() == expected
