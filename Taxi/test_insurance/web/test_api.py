import pytest

DEFAULT_RANG = {
    'newer_than': '2020-01-2T00:00:00',
    'older_than': '2020-01-3T00:00:00',
}


@pytest.mark.servicetest
async def test_ping(taxi_insurance_web):
    response = await taxi_insurance_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


@pytest.mark.parametrize(
    'api_key, insurer_id, data_range, expect_code, expect_redirect',
    [
        pytest.param(
            'test_hash',
            '1',
            DEFAULT_RANG,
            200,
            '/static/mds/1138/0d1e7e8e-fd1f-4f4d-9863-6fcc1ec6eb39',
            id='simple test',
        ),
        pytest.param(
            'incorrect', '1', DEFAULT_RANG, 403, None, id='incorrect api_key',
        ),
        pytest.param(
            'test_hash',
            '666',
            DEFAULT_RANG,
            403,
            None,
            id='incorrect insurer_id',
        ),
        pytest.param(
            'test_hash',
            '1',
            {
                'newer_than': '2000-01-1T00:00:00',
                'older_than': '2000-01-2T00:00:00',
            },
            404,
            None,
            id='data not found',
        ),
    ],
)
async def test_export_orders(
        web_app_client,
        api_key,
        insurer_id,
        data_range,
        expect_code,
        expect_redirect,
):
    response = await web_app_client.post(
        '/export/orders',
        headers={'X-YaTaxi-API-Key': api_key, 'Range': '1-100'},
        json={'insurer_id': insurer_id, 'range': data_range},
    )
    assert response.status == expect_code

    if response.status == 200:
        assert response.headers['X-Accel-Redirect'] == expect_redirect
        assert response.headers['Range'] == '1-100'
