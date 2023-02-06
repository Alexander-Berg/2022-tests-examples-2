from tests_bank_forms import common

GET_KYC_FORM_API = '/forms-internal/v1/get_kyc_form'


async def test_get_kyc_form_no_match_user(taxi_bank_forms, pgsql, mockserver):
    headers = common.default_headers()
    response = await taxi_bank_forms.post(GET_KYC_FORM_API, headers=headers)
    assert response.status_code == 200
    assert response.json()['form'] == {'passport_info_changed_by': ''}


async def test_get_kyc_form_work(taxi_bank_forms, pgsql, mockserver):

    common.insert_default_kyc_form(pgsql)

    headers = common.default_headers()
    response = await taxi_bank_forms.post(GET_KYC_FORM_API, headers=headers)
    assert response.status_code == 200
    resp = response.json()['form']

    common.assert_default(resp)


async def test_get_kyc_form_not_match(taxi_bank_forms, pgsql, mockserver):

    params = common.DefaultKycParams(bank_uid='other_buid')
    common.insert_default_kyc_form(pgsql, params)

    headers = common.default_headers()
    response = await taxi_bank_forms.post(GET_KYC_FORM_API, headers=headers)
    assert response.status_code == 200
    assert response.json()['form'] == {'passport_info_changed_by': ''}


async def test_get_kyc_form_not_all_fields(taxi_bank_forms, pgsql, mockserver):

    params = common.DefaultKycParams(phone=None)
    common.insert_default_kyc_form(pgsql, params)

    headers = common.default_headers()
    response = await taxi_bank_forms.post(GET_KYC_FORM_API, headers=headers)
    assert response.status_code == 200
    resp = response.json()['form']

    common.assert_default_without_phone(resp)


async def test_get_kyc_form_work_double(taxi_bank_forms, pgsql, mockserver):
    params = common.DefaultKycParams(phone='other phone number')
    common.insert_default_kyc_form(pgsql, params)

    common.insert_default_kyc_form(pgsql)

    headers = common.default_headers()
    response = await taxi_bank_forms.post(GET_KYC_FORM_API, headers=headers)
    assert response.status_code == 200
    resp = response.json()['form']
    common.assert_default(resp)


async def test_get_kyc_form_error(taxi_bank_forms):
    headers = common.default_headers()
    headers['X-Yandex-BUID'] = ''
    response = await taxi_bank_forms.post(
        GET_KYC_FORM_API, headers=headers, json=common.kyc_body(),
    )
    assert response.status_code == 401
