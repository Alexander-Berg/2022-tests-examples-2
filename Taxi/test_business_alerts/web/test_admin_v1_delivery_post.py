import pytest

MODIFY_URI = '/admin/v1/delivery'
HEADERS = {'X-Yandex-Login': 'user1', 'Accept-Language': 'ru'}


@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param(
            dict(
                metric='ru_name',
                dimensions=['count'],
                duration='5m',
                grid='1m',
            ),
            200,
            id='base',
        ),
    ],
)
async def test_base(
        taxi_business_alerts_web, tst_request, expected_status, atlas_backend,
):
    response = await taxi_business_alerts_web.post(
        MODIFY_URI, json=tst_request, headers=HEADERS,
    )
    assert response.status == expected_status
    assert await response.json()
