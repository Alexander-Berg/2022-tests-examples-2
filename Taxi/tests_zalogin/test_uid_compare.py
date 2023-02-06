async def request_and_check(taxi_zalogin, uid1, uid2, code=200):
    params = {'yandex_uids': '%s,%s' % (uid1, uid2)}
    headers = {'Accept-Language': 'en'}
    response = await taxi_zalogin.get(
        'admin/uid-compare', params=params, headers=headers,
    )
    assert response.status_code == code
    return response.json()


async def test_errors(taxi_zalogin):
    await request_and_check(taxi_zalogin, 'not_found', 'not_found', code=409)
    response = await taxi_zalogin.get(
        'admin/uid-compare',
        params={'yandex_uids': 'only_one_uid'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 400
    response = await taxi_zalogin.get(
        'admin/uid-compare',
        params={'yandex_uids': 'tree,different,uids'},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 400


async def test_simple(taxi_zalogin):
    body = await request_and_check(taxi_zalogin, '1111', '1111')

    assert body['yandex_uid1'] == '1111'
    assert body['yandex_uid2'] == '1111'

    assert body['code'] == 'same_phonish'
    assert body['title'] == 'same_phonish_account_title'
    assert body['description'] == 'same_phonish_account_description'


async def test_same_portal(taxi_zalogin):
    body = await request_and_check(taxi_zalogin, '1114', '1114')
    assert body['title'] == 'same_portal_account_title'
    assert body['description'] == 'same_portal_account_description'
    assert body['code'] == 'same_portal'


async def test_phonishes(taxi_zalogin):
    body = await request_and_check(taxi_zalogin, '1111', '1119')
    assert body['title'] == 'different_phonish_same_phone_id_title'
    assert body['description'] == 'different_phonish_same_phone_id_description'
    assert body['code'] == 'phonishes_with_same_phones'

    body = await request_and_check(taxi_zalogin, '1111', '1112')
    assert body['title'] == 'different_phonish_different_phone_id_title'
    assert (
        body['description']
        == 'different_phonish_different_phone_id_description'
    )
    assert body['code'] == 'phonishes_with_different_phones'


async def test_portals(taxi_zalogin):
    body = await request_and_check(taxi_zalogin, '1114', '1115')
    assert body['title'] == 'different_portal_different_phone_id_title'
    assert (
        body['description']
        == 'different_portal_different_phone_id_description'
    )
    assert body['code'] == 'portals_with_different_phones'

    body = await request_and_check(taxi_zalogin, '1120', '1115')
    assert body['title'] == 'different_portal_same_phone_id_title'
    assert body['description'] == 'different_portal_same_phone_id_description'
    assert body['code'] == 'portals_with_same_phones'


async def test_mixed(taxi_zalogin):
    body = await request_and_check(taxi_zalogin, '1116', '1115')
    assert body['title'] == 'bound_with_different_phones_title'
    assert body['description'] == 'bound_with_different_phones_description'
    assert body['code'] == 'bound_portal_and_phonish_with_different_phones'

    body = await request_and_check(taxi_zalogin, '1121', '1115')
    assert body['title'] == 'bound_with_same_phones_title'
    assert body['description'] == 'bound_with_same_phones_description'
    assert body['code'] == 'bound_portal_and_phonish_with_same_phones'

    body = await request_and_check(taxi_zalogin, '1122', '1115')
    assert body['title'] == 'not_bound_with_same_phones_title'
    assert body['description'] == 'not_bound_with_same_phones_description'
    assert body['code'] == 'not_bound_portal_and_phonish_with_same_phones'

    body = await request_and_check(taxi_zalogin, '1111', '1115')
    assert body['title'] == 'not_bound_with_different_phones_title'
    assert body['description'] == 'not_bound_with_different_phones_description'
    assert body['code'] == 'not_bound_portal_and_phonish_with_different_phones'
