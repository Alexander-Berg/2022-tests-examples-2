from tests_bank_forms import common

SET_KYC_FORM_API = '/v1/forms/v1/set_kyc_form'


async def test_set_kyc_form_work(taxi_bank_forms, pgsql):
    headers = common.default_headers()
    body = common.kyc_body()
    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=body,
    )
    assert response.status_code == 200
    data_base = common.select_kyc_form(pgsql, common.DEFAULT_YANDEX_BUID)

    common.assert_default(data_base)


async def test_set_kyc_form_not_all_fields(taxi_bank_forms, pgsql):
    headers = common.default_headers()
    body = common.kyc_body()
    body['form'].pop('phone')
    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=body,
    )
    assert response.status_code == 200
    data_base = common.select_kyc_form(pgsql, common.DEFAULT_YANDEX_BUID)

    params = common.DefaultKycParams(phone=None)
    common.assert_default(data_base, params)


async def test_set_kyc_form_double(taxi_bank_forms, pgsql):
    headers = common.default_headers()
    body = common.kyc_body()
    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=body,
    )
    assert response.status_code == 200

    other_number = '1234'
    body['form']['phone'] = other_number

    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=body,
    )
    assert response.status_code == 200

    data_base = common.select_kyc_form(pgsql, common.DEFAULT_YANDEX_BUID)

    params = common.DefaultKycParams(phone=other_number)
    common.assert_default(data_base, params)


async def test_set_kyc_form_double_records(taxi_bank_forms, pgsql):
    headers = common.default_headers()
    body = common.kyc_body()
    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=body,
    )
    assert response.status_code == 200

    other_number = '1234'
    body['form']['phone'] = other_number

    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=body,
    )
    assert response.status_code == 200

    assert common.kyc_sum_records(pgsql, common.DEFAULT_YANDEX_BUID) == 2


async def test_set_kyc_form_error(taxi_bank_forms):
    headers = common.default_headers()
    headers['X-Yandex-BUID'] = ''
    response = await taxi_bank_forms.post(
        SET_KYC_FORM_API, headers=headers, json=common.kyc_body(),
    )
    assert response.status_code == 401
