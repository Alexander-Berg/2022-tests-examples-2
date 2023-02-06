import pytest

AUTH_PARAMETERS = (
    'code=auth_code_from_amo&state=code_update_key&'
    'referer=yandexdeliverysandbox.amocrm.ru&client_id=client_id'
)
BAD_AUTH_PARAMETERS = (
    'code=auth_code_from_amo&state=wrong_code_update_key&'
    'referer=yandexdeliverysandbox.amocrm.ru&client_id=client_id'
)

YA_FORM_MAKE_NOTE_BODY = {
    'amo_handle': 'leads_note_post',
    'item_body': {
        'nein': 'ja',
        'entity_id': 1,
        'note_type': 'common',
        'params': {'text': 'note text'},
    },
    'special_fields': [
        {
            'name': 'bool_field',
            'value': 'Да',
            'location': 'root',
            'type': 'string2bool',
        },
        {
            'name': 'timestamp_field',
            'value': '2022-01-01T22:01',
            'location': 'root',
            'type': 'timestamp2unixtimestamp',
        },
        {
            'name': 'user_id_field',
            'value': 'voytekh@yandex-team.ru',
            'location': 'root',
            'type': 'login2userid',
        },
    ],
}

YA_FORM_MAKE_TASK_BODY = {
    'amo_handle': 'task_post',
    'item_body': {
        'text': 'task text',
        'complete_till': 1650717903,
        'entity_id': 1,
        'entity_type': 'leads',
        'task_type_id': 1,
    },
    'special_fields': [
        {
            'name': 'bool_field',
            'value': 'Да',
            'location': 'root',
            'type': 'string2bool',
        },
        {
            'name': 'timestamp_field',
            'value': '2022-01-01T22:01',
            'location': 'root',
            'type': 'timestamp2unixtimestamp',
        },
        {
            'name': 'responsible_user_id',
            'value': 'voytekh@yandex-team.ru',
            'location': 'root',
            'type': 'login2userid',
        },
    ],
}

YA_FORM_MAKE_TASK_BAD_BODY = {
    'amo_handle': 'task_post',
    'item_body': {
        'text': 'task text',
        'complete_till': 1650717903,
        'entity_id': 1,
        'entity_type': 'leads',
        'task_type_id': 1,
    },
    'special_fields': [
        {
            'name': 'bool_field',
            'value': 'Наверное',
            'location': 'root',
            'type': 'string2bool',
        },
        {
            'name': 'timestamp_field',
            'value': '2022-01-99T22:01',
            'location': 'root',
            'type': 'timestamp2unixtimestamp',
        },
        {
            'name': 'responsible_user_id',
            'value': 'not_voytekh@yandex-team.ru',
            'location': 'root',
            'type': 'login2userid',
        },
    ],
}

YA_FORM_NOTE_RESULT = [
    {
        'bool_field': True,
        'entity_id': 1,
        'nein': 'ja',
        'note_type': 'common',
        'params': {'text': 'note text'},
        'timestamp_field': 1641074460,
        'user_id_field': 133780085,
    },
]

YA_FORM_TASK_RESULT = [
    {
        'bool_field': True,
        'timestamp_field': 1641074460,
        'responsible_user_id': 133780085,
        'entity_id': 1,
        'entity_type': 'leads',
        'task_type_id': 1,
        'text': 'task text',
        'complete_till': 1650717903,
    },
]

YA_FORM_HEADERS = {
    'X-FORM-ID': '1',
    'X-Access-Token': 'API_TOKEN_YA_FORM_PROXY_AMOCRM',
}

YA_FORM_BAD_HEADERS = {
    'X-FORM-ID': '321',
    'X-Access-Token': 'API_TOKEN_YA_FORM_PROXY_AMOCRM',
}

MAKE_LEAD_HAPPY_PASS_QUERY = {
    'data': [
        {
            'item_body': {
                'int_key': 1,
                'str_key': '1',
                'obj_key': {'arr_key': [1, 2, 3]},
                'formatted_bool_y': {
                    'formatting_rule': 'string2bool',
                    'formatting_value': 'Да',
                },
                'formatted_bool_n': {
                    'formatting_rule': 'string2bool',
                    'formatting_value': 'Нет',
                },
                'formatted_bad_key': {
                    'formatting_rule': 'bad_rule',
                    'formatting_value': 'Да',
                },
                'formatted_dt': {
                    'formatting_rule': 'timestamp2unixtimestamp',
                    'formatting_value': '2022-06-12T12:12',
                },
                'formatted_uiser_id': {
                    'formatting_rule': 'email2userid',
                    'formatting_value': 'voytekh@yandex-team.ru',
                },
            },
            'amo_handle': 'complex',
        },
        {
            'amo_handle': 'task_post',
            'item_body': {
                'text': 'task text',
                'complete_till': {
                    'formatting_rule': 'timestamp2unixtimestamp',
                    'formatting_value': '2022-06-12T12:12',
                },
                'responsible_user_id': {
                    'formatting_rule': 'email2userid',
                    'formatting_value': 'voytekh@yandex-team.ru',
                },
                'task_type_id': 1,
            },
        },
        {
            'amo_handle': 'leads_note_post',
            'item_body': {
                'entity_id': 0,
                'nein': 'ja',
                'note_type': 'common',
                'params': {'text': 'note text'},
            },
        },
    ],
}


@pytest.mark.config(
    AMOCRM_CARGO_URL={
        'url': 'yandexdeliverysandbox.amocrm.ru',
        'auth_url': 'http://cargo-sf.taxi.tst.yandex.net/api/v1/amocrm/auth',
    },
)
@pytest.mark.parametrize(
    'response_code,auth_parameters,response_json',
    (
        (200, AUTH_PARAMETERS, {}),
        (
            400,
            BAD_AUTH_PARAMETERS,
            {
                'code': 'bad_credentials',
                'message': 'Credentials supplied are not valid.',
            },
        ),
    ),
)
async def test_auth(
        taxi_cargo_sf,
        mock_amo_auth,
        response_code,
        auth_parameters,
        response_json,
):
    response = await taxi_cargo_sf.get(
        f'/api/v1/amocrm/auth?' + auth_parameters,
    )
    assert response.status_code == response_code
    assert response.json() == response_json


async def test_refresh_auth(
        taxi_cargo_sf,
        mock_amo_auth,
        mock_amo_create_task,
        update_bad_amo_auth_token_record,
        mock_amo_leads,
):
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/amocrm/internal-requests/create-task',
        json={
            'external_event_id': 'external_event_id401',
            'task_type_id': 1,
            'text': 'text',
            'complete_till': 123456,
        },
    )
    assert mock_amo_leads.times_called == 2
    assert mock_amo_create_task.times_called == 1
    assert response.status_code == 200


async def test_lead_event(taxi_cargo_sf):
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/amocrm/internal-requests/lead-event',
        json={
            'external_event_id': 'external_event_id',
            'details': {
                'company_name': 'company_name',
                'contact_last_name': 'contact_last_name',
                'contact_mail': 'contact_mail',
                'contact_first_name': 'contact_first_name',
                'company_utm_source': 'company_utm_source',
                'lead_potential': 9001,
                'company_tin': '123456789',
                'company_city': 'company_city',
                'company_country': 'company_country',
                'company_industry': 'company_industry',
                'lead_corp_client_id': 'lead_corp_client_id',
                'ticket_state': 'card_bound',
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    'expected_response_code,data_validity',
    ((200, 'valid_data'), (400, 'some_invalid_data')),
)
async def test_create_task(
        taxi_cargo_sf,
        mock_amo_create_task,
        mock_amo_leads,
        expected_response_code,
        data_validity,
):
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/amocrm/internal-requests/create-task',
        json={
            'external_event_id': 'external_event_id',
            'task_type_id': 1,
            'text': data_validity,
            'complete_till': 123456,
            'responsible_user_id': 111,
        },
    )
    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        request_json = mock_amo_create_task.next_call()['request'].json
        assert response.json() == {}
        assert request_json == [
            {
                'entity_id': 1686611,
                'entity_type': 'leads',
                'task_type_id': 1,
                'text': 'valid_data',
                'complete_till': 123456,
                'responsible_user_id': 111,
            },
        ]


@pytest.mark.parametrize(
    'expected_response_code,data_validity',
    ((200, 'valid_data'), (400, 'some_invalid_data')),
)
async def test_create_free_task(
        taxi_cargo_sf,
        mock_amo_create_task,
        mock_amo_leads,
        expected_response_code,
        data_validity,
):
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/amocrm/internal-requests/create-task-free',
        json={
            'tasks': [
                {
                    'text': data_validity,
                    'complete_till': 1649998784,
                    'entity_id': 1,
                    'entity_type': 'leads',
                    'task_type_id': 1,
                },
                {
                    'text': 'text2',
                    'complete_till': 1649998784,
                    'entity_id': 1,
                    'entity_type': 'leads',
                    'task_type_id': 1,
                },
            ],
        },
    )
    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        request_json = mock_amo_create_task.next_call()['request'].json
        assert response.json() == {}
        assert request_json == [
            {
                'entity_id': 1,
                'entity_type': 'leads',
                'task_type_id': 1,
                'text': 'valid_data',
                'complete_till': 1649998784,
            },
            {
                'entity_id': 1,
                'entity_type': 'leads',
                'task_type_id': 1,
                'text': 'text2',
                'complete_till': 1649998784,
            },
        ]


@pytest.mark.parametrize(
    'expected_response_code,request_body,headers,expected_result',
    (
        pytest.param(
            200,
            YA_FORM_MAKE_NOTE_BODY,
            YA_FORM_HEADERS,
            YA_FORM_NOTE_RESULT,
            id='note',
        ),
        pytest.param(
            200,
            YA_FORM_MAKE_TASK_BODY,
            YA_FORM_HEADERS,
            YA_FORM_TASK_RESULT,
            id='task',
        ),
        pytest.param(
            403,
            YA_FORM_MAKE_TASK_BODY,
            YA_FORM_BAD_HEADERS,
            None,
            id='bad_form_id',
        ),
        pytest.param(
            400,
            YA_FORM_MAKE_TASK_BAD_BODY,
            YA_FORM_HEADERS,
            None,
            id='bad_task_data',
        ),
    ),
)
async def test_ya_form_proxy(
        taxi_cargo_sf,
        mock_amo_create_lead_note,
        mock_amo_users,
        mock_amo_create_task,
        expected_response_code,
        request_body,
        headers,
        expected_result,
):
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/amocrm/internal-requests/ya-forms-request',
        json=request_body,
        headers=headers,
    )
    assert response.status_code == expected_response_code
    if expected_response_code != 200:
        return
    assert mock_amo_users.times_called == 2
    if request_body['amo_handle'] == 'leads_note_post':
        request_json = mock_amo_create_lead_note.next_call()['request'].json
    elif request_body['amo_handle'] == 'task_post':
        request_json = mock_amo_create_task.next_call()['request'].json
    assert request_json == expected_result


@pytest.mark.parametrize(
    'request_data,request_to_amo_json,response_json,headers,expected_code,'
    'request_to_amo_task_json,request_to_amo_note_json',
    (
        pytest.param(
            MAKE_LEAD_HAPPY_PASS_QUERY,
            [
                {
                    'int_key': 1,
                    'str_key': '1',
                    'obj_key': {'arr_key': [1, 2, 3]},
                    'formatted_bool_y': True,
                    'formatted_bool_n': False,
                    'formatted_bad_key': {
                        'formatting_rule': 'bad_rule',
                        'formatting_value': 'Да',
                    },
                    'formatted_dt': 1655035920,
                    'formatted_uiser_id': 133780085,
                },
            ],
            {'data': [{'object_type': 'lead', 'id_list': [15198335]}]},
            YA_FORM_HEADERS,
            200,
            [
                {
                    'entity_id': 15198335,
                    'entity_type': 'leads',
                    'task_type_id': 1,
                    'text': 'task text',
                    'complete_till': 1655035920,
                    'responsible_user_id': 133780085,
                },
            ],
            [
                {
                    'nein': 'ja',
                    'entity_id': 15198335,
                    'note_type': 'common',
                    'params': {'text': 'note text'},
                },
            ],
            id='happy_pass',
        ),
        pytest.param(
            {'data': [{'amo_handle': 'complex', 'item_body': {}}]},
            [{}],
            {
                'code': 'processing_error',
                'message': (
                    'There were some errors with request: complex_query: '
                    '{"validation-errors":[{"request_id":"qweasd",'
                    '"errors":[{"code":"InvalidType",'
                    '"path":"_embedded.contacts.0.responsible_'
                    'user_id","detail":"This value should '
                    'be of type int."},{"code":"NotSupportedCho'
                    'ice","path":"_embedded.contacts.0.'
                    'responsible_user_id","detail":"The value you '
                    'selected is not a valid choice."}]}]} ||'
                ),
            },
            YA_FORM_HEADERS,
            400,
            None,
            None,
            id='amo_400_reponse',
        ),
        pytest.param(
            {'data': [{'amo_handle': 'complex', 'item_body': {}}]},
            None,
            None,
            YA_FORM_BAD_HEADERS,
            403,
            None,
            None,
            id='bad_access_params',
        ),
    ),
)
async def test_make_lead(
        taxi_cargo_sf,
        mock_amo_complex,
        mock_amo_users,
        mock_amo_create_task,
        mock_amo_create_lead_note,
        request_data,
        request_to_amo_json,
        response_json,
        headers,
        expected_code,
        request_to_amo_task_json,
        request_to_amo_note_json,
):
    response = await taxi_cargo_sf.post(
        '/internal/cargo-sf/amocrm/internal-requests/make-lead',
        json=request_data,
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 403:
        return
    request_json = mock_amo_complex.next_call()['request'].json
    assert request_json == request_to_amo_json
    assert response.json() == response_json
    if expected_code != 200:
        return
    request_task_json = mock_amo_create_task.next_call()['request'].json
    assert request_task_json == request_to_amo_task_json
    request_note_json = mock_amo_create_lead_note.next_call()['request'].json
    assert request_note_json == request_to_amo_note_json
