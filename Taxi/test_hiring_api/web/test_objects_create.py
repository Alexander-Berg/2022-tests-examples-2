import uuid

import pytest

EXTERNAL_ID = '4552995ef815c9bba2dae61d5e0f643a'
FIELD_DATA = 'data'
FIELD_ENDPOINT = 'endpoint'
FIELD_STATUS_CODE = 'status_code'
REQUESTS_FILE = 'requests.json'
SOLOMON_SENSOR_STATUS_CHANGE = 'salesforce.lead.status_change'
X_DELIVERY_ID = 'das3tji43tjgj3j9u484tj3fiewo'
STQ_SALESFORCE_CREATION_QUEUE_NAME = 'hiring_create_salesforce_objects'


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.parametrize(
    'request_name, stq_request_file_name',
    [
        ('one_object', 'normal_stq_request.json'),
        (
            'one_object_missing_non_required_object',
            'missing_non_required_object.json',
        ),
        ('two_objects_with_update', 'two_objects_with_update.json'),
        ('phone_without_plus', 'missing_non_required_object.json'),
        ('trash_phone', 'missing_non_required_object.json'),
        ('no_markup_asset', 'no_markup_asset.json'),
    ],
)
async def test_objects_create_simple_valid_requests(
        request_objects_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        mock_hiring_candidates_region,
        stq_mock,
        load_json,
        request_name,
        stq_request_file_name,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/normal.json'),
    )
    request_data = load_json(REQUESTS_FILE)['valid'][request_name]

    # act
    response_body = await request_objects_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {'external_ids': [EXTERNAL_ID]},
    }

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == STQ_SALESFORCE_CREATION_QUEUE_NAME
    assert len(stq_request['args']) == 1
    assert stq_request['args'][0].json == load_json(
        f'stq_requests/{stq_request_file_name}',
    )

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.parametrize(
    'request_name, response_file_name',
    [
        ('phone_empty', 'invalid_phone_error.json'),
        ('phone_invalid', 'invalid_phone_error.json'),
        ('short_phone', 'invalid_phone_error.json'),
        ('without_phone_code', 'invalid_phone_error.json'),
        ('unknown_country_code', 'invalid_phone_error.json'),
        ('no_markup_lead', 'no_markup_error.json'),
        ('no_dynamic_actions', 'no_dynamic_flow_error.json'),
        ('update_without_id', 'missing_id_error.json'),
    ],
)
async def test_objects_create_simple_invalid_requests(
        request_objects_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        stq_mock,
        load_json,
        request_name,
        response_file_name,
):
    # arrange
    request_data = load_json(REQUESTS_FILE)['invalid'][request_name]

    # act
    response_body = await request_objects_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == load_json(f'main_responses/{response_file_name}')

    assert stq_mock.times_called == 0


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.parametrize(
    'request_name, response_file_name',
    [
        ('dynamic_actions_missing_object', 'object_missing_error.json'),
        ('missing_required_fields', 'missing_field_error.json'),
        ('excessive_actions', 'execssive_actions_error.json'),
        (
            'dynamic_actions_missing_markup_object',
            'no_dynamic_object_error.json',
        ),
        (
            'dynamic_actions_missing_object_field',
            'missing_dynamic_field_error.json',
        ),
    ],
)
async def test_objects_create_simple_invalid_requests_with_region_id_request(
        request_objects_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        mock_hiring_candidates_region,
        stq_mock,
        load_json,
        request_name,
        response_file_name,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/normal.json'),
    )
    request_data = load_json(REQUESTS_FILE)['invalid'][request_name]

    # act
    response_body = await request_objects_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == load_json(f'main_responses/{response_file_name}')

    assert stq_mock.times_called == 0

    assert hiring_candidates_region_mock.times_called == 1


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_PROCESSING_FLOW_MARKUP_ENABLED=True)
@pytest.mark.parametrize(
    'use_external_id, expected_response_external_id, expected_stq_external_id',
    [(True, EXTERNAL_ID, EXTERNAL_ID), (False, '', X_DELIVERY_ID)],
)
async def test_objects_create_check_id(
        load_json,
        request_objects_create,
        stq_mock,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup_by_flow,
        mock_data_markup_experiments3,
        mock_hiring_candidates_region,
        taxi_config,
        use_external_id,
        expected_response_external_id,
        expected_stq_external_id,
):
    # arrange
    hiring_data_markup_mock = mock_hiring_data_markup_by_flow(
        responses_by_flows={
            None: load_json('response_data_markup.json')['valid']['Asset'],
            'hiring_data_markup_new_lead_check_processing_flow': (
                load_json('hiring_data_markup_responses/processing_flow.json')
            ),
        },
    )

    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/normal.json'),
    )
    taxi_config.set_values(
        {
            'HIRING_API_USE_EXTERNAL_ID_BY_ENDPOINTS': {
                '__default__': {'enabled': use_external_id},
                'endpoints': [],
            },
        },
    )
    request_data = load_json(REQUESTS_FILE)['valid']['one_object']

    # act
    response_body = await request_objects_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {'external_ids': [expected_response_external_id]},
    }

    assert hiring_data_markup_mock.times_called == 4

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == STQ_SALESFORCE_CREATION_QUEUE_NAME
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/normal_with_flow_markup.json')
    assert stq_args['kwargs']['external_id'] == expected_stq_external_id

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.parametrize(
    'request_type, request_name, no_lead',
    [
        ('valid', 'one_object', False),
        ('valid', 'one_object_missing_non_required_object', False),
        ('valid', 'two_objects_with_update', False),
        ('valid', 'no_markup_asset', False),
        ('invalid', 'phone_empty', True),
        ('invalid', 'phone_invalid', True),
        ('invalid', 'no_markup_lead', False),
        ('invalid', 'no_dynamic_actions', False),
        ('invalid', 'dynamic_actions_missing_object', False),
        ('invalid', 'dynamic_actions_missing_markup_object', False),
        ('invalid', 'dynamic_actions_missing_object_field', False),
        ('invalid', 'missing_required_fields', False),
        ('invalid', 'update_without_id', True),
        ('invalid', 'excessive_actions', False),
    ],
)
async def test_objects_create_should_save_metrics(
        request_objects_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        stq_mock,
        load_json,
        request_type,
        request_name,
        no_lead,
        get_single_stat_by_label_values,
        web_app,
        web_app_client,
):
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    await web_app_client.post(
        '/v1/objects/create',
        json=request_data[FIELD_DATA],
        params={'endpoint': request_data[FIELD_ENDPOINT]},
        headers={'X-Delivery-Id': uuid.uuid4().hex},
    )

    actual_stats = get_single_stat_by_label_values(
        web_app['context'], {'sensor': SOLOMON_SENSOR_STATUS_CHANGE},
    )
    if no_lead:
        assert actual_stats is None
        return

    del actual_stats['labels']['code']
    status = ''
    for obj in request_data[FIELD_DATA]['objects']:
        if obj['object'] != 'Lead':
            continue
        for field in obj['fields']:
            if field['name'] == 'Status':
                status = field['value']
    expected_stats = {
        'kind': 'IGAUGE',
        'labels': {
            'endpoint': request_data[FIELD_ENDPOINT],
            'sensor': SOLOMON_SENSOR_STATUS_CHANGE,
            'status': status,
            'source': 'hiring-api',
        },
        'timestamp': None,
        'value': 1,
    }
    assert actual_stats == expected_stats


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=False)
async def test_objects_create_with_disabled_region(
        load_json,
        request_objects_create,
        stq_mock,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
):
    # arrange
    request_data = load_json(REQUESTS_FILE)['valid']['one_object']

    # act
    response_body = await request_objects_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {'external_ids': [EXTERNAL_ID]},
    }

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == STQ_SALESFORCE_CREATION_QUEUE_NAME
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/region_disabled.json')
    assert stq_args['kwargs']['external_id'] == EXTERNAL_ID


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.parametrize('region_by_code_status', [400, 404])
async def test_objects_create_without_sf_object(
        load_json,
        request_objects_create,
        stq_mock,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        mock_hiring_candidates_region,
        region_by_code_status,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/error.json'),
        status=region_by_code_status,
    )
    request_data = load_json(REQUESTS_FILE)['valid']['one_object']

    # act
    response_body = await request_objects_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {'external_ids': [EXTERNAL_ID]},
    }

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == STQ_SALESFORCE_CREATION_QUEUE_NAME
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/region_default.json')
    assert stq_args['kwargs']['external_id'] == EXTERNAL_ID

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_DEFAULT_REGION_ID=None)
async def test_objects_create_with_region_error_and_no_default(
        load_json,
        request_objects_create,
        stq_mock,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        mock_hiring_candidates_region,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/error.json'),
        status=400,
    )
    request_data = load_json(REQUESTS_FILE)['valid']['one_object']

    # act
    response_body = await request_objects_create(
        request=request_data[FIELD_DATA],
        endpoint=request_data[FIELD_ENDPOINT],
        status_code=400,
    )

    # assert
    assert response_body == load_json(
        'main_responses/missing_field_error.json',
    )

    assert stq_mock.times_called == 0

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_DEFAULT_REGION_ID=213)
async def test_objects_create_with_region_error_but_with_default(
        load_json,
        request_objects_create,
        stq_mock,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
        mock_hiring_candidates_region,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/error.json'),
        status=400,
    )
    request_data = load_json(REQUESTS_FILE)['valid']['one_object']

    # act
    response_body = await request_objects_create(
        request=request_data[FIELD_DATA],
        endpoint=request_data[FIELD_ENDPOINT],
        status_code=201,
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {'external_ids': [EXTERNAL_ID]},
    }

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == STQ_SALESFORCE_CREATION_QUEUE_NAME
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/region_default.json')

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_DEFAULT_REGION_ID=10001)
async def test_objects_create_with_prefilled_region_makes_no_request(
        load_json,
        request_objects_create,
        stq_mock,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        mock_data_markup_experiments3,
):
    # arrange
    request_data = load_json(REQUESTS_FILE)['valid']['region_id_is_prefilled']

    # act
    response_body = await request_objects_create(
        request=request_data[FIELD_DATA],
        endpoint=request_data[FIELD_ENDPOINT],
        status_code=201,
    )

    # assert
    assert response_body == {
        'code': 'SUCCESS',
        'message': 'Survey added.',
        'details': {'external_ids': [EXTERNAL_ID]},
    }

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == STQ_SALESFORCE_CREATION_QUEUE_NAME
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/region_prefilled.json')
