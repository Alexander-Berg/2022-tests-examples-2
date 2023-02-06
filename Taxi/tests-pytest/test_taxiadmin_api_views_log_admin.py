import json

from django import test as django_test
import pytest


@pytest.mark.parametrize('request_data,expected', [
    (
        {'exclude': ['action_1', 'action_3']},
        [{
            'action': 'action_2',
            'id': '000000000000000000000002',
            'login': 'malenko',
            'timestamp': '2018-11-01T21:00:00+0300',
            'arguments': {}
        }]
    ),
    (
        {'object_id': 'test_id'},
        [{
            'action': 'action_3',
            'id': '000000000000000000000004',
            'login': 'malenko',
            'timestamp': '2018-02-01T00:04:00+0300',
            'arguments': {},
            'object_id': 'test_id'
        }]
    ),
])
@pytest.mark.asyncenv('blocking')
def test_audit_actions(request_data, expected):
    response = django_test.Client().post(
        '/api/audit/actions/',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert json.loads(response.content) == expected
