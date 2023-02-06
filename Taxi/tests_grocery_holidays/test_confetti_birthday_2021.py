import pytest


@pytest.mark.parametrize('uid', ['ok_uid', ''])
async def test_get_confetti_status(taxi_grocery_holidays, uid):
    user_headers = {'X-Yandex-UID': uid, 'X-YaTaxi-Session': 'taxi:session'}
    response = await taxi_grocery_holidays.post(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json() == {'is_seen': False}

    response = await taxi_grocery_holidays.put(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers=user_headers,
    )
    assert response.status_code == 200

    response = await taxi_grocery_holidays.post(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json() == {'is_seen': True}

    response = await taxi_grocery_holidays.post(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers={
            'X-Yandex-UID': 'other_uid',
            'X-YaTaxi-Session': 'taxi:other_session',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'is_seen': False}


@pytest.mark.parametrize('previously_seen', [True, False])
async def test_get_confetti_status_previously_unauthorized(
        taxi_grocery_holidays, previously_seen,
):
    uid = 'yandex_uid'
    session = 'taxi:session'
    authorized_user_headers = {
        'X-Yandex-UID': uid,
        'X-YaTaxi-Session': 'taxi:new_session',
        'X-YaTaxi-Bound-Sessions': f'eats:12345,{session}',
    }

    if previously_seen:  # as unauthorized session
        response = await taxi_grocery_holidays.put(
            '/lavka/v1/holidays/v1/birthday-confetti',
            json={},
            headers={'X-YaTaxi-Session': session},
        )
        assert response.status_code == 200

    response = await taxi_grocery_holidays.post(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers=authorized_user_headers,
    )
    assert response.status_code == 200
    assert response.json() == {'is_seen': previously_seen}

    response = await taxi_grocery_holidays.put(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers=authorized_user_headers,
    )
    assert response.status_code == 200

    response = await taxi_grocery_holidays.post(
        '/lavka/v1/holidays/v1/birthday-confetti',
        json={},
        headers=authorized_user_headers,
    )
    assert response.status_code == 200
    assert response.json() == {'is_seen': True}


async def test_set_confeti_duplicate(taxi_grocery_holidays):
    for _ in range(2):
        response = await taxi_grocery_holidays.put(
            '/lavka/v1/holidays/v1/birthday-confetti',
            json={},
            headers={
                'X-Yandex-UID': 'uid',
                'X-YaTaxi-Session': 'taxi:new_session',
                'X-YaTaxi-Bound-Sessions': f'taxis:12345',
            },
        )
        assert response.status_code == 200

    for _ in range(2):
        response = await taxi_grocery_holidays.put(
            '/lavka/v1/holidays/v1/birthday-confetti',
            json={},
            headers={'X-YaTaxi-Session': 'taxi:new_session'},
        )
        assert response.status_code == 200


async def test_get_confetti_no_session(taxi_grocery_holidays):
    response = await taxi_grocery_holidays.post(
        '/lavka/v1/holidays/v1/birthday-confetti', json={},
    )
    assert response.status_code == 401

    response = await taxi_grocery_holidays.put(
        '/lavka/v1/holidays/v1/birthday-confetti', json={},
    )
    assert response.status_code == 401
