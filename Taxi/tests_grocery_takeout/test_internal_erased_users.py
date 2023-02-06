async def test_list_erased_users(taxi_grocery_takeout, erased_users):
    yandex_uid_1 = 'uid_1'
    yandex_uid_2 = 'uid_2'

    erased_users.insert_user(yandex_uid_1)
    erased_users.insert_user(yandex_uid_2)

    response = await taxi_grocery_takeout.post(
        '/internal/v1/erased-users/list', json={},
    )
    assert response.status_code == 200
    erased_list = response.json()['uids']

    assert len(erased_list) == 2
    assert yandex_uid_1 in erased_list
    assert yandex_uid_2 in erased_list
