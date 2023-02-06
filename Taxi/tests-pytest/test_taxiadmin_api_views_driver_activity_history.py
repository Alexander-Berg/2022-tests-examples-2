import json

from django import test as django_test
import pytest


@pytest.mark.asyncenv('blocking')
def test_activity_history_simple(areq_request):
    request = {
        'db': '1235456',
        'uuid': '654321',
        'newer_than': '2018-10-23T16:02:48.221000Z',
        'limit': 1,
    }
    correct_response = {
        'activity': [
            {
                'item': {
                    'result': {
                        'comment': 'Cancelled',
                        'value': '-14'
                    },
                    'time': 300,
                    'distance': 1000,
                    'order_id': '123456789',
                    'code': 'REQUESTCAR_CANCELLED_FIELD'
                },
                'date': '2018-10-23T16:02:48.221000Z'
            }
        ],
        'last_items': True
    }

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == (
            'http://driver-protocol.taxi.tst.yandex.net'
            '/driver/activity_history'
        )
        assert kwargs['json'] == request

        return areq_request.response(
            200,
            json.dumps(correct_response),
            headers={
                'Content-Type': 'application/json'
            }
        )

    client = django_test.Client()
    response = client.post(
        '/api/driver_activity_history/',
        json.dumps(request),
        'application/json'
    )
    assert response.status_code == 200
    assert len(requests_request.calls) == 1
    data = json.loads(response.content)
    assert data == correct_response
