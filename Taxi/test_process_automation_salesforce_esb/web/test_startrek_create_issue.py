import json

import pytest


@pytest.mark.config(
    PROCESS_AUTOMATION_SALESFORCE_ESB_INTERNAL_STARTREK_SETTINGS={
        'api_url': '$mockserver/internal_startrek/v2/',
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
)
@pytest.mark.parametrize(
    'other_fields, status',
    [
        ('{"key": "value", "key2": "value2"}', 200),
        ('{"createdBy": "321", "key": "value", "key2": "value2"}', 400),
        ('{ddd}}', 400),
    ],
)
async def test_startrek_create_issue(
        taxi_process_automation_salesforce_esb_web,
        mockserver,
        other_fields,
        status,
):
    @mockserver.json_handler('/internal_startrek/v2/issues')
    async def issues(_request):  # pylint: disable=W0621,W0612
        assert _request.json['createdBy'] == '123'
        assert _request.json['key2'] == 'value2'
        return {'key': 'QUEUE-123'}

    data = {
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
    response = await taxi_process_automation_salesforce_esb_web.post(
        '/v1/startrek/issue', data=json.dumps(data),
    )
    assert response.status == status
    if response.status == 200:
        assert await response.json() == {
            'issue_link': 'https://st.test.yandex-team.ru/QUEUE-123',
        }
