import pytest


HEADERS = {
    'X-Yandex-Uid': '75170007',
    'User-Agent': 'Opera/9.99 (Windows NT 0.0; EN)',
}


@pytest.mark.parametrize(
    'headers', [None, HEADERS],  # headers are optional for now
)
@pytest.mark.parametrize(
    'data, expected_code',
    [({'series_id': 'notexist'}, 404), ({'series_id': 'basic'}, 200)],
)
async def test_admin_promocodes_usages(
        taxi_coupons, headers, data, expected_code,
):
    response = await taxi_coupons.post(
        '/admin/promocodes/usages/', json=data, headers=headers,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        assert response.json() == []
