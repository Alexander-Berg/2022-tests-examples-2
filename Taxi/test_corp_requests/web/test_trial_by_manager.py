import datetime

import aiohttp
import pytest

REQUEST_PHONE_CLEANED = '+79011111111'
HEADERS = {'X-Real-IP': 'remote_ip'}

ONLY_REQUIRED_FIELDS_SUCCESS = {
    'field_1': '{"question": {"type": {"slug": "answer_choices"}, "slug": "manager_login"}, "value": "\\u0422\\u0443\\u0433\\u0430\\u0435\\u043d\\u043a\\u043e \\u0410\\u043d\\u0442\\u043e\\u043d (engineer)"}',  # noqa: E501
    'field_2': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "company"}, "value": "Inkram"}',  # noqa: E501
    'field_10': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "name"}, "value": "Anton"}',  # noqa: E501
    'field_12': '{"question": {"type": {"slug": "answer_phone"}, "slug": "phone"}, "value": "+7 (926) 345-22-42"}',  # noqa: E501
    'field_11': '{"question": {"type": {"slug": "answer_non_profile_email"}, "slug": "email"}, "value": "qwerty@gmail.com"}',  # noqa: E501
    'field_35': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "city"}, "value": "Москва"}',  # noqa: E501
    'field_5': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "enterprise_name_short"}, "value": "ООО ИНКРАМ"}',  # noqa: E501
    'field_6': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "enterprise_name_full"}, "value": "ООО НПФ ИНКРАМ"}',  # noqa: E501
    'field_13': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_form"}, "value": "OOO"}',  # noqa: E501
    'field_3': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "company_tin"}, "value": "500100732259"}',  # noqa: E501
    'field_17': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "bank_bic"}, "value": "044525225"}',  # noqa: E501
    'field_21': '{"question": {"type": {"slug": "answer_boolean"}, "slug": "contract_by_proxy"}, "value": "Нет"}',  # noqa: E501
    'field_94': '{"question": {"type": {"slug": "answer_boolean"}, "slug": "mailing_address_differs"}, "value": "Нет"}',  # noqa: E501
    'field_90': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_city"}, "value": "Питер"}',  # noqa: E501
    'field_91': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_zip"}, "value": "12345"}',  # noqa: E501
    'field_92': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_street"}, "value": "Дворцовская"}',  # noqa: E501
    'field_93': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_house"}, "value": "38"}',  # noqa: E501
    'field_80': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_city"}, "value": "Москва"}',  # noqa: E501
    'field_81': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_zip"}, "value": "115222"}',  # noqa: E501
    'field_82': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_street"}, "value": "Москворечье"}',  # noqa: E501
    'field_83': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_house"}, "value": "2к2"}',  # noqa: E501
    'field_18': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "bank_account_number"}, "value": "40702810638050013199"}',  # noqa: E501
    'field_23': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "proxy_scan"}, "value": null}',  # noqa: E501
    'field_36': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "bank_name"}, "value": "СБЕР"}',  # noqa: E501
    'field_37': '{"question": {"type": {"slug": "answer_date"}, "slug": "company_registration_date"}, "value": "2020-10-15"}',  # noqa: E501
    'field_39': '{"question": {"type": {"slug": "answer_choices"}, "slug": "signer_gender"}, "value": "Мужской"}',  # noqa: E501
    'field_40': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "signer_name"}, "value": "Ivan"}',  # noqa: E501
    'field_41': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "signer_position"}, "value": "CEO"}',  # noqa: E501
    'noop': 'content',
}

ONLY_REQUIRED_FIELDS_SUCCESS_ISR = {
    'field_1': '{"question": {"type": {"slug": "answer_choices"}, "slug": "manager_login"}, "value": "\\u0422\\u0443\\u0433\\u0430\\u0435\\u043d\\u043a\\u043e \\u0410\\u043d\\u0442\\u043e\\u043d (engineer)"}',  # noqa: E501
    'field_2': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "company"}, "value": "Inkram"}',  # noqa: E501
    'field_10': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "name"}, "value": "Anton"}',  # noqa: E501
    'field_12': '{"question": {"type": {"slug": "answer_phone"}, "slug": "phone"}, "value": "+7 (926) 345-22-42"}',  # noqa: E501
    'field_11': '{"question": {"type": {"slug": "answer_non_profile_email"}, "slug": "email"}, "value": "qwerty@gmail.com"}',  # noqa: E501
    'field_35': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "city"}, "value": "Москва"}',  # noqa: E501
    'field_5': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "enterprise_name_short"}, "value": "ООО ИНКРАМ"}',  # noqa: E501
    'field_6': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "enterprise_name_full"}, "value": "ООО НПФ ИНКРАМ"}',  # noqa: E501
    'field_13': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_form"}, "value": "OOO"}',  # noqa: E501
    'field_17': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "bank_bic"}, "value": "044525225"}',  # noqa: E501
    'field_21': '{"question": {"type": {"slug": "answer_boolean"}, "slug": "contract_by_proxy"}, "value": "Нет"}',  # noqa: E501
    'field_94': '{"question": {"type": {"slug": "answer_boolean"}, "slug": "mailing_address_differs"}, "value": "Нет"}',  # noqa: E501
    'field_90': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_city"}, "value": "Питер"}',  # noqa: E501
    'field_91': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_zip"}, "value": "12345"}',  # noqa: E501
    'field_92': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_street"}, "value": "Дворцовская"}',  # noqa: E501
    'field_93': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "mailing_address_house"}, "value": "38"}',  # noqa: E501
    'field_80': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_city"}, "value": "Москва"}',  # noqa: E501
    'field_81': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_zip"}, "value": "115222"}',  # noqa: E501
    'field_82': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_street"}, "value": "Москворечье"}',  # noqa: E501
    'field_83': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "legal_address_house"}, "value": "2к2"}',  # noqa: E501
    'field_18': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "bank_account_number"}, "value": "40702810638050013199"}',  # noqa: E501
    'field_23': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "proxy_scan"}, "value": null}',  # noqa: E501
    'field_36': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "bank_name"}, "value": "СБЕР"}',  # noqa: E501
    'field_37': '{"question": {"type": {"slug": "answer_date"}, "slug": "company_registration_date"}, "value": "2020-10-15"}',  # noqa: E501
    'field_39': '{"question": {"type": {"slug": "answer_choices"}, "slug": "signer_gender"}, "value": "Мужской"}',  # noqa: E501
    'field_40': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "signer_name"}, "value": "Ivan"}',  # noqa: E501
    'field_41': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "signer_position"}, "value": "CEO"}',  # noqa: E501
    'field_38': '{"question": {"type": {"slug": "answer_choices"}, "slug": "service"}, "value": "Доставка"}',  # noqa: E501
    'field_101': '{"question": {"type": {"slug": "answer_choices"}, "slug": "country"}, "value": "isr"}',  # noqa: E501
    'field_3': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "company_tin"}, "value": "559017555"}',  # noqa: E501
    'field_103': '{"question": {"type": {"slug": "answer_short_text"}, "slug": "registration_number"}, "value": "123456789"}',  # noqa: E501
    'noop': 'content',
}

EXPECTED_DRAFT_RUS = {
    'contact_emails': ['qwerty@gmail.com'],
    'contact_emails_ids': ['random_id'],
    'contact_phone': '+79263452242',
    'contact_phone_id': 'pd_id1',
    'contact_name': 'Anton',
    'company_name': 'Inkram',
    'country': 'rus',
    'city': 'Москва',
    'client_id': 'client_id',
    'yandex_login_id': 'pd_id',
    'references': {'ya_source': 'businesstaxi'},
    'contract_type': 'taxi',
    'bank_account_number': '40702810638050013199',
    'bank_bic': '044525225',
    'bank_name': 'СБЕР',
    'company_registration_date': datetime.datetime(2020, 10, 15, 0, 0),
    'company_tin': '500100732259',
    'company_tin_id': 'tin_pd_id',
    'contract_by_proxy': False,
    'enterprise_name_full': 'ООО НПФ ИНКРАМ',
    'enterprise_name_short': 'ООО ИНКРАМ',
    'legal_address': 'Москва;115222;Москворечье;2к2',
    'legal_address_info': {
        'post_index': '115222',
        'house': '2к2',
        'city': 'Москва',
        'street': 'Москворечье',
    },
    'legal_form': 'OOO',
    'mailing_address': 'Москва;115222;Москворечье;2к2',
    'mailing_address_info': {
        'post_index': '115222',
        'house': '2к2',
        'city': 'Москва',
        'street': 'Москворечье',
    },
    'proxy_scan': None,
    'services': ['taxi'],
    'signer_gender': 'male',
    'signer_name': 'Ivan',
    'signer_position': 'CEO',
    'flow': 'trial_by_manager',
    'draft_status': 'blank',
}

EXPECTED_DRAFT_ISR = {
    'contact_emails': ['qwerty@gmail.com'],
    'contact_emails_ids': ['random_id'],
    'contact_phone': '+79263452242',
    'contact_phone_id': 'pd_id1',
    'contact_name': 'Anton',
    'company_name': 'Inkram',
    'country': 'isr',
    'city': 'Москва',
    'client_id': 'client_id',
    'yandex_login_id': 'pd_id',
    'references': {'ya_source': 'businessdelivery'},
    'contract_type': 'cargo',
    'company_tin': '559017555',
    'company_tin_id': 'full_isr_draft_tin_id',
    'enterprise_name_full': 'ООО НПФ ИНКРАМ',
    'enterprise_name_short': 'ООО ИНКРАМ',
    # 'legal_address': 'Москва;115222;Москворечье;2к2',
    'legal_address_info': {
        'post_index': '115222',
        'house': '2к2',
        'city': 'Москва',
        'street': 'Москворечье',
    },
    'legal_form': 'OOO',
    # 'mailing_address': 'Москва;115222;Москворечье;2к2',
    'mailing_address_info': {
        'post_index': '115222',
        'house': '2к2',
        'city': 'Москва',
        'street': 'Москворечье',
    },
    'services': ['cargo'],
    'signer_gender': 'male',
    'signer_name': 'Ivan',
    'signer_position': 'CEO',
    'flow': 'trial_by_manager',
    'registration_number': '123456789',
    'draft_status': 'blank',
}


@pytest.mark.parametrize(
    'fields, files, expected_draft, expected_stq_zapier_args',
    [
        pytest.param(
            dict(
                ONLY_REQUIRED_FIELDS_SUCCESS,
                field_38='{"question": {"type": {"slug": "answer_choices"}, "slug": "service"}, "value": "Такси"}',  # noqa: E501
            ),
            {},
            EXPECTED_DRAFT_RUS,
            {
                'phone': '+79263452242',
                'email': 'qwerty@gmail.com',
                'name': 'Anton',
                'company': 'Inkram',
                'client_id': 'client_id',
                'city': 'Москва',
                'utm': {'ya_source': 'businesstaxi'},
                'country': 'rus',
            },
            id='Only required fields rus',
        ),
        pytest.param(
            ONLY_REQUIRED_FIELDS_SUCCESS_ISR,
            {},
            EXPECTED_DRAFT_ISR,
            {
                'phone': '+79263452242',
                'email': 'qwerty@gmail.com',
                'name': 'Anton',
                'company': 'Inkram',
                'client_id': 'client_id',
                'city': 'Москва',
                'utm': {'ya_source': 'businessdelivery'},
                'country': 'isr',
            },
            id='Only required fields isr',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
        {'dst': 'corp-clients', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
)
async def test_trial_by_manager(
        mock_mds,
        mock_personal_random_gen_login,
        taxi_corp_requests_web,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients,
        db,
        fields,
        files,
        expected_draft,
        expected_stq_zapier_args,
        stq,
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
        '/v1/trial-by-manager', data=mpwriter,
    )

    assert response.status == 200

    response_json = await response.json()

    request_draft = await db.corp_client_request_drafts.find(
        {'client_id': response_json['client_id']},
    ).to_list(None)

    assert len(request_draft) == 1
    draft = request_draft[0]
    draft.pop('_id')
    draft.pop('created')
    draft.pop('updated')

    assert draft.pop('yandex_login')
    assert draft == expected_draft

    call = stq.corp_send_request_data_to_zapier.next_call()
    call['kwargs']['client_request'].pop('login')
    assert call['kwargs']['client_request'] == expected_stq_zapier_args


@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
)
async def test_not_sent_data_to_zapier(
        taxi_corp_requests_web,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients,
        db,
        stq,
):
    fields = dict(
        ONLY_REQUIRED_FIELDS_SUCCESS_ISR,
        field_38='{"question": {"type": {"slug": "answer_choices"}, "slug": "service"}, "value": "Единый договор (доставка)"}',  # noqa: E501
    )

    with aiohttp.MultipartWriter('form-data') as mpwriter:
        for key, value in fields.items():
            payload = aiohttp.payload.StringPayload(value)
            payload.set_content_disposition('form-data', name=key)
            mpwriter.append_payload(payload)

    response = await taxi_corp_requests_web.post(
        '/v1/trial-by-manager', data=mpwriter,
    )
    assert response.status == 200
    request_draft = await db.corp_client_request_drafts.find_one(
        {'client_id': 'client_id'},
    )
    assert request_draft['services'] == ['taxi', 'cargo']
    assert stq.corp_send_request_data_to_zapier.times_called == 0
