async def test_204(taxi_eats_eaters, get_user, format_datetime, create_user):
    eater_id = create_user()
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-last-login',
        json={
            'eater_id': str(eater_id),
            'last_login': '2021-12-31T10:59:59+03:00',
        },
    )

    user = get_user(eater_id)

    assert response.status_code == 204
    assert format_datetime(user['last_login']) == '2021-12-31T10:59:59+03:00'


async def test_404(taxi_eats_eaters):
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-last-login',
        json={'eater_id': '11', 'last_login': '2021-12-31T10:59:59+03:00'},
    )

    assert response.status_code == 404


async def test_400(taxi_eats_eaters):
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-last-login',
        json={'eater_id': '11', 'last_login': None},
    )

    assert response.status_code == 400
