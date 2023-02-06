import pytest

from taxi_selfreg.components import car_checker

HEADERS = {'User-Agent': 'Taximeter 9.61 (1234)'}


@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={'enable_fns_selfemployment': True},
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': ['Москва'],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
)
@pytest.mark.parametrize(
    'token, expect_city, expect_phone_pd_id, expect_fns_available',
    [
        ('token_spb', 'Санкт-Петербург', 'some_phone_pd_id_1', False),
        ('token_msk', 'Москва', 'some_phone_pd_id_2', True),
    ],
)
async def test_car_new_ok(
        web_app_client,
        mongo,
        patch,
        token,
        expect_city,
        expect_phone_pd_id,
        expect_fns_available,
):
    @patch('taxi_selfreg.components.car_checker.Component.check')
    async def _check(
            phone_pd_id, app, city_name, brand, model, year, car_number=None,
    ):
        assert phone_pd_id == expect_phone_pd_id
        assert city_name == expect_city
        assert brand == 'Kia'
        assert model == 'Rio'
        assert year == 2018
        assert car_number is None
        return None

    response = await web_app_client.post(
        '/selfreg/v1/car/new',
        params={'token': token},
        headers=HEADERS,
        json={
            'option': 'owncar',
            'model': 'Rio',
            'brand': 'Kia',
            'color_id': 'Красный',
            'number': 'A666FF150',
            'reg_cert': '007712345678',
            'year': 2018,
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'self_employment_fns_available': expect_fns_available}
    selfreg_user = await mongo.selfreg_profiles.find_one({'token': token})
    assert selfreg_user['car_brand'] == 'Kia'
    assert selfreg_user['car_model'] == 'Rio'
    assert selfreg_user['car_color'] == 'Красный'
    assert selfreg_user['car_number'] == 'A666FF150'
    assert selfreg_user['car_reg_cert'] == '007712345678'
    assert selfreg_user['car_year'] == 2018
    assert selfreg_user['car_is_not_allowed'] is False
    assert selfreg_user['chosen_flow'] == 'driver-with-auto'
    assert selfreg_user['rent_option'] == 'owncar'
    assert selfreg_user['registration_step'] == 'car'

    response = await web_app_client.post(
        '/selfreg/v1/car/new',
        params={'token': token},
        headers=HEADERS,
        json={'option': 'rent'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'self_employment_fns_available': expect_fns_available}
    selfreg_user = await mongo.selfreg_profiles.find_one({'token': token})

    for key in {
            'car_brand',
            'car_model',
            'car_color',
            'car_number',
            'car_reg_cert',
            'car_year',
            'car_is_not_allowed',
    }:
        assert selfreg_user.get(key) is None

    assert selfreg_user['chosen_flow'] == 'driver-without-auto'
    assert selfreg_user['rent_option'] == 'rent'
    assert selfreg_user['registration_step'] == 'car'


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'selfreg_onfoot_flow': '9.61'}},
    },
)
@pytest.mark.parametrize(
    'user_agent, expect_error',
    [('Taximeter 9.60 (1234)', True), ('Taximeter 9.61 (1234)', False)],
)
async def test_car_new_failed_car_check(
        web_app_client, mongo, patch, user_agent, expect_error,
):
    @patch('taxi_selfreg.components.car_checker.Component.check')
    async def _check(
            phone_pd_id, app, city_name, brand, model, year, car_number=None,
    ):
        return car_checker.Rejected()

    token = 'token_spb'

    response = await web_app_client.post(
        '/selfreg/v1/car/new',
        params={'token': token},
        headers={'User-Agent': user_agent},
        json={
            'option': 'owncar',
            'model': '2103',
            'brand': 'ВАЗ',
            'color_id': 'Красный',
            'number': 'A666FF150',
            'reg_cert': '007712345678',
            'year': 2000,
        },
    )

    if expect_error:
        assert response.status == 400
        content = await response.json()
        assert content == {'code': '400', 'message': 'failed to check car'}
    else:
        assert response.status == 200
        content = await response.json()
        assert content == {'self_employment_fns_available': False}

    selfreg_user = await mongo.selfreg_profiles.find_one({'token': token})
    if expect_error:
        for key in {
                'car_brand',
                'car_model',
                'car_color',
                'car_number',
                'car_reg_cert',
                'car_year',
                'car_is_not_allowed',
                'chosen_flow',
                'rent_option',
                'registration_step',
        }:
            assert selfreg_user.get(key) is None
    else:
        assert selfreg_user['car_brand'] == 'ВАЗ'
        assert selfreg_user['car_model'] == '2103'
        assert selfreg_user['car_color'] == 'Красный'
        assert selfreg_user['car_number'] == 'A666FF150'
        assert selfreg_user['car_reg_cert'] == '007712345678'
        assert selfreg_user['car_year'] == 2000
        assert selfreg_user['chosen_flow'] == 'driver-with-auto'
        assert selfreg_user['rent_option'] == 'owncar'
        assert selfreg_user['car_is_not_allowed'] is True
        assert selfreg_user['registration_step'] == 'car'


@pytest.mark.parametrize('rent_option', ['rent', 'owncar'])
async def test_car_new_no_city(taxi_selfreg, rent_option):
    token = 'token_no_city'

    response = await taxi_selfreg.post(
        '/selfreg/v1/car/new',
        params={'token': token},
        headers=HEADERS,
        json={
            'option': rent_option,
            'model': '2103',
            'brand': 'ВАЗ',
            'color_id': 'Красный',
            'number': 'A666FF150',
            'reg_cert': '007712345678',
            'year': 2000,
        },
    )

    assert response.status == 400
    content = await response.json()
    assert content == {'code': '400', 'message': 'no city in profile'}


async def test_car_new_no_data(taxi_selfreg):
    token = 'token_spb'

    response = await taxi_selfreg.post(
        '/selfreg/v1/car/new',
        params={'token': token},
        headers=HEADERS,
        json={'option': 'owncar'},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {'code': '400', 'message': 'not enough car data'}
