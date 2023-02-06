import pytest


YANDEX_UID = '800500'
TOKEN = 'idempotency_key_0'
SERIES_ID = 'series_id_0'


@pytest.mark.parametrize(
    'body',
    [
        pytest.param(
            {
                'series_id': SERIES_ID,
                'token': TOKEN,
                'users_list': [{'yandex_uid': YANDEX_UID}],
            },
            id='missing application_name or brand_anme',
        ),
        pytest.param(
            {
                'series_id': 'bad_series_id',
                'token': TOKEN,
                'users_list': [
                    {'yandex_uid': YANDEX_UID, 'application_name': 'eats'},
                ],
            },
            id='bad series id',
        ),
        pytest.param(
            {
                'series_id': 'series_id_1',
                'token': TOKEN,
                'users_list': [
                    {'yandex_uid': YANDEX_UID, 'application_name': 'eats'},
                ],
            },
            id='series without value',
        ),
        pytest.param(
            {
                'series_id': SERIES_ID,
                'token': TOKEN,
                'users_list': [
                    {'yandex_uid': YANDEX_UID, 'application_name': 'eats'},
                ],
                'expire_at': '2022-03-01T11:00:00+03:00',
            },
            id='bad expire at',
        ),
        pytest.param(
            {
                'series_id': 'series_id_2',
                'token': TOKEN,
                'users_list': [
                    {'yandex_uid': YANDEX_UID, 'application_name': 'eats'},
                ],
                'value': '444.4',
            },
            id='value more than series value',
        ),
        pytest.param(
            {
                'series_id': 'series_id_3',
                'token': TOKEN,
                'users_list': [
                    {'yandex_uid': YANDEX_UID, 'application_name': 'eats'},
                ],
                'value': '100',
            },
            id='finish time less than now',
        ),
    ],
)
@pytest.mark.now('2022-06-24T20:00:00+0300')
async def test_request_validation_failed(taxi_coupons, stq, body):
    """
    This test is intended to check that validators work correctly
    """
    response = await taxi_coupons.post('/internal/bulk-generate', body)
    assert response.status_code == 400
    assert stq.coupons_bulk_generate_and_activate_promocodes.times_called == 0


@pytest.mark.now('2022-06-24T20:00:00+0300')
async def test_happy_path(taxi_coupons, stq):
    body = {
        'series_id': SERIES_ID,
        'token': TOKEN,
        'users_list': [{'yandex_uid': YANDEX_UID, 'application_name': 'eats'}],
    }
    response = await taxi_coupons.post('/internal/bulk-generate', body)
    assert response.status_code == 200
    assert stq.coupons_bulk_generate_and_activate_promocodes.times_called == 1
