# pylint: disable=C5521
import pytest


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
async def test_offer_state(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/offer_state', json={'offer_id': 'offer-4q2VolejNlejNmGQ'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_valid': False,
        'session': {
            'is_active': True,
            'is_completed': False,
            'mode': 'home',
            'point': [3.0, 4.0],
        },
    }


@pytest.mark.now('2018-10-12T19:04:45+0300')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'inactive_session.sql',
    ],
)
async def test_offer_state_inactive(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/offer_state', json={'offer_id': 'offer-4q2VolejNlejNmGQ'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'expires_at': '2018-11-26T13:00:00+00:00',
        'is_valid': True,
        'session': {
            'is_active': False,
            'is_completed': False,
            'mode': 'home',
            'point': [3.0, 4.0],
            'end_ts': '2018-10-11T19:01:11.540859+00:00',
        },
    }


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
@pytest.mark.now('2018-10-12T19:04:45+0300')
async def test_offer_no_state(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/offer_state', json={'offer_id': 'offer-O3GWpmbkNEazJn4K'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'expires_at': '2018-11-26T13:00:00+00:00',
        'is_valid': True,
    }


async def test_offer_no_offer(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/offer_state', json={'offer_id': 'offer-O3GWpmbkNEazJn4K'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'OFFER_NOT_FOUND',
        'message': 'Offer not found',
    }
