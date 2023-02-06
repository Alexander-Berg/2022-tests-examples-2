import pytest

import tests_eats_offers.utils as utils


@pytest.mark.now('2019-10-31T11:10:00+00:00')
async def test_user_correctly_deleted(taxi_eats_offers, pgsql):
    request_json = {
        'session_id': 'session_id',
        'parameters': {
            'location': [2, 2],
            'delivery_time': '2019-10-31T12:00:00+00:00',
        },
        'payload': {'extra-data': 'value'},
    }
    user_id = 'some_user'
    response = await taxi_eats_offers.post(
        '/v1/offer/set',
        json=request_json,
        headers=utils.get_headers_with_user_id(user_id),
    )
    assert response.status_code == 200

    cursor = pgsql['eats_offers'].cursor()
    cursor.execute(
        'SELECT user_id FROM eats_offers.users WHERE user_id = %s;',
        (user_id,),
    )
    users = list(cursor)
    assert not users
