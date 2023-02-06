import pytest

HEADERS = {'Accept-Language': 'ru_RU'}


@pytest.mark.parametrize(
    'token, expected_response',
    [
        [
            'token',
            {
                'model': 'some model',
                'brand': 'some brand',
                'color_id': 'some color',
                'number': 'some number',
                'reg_cert': 'some reg_cert',
                'year': 2018,
            },
        ],
        ['missing token', {}],
    ],
)
async def test_ok(taxi_selfreg, token, expected_response):
    response = await taxi_selfreg.get(
        '/selfreg/v1/car', params={'token': token}, headers=HEADERS,
    )

    if token != 'missing token':
        assert response.status == 200
        content = await response.json()
        assert content == expected_response
    else:
        assert response.status == 401
