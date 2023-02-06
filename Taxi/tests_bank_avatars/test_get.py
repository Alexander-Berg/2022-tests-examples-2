import pytest

MCC = '1234'
MCC_URL = 'http://mcc_url.com'

MERCHANT_NAME = 'eda'
MERCHANT_NAME_URL = 'eda.com/get-fintech/123'

TYPE = 'topup'
TYPE_URL = 'topup.com/get-topup'

IMAGES_MAPPING = {
    'mcc': {MCC: MCC_URL},
    'merchant_name': {MERCHANT_NAME: MERCHANT_NAME_URL},
    'type': {TYPE: TYPE_URL},
}

GET_IMAGE_HANDLE_URL = '/v1/avatars/v1/get_image'
GET_IMAGES_HANDLE_URL = '/v1/avatars/v1/get_images'


@pytest.mark.config(BANK_AVATARS_IMAGES_MAPPING=IMAGES_MAPPING)
async def test_get_image_one_param(taxi_bank_avatars):
    data = {'merchant_name': MERCHANT_NAME, 'type': TYPE}
    response = await taxi_bank_avatars.post(GET_IMAGE_HANDLE_URL, json=data)

    assert response.status_code == 200
    assert response.json()['image_url'] == MERCHANT_NAME_URL
    assert response.json()['merchant_name'] == MERCHANT_NAME

    data = {'mcc': MCC, 'type': TYPE}
    response = await taxi_bank_avatars.post(GET_IMAGE_HANDLE_URL, json=data)

    assert response.status_code == 200
    assert response.json()['image_url'] == MCC_URL
    assert response.json()['mcc'] == MCC

    data = {'type': TYPE}
    response = await taxi_bank_avatars.post(GET_IMAGE_HANDLE_URL, json=data)

    assert response.status_code == 200
    assert response.json()['image_url'] == TYPE_URL
    assert response.json()['type'] == TYPE


@pytest.mark.config(BANK_AVATARS_IMAGES_MAPPING=IMAGES_MAPPING)
async def test_get_image_multiple_params(
        taxi_bank_avatars, taxi_config, pgsql,
):
    data = {'merchant_name': MERCHANT_NAME, 'mcc': MCC, 'type': TYPE}
    response = await taxi_bank_avatars.post(GET_IMAGE_HANDLE_URL, json=data)

    assert response.status_code == 200
    assert response.json()['image_url'] == MERCHANT_NAME_URL
    assert response.json()['merchant_name'] == MERCHANT_NAME

    data = {'mcc': 'invalid_mcc', 'type': TYPE}

    response = await taxi_bank_avatars.post(GET_IMAGE_HANDLE_URL, json=data)

    assert response.status_code == 200
    assert response.json()['image_url'] == TYPE_URL
    assert response.json()['type'] == TYPE

    data = {'mcc': 'invalid_mcc', 'type': 'withdraw'}

    response = await taxi_bank_avatars.post(GET_IMAGE_HANDLE_URL, json=data)

    assert response.status_code == 404


@pytest.mark.config(BANK_AVATARS_IMAGES_MAPPING=IMAGES_MAPPING)
async def test_get_image_batch(taxi_bank_avatars, taxi_config, pgsql):
    parameters_list = {
        'parameters_array': [
            {'merchant_name': MERCHANT_NAME, 'type': TYPE},
            {'mcc': MCC, 'type': TYPE},
            {'type': TYPE},
            {'type': 'withdraw'},
            {'mcc': 'invalid_mcc', 'type': TYPE},
        ],
    }

    response = await taxi_bank_avatars.post(
        GET_IMAGES_HANDLE_URL, json=parameters_list,
    )

    assert response.status_code == 200
    res_array = response.json()['images']

    assert len(res_array) == 5
    assert res_array[0] == {
        'merchant_name': MERCHANT_NAME,
        'image_url': MERCHANT_NAME_URL,
    }
    assert res_array[1] == {'mcc': MCC, 'image_url': MCC_URL}
    assert res_array[2] == {'type': TYPE, 'image_url': TYPE_URL}
    assert res_array[3] == {}
    assert res_array[4] == {'type': TYPE, 'image_url': TYPE_URL}
