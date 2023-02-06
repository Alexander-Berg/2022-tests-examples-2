YANDEX_UID = 'some_yandex_uid'


async def test_status_actually_erased(taxi_grocery_takeout, erased_users):
    erased_users.insert_user(yandex_uid=YANDEX_UID)

    response = await _check_erase(taxi_grocery_takeout, YANDEX_UID)

    assert response == {'status': 'erased'}


async def test_status_not_erased(taxi_grocery_takeout):
    response = await _check_erase(taxi_grocery_takeout, YANDEX_UID)

    assert response == {'status': 'not_erased'}


async def _check_erase(taxi_grocery_takeout, yandex_uid):
    response = await taxi_grocery_takeout.post(
        '/internal/v1/check-erased', json={'yandex_uid': yandex_uid},
    )
    assert response.status_code == 200

    return response.json()
