import pytest


# Проверяем, что возвращаются все статусы просмотра онбординга для юзера
@pytest.mark.parametrize(
    'onboardings',
    [
        pytest.param(
            [{'type': 'attributes', 'viewed': True}], id='user in db',
        ),
        pytest.param([], id='user not in db'),
    ],
)
async def test_get_onboarding_status(
        taxi_grocery_user_data, onboardings_db, onboardings,
):
    yandex_uid = 'some_uid'
    for onboarding in onboardings:
        onboardings_db.add_onboarding(
            yandex_uid=yandex_uid,
            onboarding_type=onboarding['type'],
            viewed=onboarding['viewed'],
        )
    response = await taxi_grocery_user_data.post(
        '/lavka/v1/user-data/v1/onboardings',
        json={},
        headers={'X-YaTaxi-Session': 'taxi:123', 'X-Yandex-UID': yandex_uid},
    )
    assert response.status == 200
    assert response.json()['onboardings'] == onboardings


# Проверяем, что возвращается 400, если нет uid-a
async def test_no_uid(taxi_grocery_user_data):
    response = await taxi_grocery_user_data.post(
        '/lavka/v1/user-data/v1/onboardings',
        json={},
        headers={'X-YaTaxi-Session': 'taxi:123'},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }


# Проверяем, что возвращается 401, если пользователь неавторизован
async def test_unauthorized(taxi_grocery_user_data):
    response = await taxi_grocery_user_data.post(
        '/lavka/v1/user-data/v1/onboardings', json={}, headers={},
    )
    assert response.status == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
