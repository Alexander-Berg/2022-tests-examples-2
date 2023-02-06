import datetime

import aiohttp
import pytest

ONLY_REQUIRED_FIELDS = {
    'field_28': '{"question": {"type": {"admin_preview": "input"}, "slug": "desired_button_name"}, "value": null}',  # noqa: E501
    'field_4': '{"question": {"type": {"admin_preview": "input"}, "slug": "company_cio"}, "value": null}',  # noqa: E501
    'field_12': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_1_phone"}, "value": "+7 9011111111"}',  # noqa: E501
    'field_11': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_1_email"}, "value": "example@yandex.ru"}',  # noqa: E501
    'field_20': '{"question": {"type": {"admin_preview": "list"}, "slug": "signer_gender"}, "value": "\\u041c\\u0443\\u0436\\u0441\\u043a\\u043e\\u0439"}',  # noqa: E501
    'field_27': '{"question": {"type": {"admin_preview": "input"}, "slug": "st_link"}, "value": null}',  # noqa: E501
    'field_3': '{"question": {"type": {"admin_preview": "input"}, "slug": "company_tin"}, "value": "1503009020"}',  # noqa: E501
    'field_9': '{"question": {"type": {"admin_preview": "input"}, "slug": "mailing_address"}, "value": "4;Алматы"}',  # noqa: E501
    'field_17': '{"question": {"type": {"admin_preview": "input"}, "slug": "bank_bic"}, "value": "11"}',  # noqa: E501
    'field_23': '{"question": {"type": {"admin_preview": "file"}, "slug": "attachments"}, "value": null}',  # noqa: E501
    'field_21': '{"question": {"type": {"admin_preview": "list"}, "slug": "signer_duly_authorized"}, "value": "\\u0423\\u0441\\u0442\\u0430\\u0432\\u0430"}',  # noqa: E501
    'field_7': '{"question": {"type": {"admin_preview": "list"}, "slug": "contract_type"}, "value": "\\u041f\\u0440\\u0435\\u0434\\u043e\\u043f\\u043b\\u0430\\u0442\\u043d\\u044b\\u0439"}',  # noqa: E501
    'field_10': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_1_name"}, "value": "r1_name"}',  # noqa: E501
    'field_1': '{"question": {"type": {"admin_preview": "list"}, "slug": "manager_login"}, "value": "\\u0427\\u0438\\u0441\\u0442\\u044f\\u043a\\u043e\\u0432 \\u0418\\u043b\\u044c\\u044f (ilchistyakov)"}',  # noqa: E501
    'field_26': '{"question": {"type": {"admin_preview": "input"}, "slug": "power_of_attorney_limit"}, "value": null}',  # noqa: E501
    'field_6': '{"question": {"type": {"admin_preview": "input"}, "slug": "enterprise_name_full"}, "value": "2"}',  # noqa: E501
    'field_8': '{"question": {"type": {"admin_preview": "input"}, "slug": "legal_address"}, "value": "3;Алматы"}',  # noqa: E501
    'field_19': '{"question": {"type": {"admin_preview": "input"}, "slug": "signer_name"}, "value": "13"}',  # noqa: E501
    'field_30': '{"question": {"type": {"admin_preview": "input"}, "slug": "signer_position"}, "value": "signer pos"}',  # noqa: E501
    'field_5': '{"question": {"type": {"admin_preview": "input"}, "slug": "enterprise_name_short"}, "value": "1"}',  # noqa: E501
    'field_18': '{"question": {"type": {"admin_preview": "input"}, "slug": "bank_account_number"}, "value": "12"}',  # noqa: E501
    'field_15': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_2_email"}, "value": null}',  # noqa: E501
    'field_29': '{"question": {"type": {"admin_preview": "textarea"}, "slug": "additional_information"}, "value": null}',  # noqa: E501
    'field_14': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_2_name"}, "value": null}',  # noqa: E501
    'field_16': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_2_phone"}, "value": null}',  # noqa: E501
    'field_31': '{"question": {"type": {"admin_preview": "input"}, "slug": "service"}, "value": "Такси"}',  # noqa: E501
    'field_32': '{"question": {"type": {"admin_preview": "input"}, "slug": "country"}, "value": "kaz"}',  # noqa: E501
    'field_33': '{"question": {"type": {"admin_preview": "input"}, "slug": "kbe"}, "value": "2"}',  # noqa: E501
    'field_35': '{"question": {"type": {"admin_preview": "input"}, "slug": "city"}, "value": "Алматы, Алматинская область, Казахстан"}',  # noqa: E501
    'noop': 'content',
}


@pytest.mark.parametrize(
    'fields, files, expected_doc',
    [
        pytest.param(
            ONLY_REQUIRED_FIELDS,
            {},
            {
                'bank_account_number': '12',
                'bank_bic': '11',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'example_email_pd_id',
                        'name': 'r1_name',
                        'phone_id': 'phone_pd_id_1',
                    },
                ],
                'contract_type': 'prepaid',
                'enterprise_name_full': '2',
                'enterprise_name_short': '1',
                'legal_address': '3;Алматы',
                'mailing_address': '4;Алматы',
                'manager_login': 'ilchistyakov',
                'signer_duly_authorized': 'charter',
                'signer_gender': 'male',
                'signer_name': '13',
                'signer_position': 'signer pos',
                'status': 'pending',
                'country': 'kaz',
                'kbe': '2',
                'city': 'Алматы',
                'service': 'taxi',
            },
            id='fill_min_fields',
        ),
        pytest.param(
            {
                **ONLY_REQUIRED_FIELDS,
                **{
                    'field_31': '{"question": {"type": {"admin_preview": "input"}, "slug": "service"}, "value": "Логистика"}',  # noqa: E501
                },
            },
            {},
            {
                'bank_account_number': '12',
                'bank_bic': '11',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'example_email_pd_id',
                        'name': 'r1_name',
                        'phone_id': 'phone_pd_id_1',
                    },
                ],
                'contract_type': 'prepaid',
                'enterprise_name_full': '2',
                'enterprise_name_short': '1',
                'legal_address': '3;Алматы',
                'mailing_address': '4;Алматы',
                'manager_login': 'ilchistyakov',
                'signer_duly_authorized': 'charter',
                'signer_gender': 'male',
                'signer_name': '13',
                'signer_position': 'signer pos',
                'status': 'pending',
                'country': 'kaz',
                'kbe': '2',
                'city': 'Алматы',
                'service': 'cargo',
            },
            id='service_cargo',
        ),
        pytest.param(
            {
                **ONLY_REQUIRED_FIELDS,
                **{
                    'field_31': '{"question": {"type": {"admin_preview": "input"}, "slug": "service"}, "value": "Единый договор"}',  # noqa: E501
                },
            },
            {},
            {
                'bank_account_number': '12',
                'bank_bic': '11',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'example_email_pd_id',
                        'name': 'r1_name',
                        'phone_id': 'phone_pd_id_1',
                    },
                ],
                'contract_type': 'prepaid',
                'enterprise_name_full': '2',
                'enterprise_name_short': '1',
                'legal_address': '3;Алматы',
                'mailing_address': '4;Алматы',
                'manager_login': 'ilchistyakov',
                'signer_duly_authorized': 'charter',
                'signer_gender': 'male',
                'signer_name': '13',
                'signer_position': 'signer pos',
                'status': 'pending',
                'country': 'kaz',
                'kbe': '2',
                'city': 'Алматы',
                'service': 'multi',
            },
            id='fill_min_fields',
        ),
        pytest.param(
            {
                'field_28': '{"question": {"type": {"admin_preview": "input"}, "slug": "desired_button_name"}, "value": "19"}',  # noqa: E501
                'field_4': '{"question": {"type": {"admin_preview": "input"}, "slug": "company_cio"}, "value": "2"}',  # noqa: E501
                'field_12': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_1_phone"}, "value": "+7 9011111111"}',  # noqa: E501
                'field_11': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_1_email"}, "value": "example@yandex.ru"}',  # noqa: E501
                'field_20': '{"question": {"type": {"admin_preview": "list"}, "slug": "signer_gender"}, "value": "\\u041c\\u0443\\u0436\\u0441\\u043a\\u043e\\u0439"}',  # noqa: E501
                'field_27': '{"question": {"type": {"admin_preview": "input"}, "slug": "st_link"}, "value": "18"}',  # noqa: E501
                'field_3': '{"question": {"type": {"admin_preview": "input"}, "slug": "company_tin"}, "value": "1503009020"}',  # noqa: E501
                'field_9': '{"question": {"type": {"admin_preview": "input"}, "slug": "mailing_address"}, "value": "6;Алматы"}',  # noqa: E501
                'field_17': '{"question": {"type": {"admin_preview": "input"}, "slug": "bank_bic"}, "value": "13"}',  # noqa: E501
                'field_21': '{"question": {"type": {"admin_preview": "list"}, "slug": "signer_duly_authorized"}, "value": "\\u0414\\u043e\\u0433\\u043e\\u0432\\u043e\\u0440\\u0430 \\u043f\\u0435\\u0440\\u0435\\u0434\\u0430\\u0447\\u0438 \\u043f\\u043e\\u043b\\u043d\\u043e\\u043c\\u043e\\u0447\\u0438\\u0439"}',  # noqa: E501
                'field_7': '{"question": {"type": {"admin_preview": "list"}, "slug": "contract_type"}, "value": "\\u041f\\u0440\\u0435\\u0434\\u043e\\u043f\\u043b\\u0430\\u0442\\u043d\\u044b\\u0439"}',  # noqa: E501
                'field_10': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_1_name"}, "value": "r1_name"}',  # noqa: E501
                'field_1': '{"question": {"type": {"admin_preview": "list"}, "slug": "manager_login"}, "value": "\\u0427\\u0438\\u0441\\u0442\\u044f\\u043a\\u043e\\u0432 \\u0418\\u043b\\u044c\\u044f (ilchistyakov)"}',  # noqa: E501
                'field_26': '{"question": {"type": {"admin_preview": "input"}, "slug": "power_of_attorney_limit"}, "value": "17"}',  # noqa: E501
                'field_6': '{"question": {"type": {"admin_preview": "input"}, "slug": "enterprise_name_full"}, "value": "4"}',  # noqa: E501
                'field_8': '{"question": {"type": {"admin_preview": "input"}, "slug": "legal_address"}, "value": "5;Алматы"}',  # noqa: E501
                'field_19': '{"question": {"type": {"admin_preview": "input"}, "slug": "signer_name"}, "value": "15"}',  # noqa: E501
                'field_30': '{"question": {"type": {"admin_preview": "input"}, "slug": "signer_position"}, "value": "signer pos"}',  # noqa: E501
                'field_5': '{"question": {"type": {"admin_preview": "input"}, "slug": "enterprise_name_short"}, "value": "3"}',  # noqa: E501
                'field_18': '{"question": {"type": {"admin_preview": "input"}, "slug": "bank_account_number"}, "value": "14"}',  # noqa: E501
                'field_32': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_2_name"}, "value": "r2_name"}',  # noqa: E501
                'field_15': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_2_email"}, "value": "qwerty@gmail.com"}',  # noqa: E501
                'field_29': '{"question": {"type": {"admin_preview": "textarea"}, "slug": "additional_information"}, "value": "20"}',  # noqa: E501
                'field_16': '{"question": {"type": {"admin_preview": "input"}, "slug": "contact_2_phone"}, "value": "+7 9263452243"}',  # noqa: E501
                'field_31': '{"question": {"type": {"admin_preview": "input"}, "slug": "service"}, "value": "Логистика"}',  # noqa: E501
                'noop': 'content',
            },
            {
                'field_32': dict(
                    filename='1.jpg',
                    file=b'JPG',
                    content_type='image/jpeg',
                    headers={
                        'Content-Disposition': (
                            'form-data; name="field_30"; filename="1.jpg"'
                        ),  # noqa: E501
                        'Content-Type': 'image/jpeg',
                        'X-META-INFO': '{\\"question\\": {\\"id\\": 18851, \\"label\\": {\\"ru\\": \\"\\\\u0421\\\\u043a\\\\u0430\\\\u043d \\\\u0434\\\\u043e\\\\u0432\\\\u0435\\\\u0440\\\\u0435\\\\u043d\\\\u043d\\\\u043e\\\\u0441\\\\u0442\\\\u0438 \\\\u043d\\\\u0430 \\\\u043f\\\\u043e\\\\u0434\\\\u043f\\\\u0438\\\\u0441\\\\u0430\\\\u043d\\\\u0442\\\\u0430\\"}}, \\"frontend_url\\": \\"https://forms.test.yandex-team.ru/files?path=%2F430%2F861adf4eae29ed7a847f8cf0cc4f0363_1.jpg\\"}',  # noqa: E501
                    },
                ),
                'field_33': dict(
                    filename='2.jpg',
                    file=b'JPG',
                    content_type='image/jpeg',
                    headers={
                        'Content-Disposition': (
                            'form-data; name="field_31"; filename="2.jpg"'
                        ),  # noqa: E501
                        'Content-Type': 'image/jpeg',
                        'X-META-INFO': '{\\"question\\": {\\"id\\": 18852, \\"label\\": {\\"ru\\": \\"\\\\u0421\\\\u043a\\\\u0430\\\\u043d \\\\u0434\\\\u043e\\\\u0433\\\\u043e\\\\u0432\\\\u043e\\\\u0440\\\\u0430 \\\\u043f\\\\u0435\\\\u0440\\\\u0435\\\\u0434\\\\u0430\\\\u0447\\\\u0438 \\\\u043f\\\\u043e\\\\u043b\\\\u043d\\\\u043e\\\\u043c\\\\u043e\\\\u0447\\\\u0438\\\\u0439\\"}}, \\"frontend_url\\": \\"https://forms.test.yandex-team.ru/files?path=%2F430%2Fd7b063cae1ec83e215d21c978884c012_2.jpg\\"}',  # noqa: E501
                    },
                ),
            },
            {
                'additional_information': '20',
                'bank_account_number': '14',
                'bank_bic': '13',
                'company_cio': '2',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'example_email_pd_id',
                        'name': 'r1_name',
                        'phone_id': 'phone_pd_id_1',
                    },
                    {
                        'email_id': 'random_id',
                        'name': 'r2_name',
                        'phone_id': 'phone_pd_id2',
                    },
                ],
                'contract_type': 'prepaid',
                'desired_button_name': '19',
                'enterprise_name_full': '4',
                'enterprise_name_short': '3',
                'legal_address': '5;Алматы',
                'mailing_address': '6;Алматы',
                'manager_login': 'ilchistyakov',
                'power_of_attorney_limit': '17',
                'attachments': [
                    {'file_key': 'key', 'filename': '1.jpg'},
                    {'file_key': 'key', 'filename': '2.jpg'},
                ],
                'service': 'cargo',
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': '15',
                'signer_position': 'signer pos',
                'st_link': '18',
                'status': 'pending',
            },
            id='fill_all_fields',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_create(
        taxi_corp_requests_web,
        mock_personal,
        mock_mds,
        db,
        fields,
        files,
        expected_doc,
):
    with aiohttp.MultipartWriter('form-data') as mpwriter:
        for key, value in fields.items():
            payload = aiohttp.payload.StringPayload(value)
            payload.set_content_disposition('form-data', name=key)
            mpwriter.append_payload(payload)

        for key, value in files.items():
            payload = aiohttp.payload.BytesPayload(
                value['file'],
                content_type=value['content_type'],
                headers=value['headers'],
            )
            payload.set_content_disposition(
                'form-data', name=key, filename=value['filename'],
            )
            mpwriter.append_payload(payload)

    response = await taxi_corp_requests_web.post(
        '/v1/manager-requests', data=mpwriter,
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    doc = await db.corp_manager_requests.find_one(
        {'_id': response_json['id']},
        projection={'_id': 0, 'created': 0, 'updated': 0},
    )
    assert doc == expected_doc


@pytest.mark.parametrize(
    ['request_id', 'expected_response', 'status_code'],
    [
        (
            'request_accepted',
            {
                'activation_email_sent': True,
                'additional_information': 'r1_additional_information',
                'attachments': [
                    {
                        'filename': 'r1_filename1',
                        'url': '$mockserver/mds/get-taxi/r1_file_key1',
                    },
                    {
                        'filename': 'r1_filename2',
                        'url': '$mockserver/mds/get-taxi/r1_file_key2',
                    },
                ],
                'bank_account_number': 'r1_bank_account_number',
                'bank_bic': 'r1_bank_bic',
                'client_id': 'r1_client_id',
                'client_login': 'small_yandex_login',
                'client_tmp_password': 'some_aes_string',
                'company_cio': 'r1_company_cio',
                'company_tin': '500100732259',
                'contacts': [
                    {
                        'email': 'example@yandex.ru',
                        'name': 'r1_name',
                        'phone': '+79011111111',
                    },
                ],
                'contract_type': 'postpaid',
                'created': '2000-01-01T03:00:00+03:00',
                'desired_button_name': 'r1_desired_button_name',
                'enterprise_name_full': 'r1_enterprise_name_full',
                'enterprise_name_short': 'r1_enterprise_name_short',
                'final_status_date': '2000-01-01T03:00:00+03:00',
                'final_status_manager_login': 'r1_final_status_manager_login',
                'id': 'request_accepted',
                'last_error': 'error',
                'error_reason': 'some error reason',
                'legal_address': '7;r1_legal_address',
                'mailing_address': '7;r1_mailing_address',
                'manager_login': 'r1_manager_login',
                'power_of_attorney_limit': '100',
                'readonly_fields': [
                    'id',
                    'status',
                    'created',
                    'readonly_fields',
                    'manager_login',
                    'signer_duly_authorized',
                    'attachments',
                    'final_status_date',
                    'final_status_manager_login',
                    'client_id',
                    'client_login',
                    'client_tmp_password',
                    'billing_external_id',
                    'last_error',
                    'country',
                    'activation_email_sent',
                ],
                'reason': 'r1_reason',
                'service': 'taxi',
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': 'r1_signer_name',
                'signer_position': 'r1_signer_position',
                'st_link': 'r1_st_link',
                'status': 'accepted',
                'updated': '2000-01-01T03:00:00+03:00',
                'billing_client_id': 73170692,
            },
            200,
        ),
        (
            'non_exist_id',
            {
                'message': 'manager request not found',
                'code': 'request-not-found',
                'details': {},
            },
            404,
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_get_one(
        taxi_corp_requests_web,
        mock_personal,
        request_id,
        expected_response,
        status_code,
):
    response = await taxi_corp_requests_web.get(
        '/v1/manager-requests', params={'request_id': request_id},
    )
    response_json = await response.json()

    assert response.status == status_code, response_json

    if status_code == 200:
        assert set(response_json.pop('readonly_fields')) == set(
            expected_response.pop('readonly_fields'),
        )

    assert response_json == expected_response


@pytest.mark.parametrize(
    ['request_id', 'request_params', 'expected_result'],
    [
        (
            'request_accepted',
            {
                'id': 'ignored',
                'service': 'taxi',
                'manager_login': 'ignored',
                'enterprise_name_full': 'r1_enterprise_name_full',
                'company_cio': 'r1_company_cio',
                'bank_account_number': 'r1_bank_account_number',
                'contract_type': 'postpaid',
                'enterprise_name_short': 'r1_enterprise_name_short',
                'legal_address': '7;r1_legal_address',
                'mailing_address': '7;r1_mailing_address',
                'bank_bic': 'modified',
                'signer_gender': 'male',
                'signer_name': 'r1_signer_name',
                'signer_position': 'r1_signer_position',
                'company_tin': '1503009020',
                'contacts': [
                    {
                        'email': 'example@yandex.ru',
                        'name': 'r1_name',
                        'phone': '+79011111111',
                    },
                ],
                'st_link': 'r1_st_link',
                'power_of_attorney_limit': '100',
                'reason': 'r1_reason',
                'desired_button_name': 'r1_desired_button_name',
            },
            {
                '_id': 'request_accepted',
                'activation_email_sent': True,
                'additional_information': 'r1_additional_information',
                'bank_account_number': 'r1_bank_account_number',
                'bank_bic': 'modified',
                'client_id': 'r1_client_id',
                'client_login_id': 'small_yandex_login_id',
                'client_tmp_password': 'some_aes_string',
                'company_cio': 'r1_company_cio',
                'company_tin_id': 'tin_pd_id2',
                'contacts': [
                    {
                        'email_id': 'example_email_pd_id',
                        'name': 'r1_name',
                        'phone_id': 'phone_pd_id_1',
                    },
                ],
                'contract_type': 'postpaid',
                'created': datetime.datetime(2000, 1, 1, 0, 0),
                'desired_button_name': 'r1_desired_button_name',
                'enterprise_name_full': 'r1_enterprise_name_full',
                'enterprise_name_short': 'r1_enterprise_name_short',
                'final_status_date': datetime.datetime(2000, 1, 1, 0, 0),
                'final_status_manager_login': 'r1_final_status_manager_login',
                'legal_address': '7;r1_legal_address',
                'mailing_address': '7;r1_mailing_address',
                'manager_login': 'r1_manager_login',
                'power_of_attorney_limit': '100',
                'reason': 'r1_reason',
                'attachments': [
                    {'file_key': 'r1_file_key1', 'filename': 'r1_filename1'},
                    {'file_key': 'r1_file_key2', 'filename': 'r1_filename2'},
                ],
                'signer_duly_authorized': 'authority_agreement',
                'signer_gender': 'male',
                'signer_name': 'r1_signer_name',
                'signer_position': 'r1_signer_position',
                'st_link': 'r1_st_link',
                'status': 'accepted',
                'last_error': 'error',
                'error_reason': 'some error reason',
                'service': 'taxi',
                'billing_client_id': 73170692,
            },
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_change(
        mock_personal,
        taxi_corp_requests_web,
        db,
        request_id,
        request_params,
        expected_result,
):
    response = await taxi_corp_requests_web.put(
        '/v1/manager-requests',
        params={'request_id': request_id},
        json=request_params,
    )

    assert response.status == 200, await response.json()

    db_item = await db.corp_manager_requests.find_one(
        {'_id': request_id}, projection={'updated': 0},
    )
    assert db_item == expected_result


@pytest.mark.parametrize(
    ['client_ids', 'expected_response', 'status_code'],
    [
        (
            ['r1_client_id'],
            {
                'manager_requests': [
                    {
                        'activation_email_sent': True,
                        'additional_information': 'r1_additional_information',
                        'attachments': [
                            {
                                'filename': 'r1_filename1',
                                'url': '$mockserver/mds/get-taxi/r1_file_key1',
                            },
                            {
                                'filename': 'r1_filename2',
                                'url': '$mockserver/mds/get-taxi/r1_file_key2',
                            },
                        ],
                        'bank_account_number': 'r1_bank_account_number',
                        'bank_bic': 'r1_bank_bic',
                        'client_id': 'r1_client_id',
                        'client_login': 'small_yandex_login',
                        'client_tmp_password': 'some_aes_string',
                        'company_cio': 'r1_company_cio',
                        'company_tin': '500100732259',
                        'contacts': [
                            {
                                'email': 'example@yandex.ru',
                                'name': 'r1_name',
                                'phone': '+79011111111',
                            },
                        ],
                        'contract_type': 'postpaid',
                        'created': '2000-01-01T03:00:00+03:00',
                        'desired_button_name': 'r1_desired_button_name',
                        'enterprise_name_full': 'r1_enterprise_name_full',
                        'enterprise_name_short': 'r1_enterprise_name_short',
                        'final_status_date': '2000-01-01T03:00:00+03:00',
                        'final_status_manager_login': (
                            'r1_final_status_manager_login'
                        ),
                        'id': 'request_accepted',
                        'last_error': 'error',
                        'error_reason': 'some error reason',
                        'legal_address': '7;r1_legal_address',
                        'mailing_address': '7;r1_mailing_address',
                        'manager_login': 'r1_manager_login',
                        'power_of_attorney_limit': '100',
                        'readonly_fields': [
                            'id',
                            'status',
                            'created',
                            'readonly_fields',
                            'manager_login',
                            'signer_duly_authorized',
                            'attachments',
                            'final_status_date',
                            'final_status_manager_login',
                            'client_id',
                            'client_login',
                            'client_tmp_password',
                            'billing_external_id',
                            'last_error',
                            'country',
                            'activation_email_sent',
                        ],
                        'reason': 'r1_reason',
                        'service': 'taxi',
                        'signer_duly_authorized': 'authority_agreement',
                        'signer_gender': 'male',
                        'signer_name': 'r1_signer_name',
                        'signer_position': 'r1_signer_position',
                        'st_link': 'r1_st_link',
                        'status': 'accepted',
                        'updated': '2000-01-01T03:00:00+03:00',
                        'billing_client_id': 73170692,
                    },
                ],
            },
            200,
        ),
        (['non_exist_id'], {'manager_requests': []}, 200),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_get_by_client_id(
        web_app_client,
        mock_personal,
        client_ids,
        expected_response,
        status_code,
):
    response = await web_app_client.post(
        '/v1/manager-requests/by-client-ids', json={'client_ids': client_ids},
    )
    response_json = await response.json()
    manager_requests = response_json.get('manager_requests')
    expected_manager_request = expected_response.get('manager_requests')

    if status_code == 200 and manager_requests:
        readonly_fields = manager_requests[0].pop('readonly_fields')
        expected_readonly_fields = expected_manager_request[0].pop(
            'readonly_fields',
        )
        assert set(readonly_fields) == set(expected_readonly_fields)

    assert response.status == status_code, response_json
    assert response_json == expected_response
