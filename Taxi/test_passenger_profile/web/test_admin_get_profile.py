import pytest


@pytest.mark.parametrize(
    ['brand', 'expected_name', 'expected_rating'],
    [['yataxi', 'Алексей', '4.90'], ['yauber', 'Лёха', '4.10']],
)
async def test_admin_get_profile(
        web_app_client, brand, expected_name, expected_rating,
):
    test_yandex_uid = '10002'
    query = {'yandex_uids': test_yandex_uid, 'brand': brand}
    response = await web_app_client.get('/v1/admin/profile', params=query)
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {
        'profiles': [
            {
                'first_name': expected_name,
                'rating': expected_rating,
                'yandex_uid': test_yandex_uid,
                'brand': brand,
            },
        ],
    }


async def test_admin_get_profile_no_brand(web_app_client):
    test_yandex_uid = '10002'
    query = {'yandex_uids': test_yandex_uid}
    response = await web_app_client.get('/v1/admin/profile', params=query)
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {
        'profiles': [
            {
                'first_name': 'Алексей',
                'rating': '4.90',
                'yandex_uid': test_yandex_uid,
                'brand': 'yataxi',
            },
            {
                'first_name': 'Лёха',
                'rating': '4.10',
                'yandex_uid': test_yandex_uid,
                'brand': 'yauber',
            },
        ],
    }


async def test_admin_get_profile_several_uids(web_app_client):
    test_yandex_uids = ['10002', '1000005']
    query = {'yandex_uids': ','.join(test_yandex_uids), 'brand': 'yataxi'}
    response = await web_app_client.get('/v1/admin/profile', params=query)
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {
        'profiles': [
            {
                'first_name': '',
                'rating': '4.90',
                'yandex_uid': test_yandex_uids[1],
                'brand': 'yataxi',
            },
            {
                'first_name': 'Алексей',
                'rating': '4.90',
                'yandex_uid': test_yandex_uids[0],
                'brand': 'yataxi',
            },
        ],
    }


async def test_admin_get_profile_several_uids_no_brand(web_app_client):
    test_yandex_uids = ['10002', '1000005']
    query = {'yandex_uids': ','.join(test_yandex_uids)}
    response = await web_app_client.get('/v1/admin/profile', params=query)
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {
        'profiles': [
            {
                'first_name': 'Алексей',
                'rating': '4.90',
                'yandex_uid': test_yandex_uids[0],
                'brand': 'yataxi',
            },
            {
                'first_name': 'Лёха',
                'rating': '4.10',
                'yandex_uid': test_yandex_uids[0],
                'brand': 'yauber',
            },
            {
                'first_name': '',
                'rating': '4.90',
                'yandex_uid': test_yandex_uids[1],
                'brand': 'yataxi',
            },
        ],
    }


@pytest.mark.config(PASSENGER_PROFILE_DEFAULT_RATING=4.87)
async def test_admin_get_profile_default(web_app_client):
    # If nothing was found for yandex_iud, return empty array

    test_yandex_uid = '1000003'
    query = {'yandex_uids': test_yandex_uid}
    response = await web_app_client.get('/v1/admin/profile', params=query)
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {'profiles': []}


async def test_empty(web_app_client):
    query = {'yandex_uids': ''}
    response = await web_app_client.get('v1/admin/profile', params=query)
    assert response.status == 200

    response_data = await response.json()
    assert response_data == {'profiles': []}
