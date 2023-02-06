import json

import pytest


@pytest.mark.config(
    PROCESS_AUTOMATION_SALESFORCE_ESB_EXTERNAL_STARTREK_SETTINGS={
        'external_startrek_settings': [
            {
                'name': 'robot-sf-market',
                'settings': {
                    'api_url': '$mockserver/external_startrek/v2/',
                    'web_url': 'https://st.test.yandex-team.ru/',
                    'client_kwargs': [
                        'summary',
                        'queue',
                        'description',
                        'ticket_type',
                        'parent',
                        'priority',
                        'sprints',
                        'assignee',
                        'followers',
                        'unique',
                        'tags',
                        'custom_fields',
                        'comment',
                        'log_extra',
                    ],
                },
            },
        ],
    },
)
@pytest.mark.parametrize(
    'request_file_name', ['normal.json', 'normal_without_tracker_alias.json'],
)
async def test_startrek_create_issue(
        taxi_process_automation_salesforce_esb_web,
        mockserver,
        mock_external_startrek,
        load_json,
        request_file_name,
):
    # arrange
    startrek_mock = mock_external_startrek(response={'key': 'QUEUE-123'})
    request = json.dumps(load_json(f'requests/{request_file_name}'))

    # act
    response = await taxi_process_automation_salesforce_esb_web.post(
        '/v1/external-tracker/issue', data=request,
    )

    # assert
    assert response.status == 200
    assert await response.json() == {
        'issue_link': 'https://st.test.yandex-team.ru/QUEUE-123',
    }

    assert startrek_mock.times_called == 1
    startrek_request = startrek_mock.next_call()['_request']
    assert startrek_request.method == 'POST'
    assert startrek_request.json == load_json('startrek_request.json')


@pytest.mark.now('2022-04-26T12:00:00+0000')
async def test_startrek_create_issue_without_setting_in_config(
        taxi_process_automation_salesforce_esb_web, mockserver, load_json,
):
    # arrange
    request = json.dumps(load_json('requests/normal.json'))

    # act
    response = await taxi_process_automation_salesforce_esb_web.post(
        '/v1/external-tracker/issue', data=request,
    )

    # assert
    assert response.status == 400
    assert await response.json() == load_json(
        'responses/no_settings_for_tracker.json',
    )


@pytest.mark.now('2022-04-26T12:00:00+0000')
@pytest.mark.config(
    PROCESS_AUTOMATION_SALESFORCE_ESB_EXTERNAL_STARTREK_SETTINGS={
        'external_startrek_settings': [
            {
                'name': 'robot-sf-market',
                'settings': {
                    'api_url': '$mockserver/external_startrek/v2/',
                    'web_url': 'https://st.test.yandex-team.ru/',
                    'client_kwargs': ['tags', 'comment'],
                },
            },
        ],
    },
)
@pytest.mark.parametrize(
    'error_code, other_fields, message, nested_message',
    [
        (
            'DUPLICATE_REQUEST_KEYS',
            '{"createdBy": "321", "key": "value", "key2": "value2"}',
            'Request key error',
            'Key {\'createdBy\'} must be unique for request body',
        ),
        (
            'INCORRECT_REQUEST_DATA',
            '{ddd}}',
            'Request JSON parsing error',
            'Error while parsing other_fields: {ddd}} is not instance of json',
        ),
    ],
)
async def test_startrek_create_issue_with_incorrect_fields(
        taxi_process_automation_salesforce_esb_web,
        mockserver,
        error_code,
        other_fields,
        message,
        nested_message,
):
    # arrange
    request = {
        'tracker_alias': 'robot-sf-market',
        'queue': '123',
        'summary': '123',
        'description': '123',
        'createdBy': '123',
        'assignee': '123',
        'deadline': '2017-01-01',
        'followers': ['123'],
        'tags': ['123'],
        'other_fields': other_fields,
        'comment': 'test_comment',
    }

    # act
    response = await taxi_process_automation_salesforce_esb_web.post(
        '/v1/external-tracker/issue', data=json.dumps(request),
    )

    # assert
    assert response.status == 400
    assert await response.json() == {
        'code': 'INVALID_REQUEST',
        'details': {
            'errors': [{'code': error_code, 'message': nested_message}],
            'occurred_at': '2022-04-26T15:00:00+03:00',
        },
        'message': message,
    }


@pytest.mark.now('2022-04-26T12:00:00+0000')
@pytest.mark.config(
    PROCESS_AUTOMATION_SALESFORCE_ESB_EXTERNAL_STARTREK_SETTINGS={
        'external_startrek_settings': [
            {
                'name': 'alias-without-secdist',
                'settings': {
                    'api_url': '$mockserver/external_startrek/v2/',
                    'web_url': 'https://st.test.yandex-team.ru/',
                    'client_kwargs': ['tags', 'comment'],
                },
            },
        ],
    },
)
async def test_startrek_create_issue_without_secdist(
        taxi_process_automation_salesforce_esb_web, mockserver, load_json,
):
    # arrange
    request = json.dumps(load_json('requests/no_secdist.json'))

    # act
    response = await taxi_process_automation_salesforce_esb_web.post(
        '/v1/external-tracker/issue', data=request,
    )

    # assert
    assert response.status == 400
    assert await response.json() == load_json('responses/secdist_error.json')
