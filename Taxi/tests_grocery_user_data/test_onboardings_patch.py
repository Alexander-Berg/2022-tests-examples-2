# Проверяем, что статус онбодинга сохраняется
async def test_set_onboarding_status(taxi_grocery_user_data, onboardings_db):
    yandex_uid = 'some_uid'
    onboarding_status = {'type': 'attributes', 'viewed': True}
    response = await taxi_grocery_user_data.patch(
        '/lavka/v1/user-data/v1/onboardings',
        json={'onboardings': [onboarding_status]},
        headers={'X-YaTaxi-Session': 'taxi:123', 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200
    assert response.json()['onboardings'] == [onboarding_status]
    in_db_onboardings = onboardings_db.get_all_onboardings()
    assert in_db_onboardings == [
        {'yandex_uid': yandex_uid, **onboarding_status},
    ]


# Проверяем, что статус онбодинга обновляется в базе
async def test_set_onboarding_status_change(
        taxi_grocery_user_data, onboardings_db,
):
    yandex_uid = 'some_uid'
    onboarding_type = 'attributes'
    onboardings_db.add_onboarding(
        yandex_uid=yandex_uid, onboarding_type=onboarding_type, viewed=False,
    )
    onboarding_status = {'type': onboarding_type, 'viewed': True}
    response = await taxi_grocery_user_data.patch(
        '/lavka/v1/user-data/v1/onboardings',
        json={'onboardings': [onboarding_status]},
        headers={'X-YaTaxi-Session': 'taxi:123', 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200
    assert response.json()['onboardings'] == [onboarding_status]
    in_db_onboardings = onboardings_db.get_all_onboardings()
    assert in_db_onboardings == [
        {'yandex_uid': yandex_uid, **onboarding_status},
    ]


# Проверяем, что возвращается 400, если нет uid-a
async def test_no_uid(taxi_grocery_user_data, onboardings_db):
    onboarding = {'type': 'attributes', 'viewed': True}
    response = await taxi_grocery_user_data.patch(
        '/lavka/v1/user-data/v1/onboardings',
        json={'onboardings': [onboarding]},
        headers={'X-YaTaxi-Session': 'taxi:123'},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }


# Проверяем, что возвращается 401, если пользователь неавторизован
async def test_unauthorized(taxi_grocery_user_data, onboardings_db):
    onboarding = {'type': 'attributes', 'viewed': True}
    response = await taxi_grocery_user_data.patch(
        '/lavka/v1/user-data/v1/onboardings',
        json={'onboardings': [onboarding]},
        headers={},
    )
    assert response.status == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
