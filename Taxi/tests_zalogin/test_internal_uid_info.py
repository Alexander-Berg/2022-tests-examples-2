# pylint: disable=invalid-name
import pytest


check_all_versions = pytest.mark.parametrize(
    'url',
    [
        pytest.param('v1/internal/uid-info', id='v1'),
        pytest.param('v2/internal/uid-info', id='v2'),
    ],
)


async def request_and_check(taxi_zalogin, url, uid, code=200):
    params = {'yandex_uid': uid}
    response = await taxi_zalogin.get(url, params=params)
    assert response.status_code == code
    return response.json()


@check_all_versions
async def test_errors(taxi_zalogin, url):
    await request_and_check(taxi_zalogin, url, 'not_found', code=409)
    await request_and_check(taxi_zalogin, url, '1113', 500)


@pytest.mark.parametrize(
    'uid, uid_type', [('1111', 'phonish'), ('1114', 'portal')],
)
@check_all_versions
async def test_simple(taxi_zalogin, url, uid, uid_type):
    body = await request_and_check(taxi_zalogin, url, uid=uid)

    assert body['type'] == uid_type
    assert body['yandex_uid'] == uid
    assert 'bound_to' not in body
    assert 'bound_phonishes' not in body


@check_all_versions
async def test_phonish_bound_to(taxi_zalogin, url):
    uid = '1112'
    body = await request_and_check(taxi_zalogin, url, uid=uid)

    assert body['type'] == 'phonish'
    assert body['yandex_uid'] == uid
    assert body['bound_to'] == '1000'
    assert 'bound_phonishes' not in body


@check_all_versions
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_portal_bound_phonishes(taxi_zalogin, url):
    uid = '1115'
    body = await request_and_check(taxi_zalogin, url, uid=uid)

    assert body['type'] == 'portal'
    assert body['yandex_uid'] == uid
    assert 'bound_to' not in body

    if url == 'v1/internal/uid-info':
        bound_phonishes = set(body['bound_phonishes'])
        expected_bound_phonishes = {'1116', '1117', '1118', '1121'}
    elif url == 'v2/internal/uid-info':
        bound_phonishes = {
            (
                item['uid'],
                item['phone_id'],
                item['created'],
                item['last_confirmed'],
            )
            for item in body['bound_phonishes']
        }
        expected_bound_phonishes = {
            (
                '1116',
                '594baaba0000070000040009',
                '2019-02-01T12:20:00+0000',
                '2016-03-10T14:34:31.084+0000',
            ),
            (
                '1117',
                '594baaba0000070000040010',
                '2019-02-01T12:20:00+0000',
                '2017-03-10T14:34:31.084+0000',
            ),
            (
                '1118',
                '594baaba0000070000040011',
                '2019-02-01T12:20:00+0000',
                '2018-03-10T14:34:31.084+0000',
            ),
            (
                '1121',
                '594baaba0000070000040006',
                '2019-02-01T12:20:00+0000',
                '2021-03-10T14:34:31.084+0000',
            ),
        }
    else:
        raise ValueError

    assert bound_phonishes == expected_bound_phonishes, bound_phonishes


async def test_portal_with_no_phones(taxi_zalogin):
    uid = '5500'
    body = await request_and_check(
        taxi_zalogin, 'v1/internal/uid-info', uid=uid,
    )

    assert body['type'] == 'portal'
    assert body['yandex_uid'] == uid
    assert 'bound_to' not in body
    assert body['bound_phonishes'] == ['5501']


async def test_v2_null_fields(taxi_zalogin):
    body = await request_and_check(
        taxi_zalogin, 'v2/internal/uid-info', uid='7777',
    )

    assert body['bound_phonishes'] == [{'uid': '1123'}]
