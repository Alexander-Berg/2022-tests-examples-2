import pytest

from test_rida import helpers


_DRIVER_GUID = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'
_OFFER_GUID = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'


@pytest.mark.translations(
    rida={
        'errors.validation.fraud.default.title': {'en': 'Bad boys'},
        'errors.validation.fraud.default.body': {'en': 'bad boys'},
        'errors.validation.fraud.default.button': {'en': 'whatcha gonna do'},
    },
)
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.now('2025-04-29T12:12:00.000+0000')
@pytest.mark.config(
    RIDA_SUSPICIOUS_DRIVERS={'drivers': [{'guid': _DRIVER_GUID}]},
)
async def test_driver_bid_place_restriction(taxi_rida_web, stq, mongodb):
    headers = helpers.get_auth_headers(user_id=5678)
    response = await taxi_rida_web.post(
        '/v3/driver/bid/place',
        headers=headers,
        json={
            'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            'offer_guid': _OFFER_GUID,
            'proposed_price': 500,
        },
    )
    assert response.status == 418
    body = await response.json()
    assert body == {
        'title': 'Bad boys',
        'body': 'bad boys',
        'button': 'whatcha gonna do',
        'type': 1,
        'data': {},
    }
