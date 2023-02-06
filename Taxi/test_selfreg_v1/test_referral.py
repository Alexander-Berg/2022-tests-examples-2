import pytest

HEADERS = {'Accept-Language': 'ru_RU'}


@pytest.mark.config(TAXIMETER_PROMOCODE_PARAMS={'hint': 'HINT0000'})
@pytest.mark.parametrize(
    'token, expected_response',
    [
        ['token1', {'code_hint': 'HINT0000', 'saved_code': 'SWAGCODE'}],
        ['token2', {'code_hint': 'HINT0000'}],
    ],
)
async def test_referral_get(taxi_selfreg, token, expected_response):
    response = await taxi_selfreg.get(
        '/selfreg/v1/referral-code/', params={'token': token}, headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_response


async def test_referral_post(taxi_selfreg, mockserver, mongo):
    token = 'token1'

    @mockserver.json_handler('/driver-referrals/service/check-promocode')
    async def _mock(*args, **kwargs):
        return {'result': 'OK', 'park_id': 'park_id', 'driver_id': 'driver_id'}

    response = await taxi_selfreg.post(
        '/selfreg/v1/referral-code/',
        params={'token': token},
        json={'code': 'COOL666'},
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'result': 'OK', 'code': 'COOL666'}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile['referral_promocode'] == 'COOL666'


async def test_referral_post_bad_code(taxi_selfreg, mockserver, mongo):
    token = 'token2'

    @mockserver.json_handler('/driver-referrals/service/check-promocode')
    async def _mock(*args, **kwargs):
        return mockserver.make_response(
            status=400, json={'result': 'Код не тот'},
        )

    response = await taxi_selfreg.post(
        '/selfreg/v1/referral-code/',
        params={'token': token},
        json={'code': 'COOL666'},
        headers=HEADERS,
    )

    assert response.status == 400
    content = await response.json()
    assert content == {'result': 'Код не тот'}

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile.get('referral_promocode') is None
