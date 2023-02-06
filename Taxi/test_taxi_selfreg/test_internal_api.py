import pytest


@pytest.mark.parametrize(
    'token,is_token_valid', [('good_token', True), ('test_token_2', False)],
)
async def test_validate_token(taxi_selfreg, token, is_token_valid):
    data = {'token': token}
    response = await taxi_selfreg.post(
        '/validate_token',
        json=data,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['valid'] == is_token_valid


async def test_check_token_ok(taxi_selfreg):
    data = {'token': 'good_token'}
    response = await taxi_selfreg.post(
        '/check_token',
        json=data,
        headers={'Content-Type': 'application/json'},
    )
    response_json = await response.json()
    assert response.status == 200
    assert response_json['selfreg_id'] == '5a7581722016667706734a33'


async def test_check_token_missing(taxi_selfreg):
    data = {'token': 'test_token_missing'}
    response = await taxi_selfreg.post(
        '/check_token',
        json=data,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == 404
    response_json = await response.json()
    assert response_json == {}


async def test_get_profile_ok(taxi_selfreg):
    data = {'selfreg_id': '5a7581722016667706734a33'}
    response = await taxi_selfreg.post(
        '/get_profile',
        json=data,
        headers={'Content-Type': 'application/json'},
    )
    response_json = await response.json()
    assert response.status == 200
    assert response_json['phone_number'] == '89123456789'
    assert response_json['referral_promocode'] == 'abacaba'


@pytest.mark.parametrize(
    'selfreg_id, expect_status, '
    'phone_pd_id, license_pd_id, car_brand, passport_uid',
    [
        (
            '639568215425349876152468',
            200,
            '+79123456789_PD',
            '00АА123456_PD',
            None,
            None,
        ),
        (
            '221328495326451287545348',
            200,
            '+70123456789_PD',
            '01АА123412_PD',
            'Ford',
            '4011223344',
        ),
        ('incorrect_id', 400, None, None, None, None),
        ('375476572865982435758579', 404, None, None, None, None),
    ],
)
async def test_get_profile_v2(
        taxi_selfreg,
        selfreg_id,
        expect_status,
        phone_pd_id,
        license_pd_id,
        car_brand,
        passport_uid,
):
    response = await taxi_selfreg.get(
        '/internal/selfreg/v2/profile', params={'selfreg_id': selfreg_id},
    )
    assert response.status == expect_status
    if expect_status == 200:
        response_json = await response.json()
        assert response_json['phone_pd_id'] == phone_pd_id
        assert response_json['license_pd_id'] == license_pd_id
        assert response_json.get('car_brand') == car_brand
        assert response_json.get('passport_uid') == passport_uid


@pytest.mark.parametrize('license_pd_id_found', (True, False))
async def test_get_profile_v2_no_license_pd_id(
        taxi_selfreg, mock_personal, license_pd_id_found,
):
    mock_personal.set_license_pd_id_found(license_pd_id_found)

    response = await taxi_selfreg.get(
        '/internal/selfreg/v2/profile',
        params={'selfreg_id': '123328495326451287545456'},
    )
    if license_pd_id_found:
        assert response.status == 200
        response_json = await response.json()
        assert response_json['license_pd_id'] == 'personal_01BB123412'
    else:
        assert response.status == 500
    assert mock_personal.store_licenses.has_calls


@pytest.mark.parametrize(
    'selfreg_id, expect_status, registration_parameters',
    [
        ('639568215425349876152468', 200, []),
        (
            '221328495326451287545348',
            200,
            [
                {'name': 'some_other_parameter', 'value': 'some-other-value'},
                {'name': 'some_parameter', 'value': 'some-value'},
            ],
        ),
        ('incorrect_id', 400, None),
        ('375476572865982435758579', 404, None),
    ],
)
async def test_get_profile_v2_registration_parameters(
        taxi_selfreg, selfreg_id, expect_status, registration_parameters,
):
    response = await taxi_selfreg.get(
        '/internal/selfreg/v2/profile', params={'selfreg_id': selfreg_id},
    )
    assert response.status == expect_status
    if expect_status == 200:
        response_json = await response.json()
        assert (
            response_json['registration_parameters'] == registration_parameters
        )


async def test_delete_profile_ok(taxi_selfreg):
    data = {'selfreg_id': '5a75c4a9b9a179baaf70a52f'}
    response = await taxi_selfreg.post(
        '/delete_profile',
        json=data,
        headers={'Content-Type': 'application/json'},
    )
    assert response.status == 200
