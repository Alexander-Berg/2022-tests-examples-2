import json

from django.test import Client
import pytest

from taxi.conf import settings


@pytest.mark.parametrize('method,data',
    [
        (Client().get, None),
        (Client().post, {'test': 'test'}),
        (Client().put, {'test': 'test'}),
        (Client().delete, None),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_list(method, data, areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert url == 'http://test-host/monitoring-areas/test1/test2/'
        request_data = kwargs.get('data')
        if data:
            return areq_request.response(200, body=request_data)
        else:
            return areq_request.response(200)

    monkeypatch.setattr(
        settings, 'TAXI_GEOFENCE_HOST', 'http://test-host'
    )
    if data:
        response = method(
            '/api/geofence/monitoring-areas/test1/test2/',
            json.dumps(data),
            'application/json'
        )
        assert json.loads(response.content) == data
    else:
        response = method('/api/geofence/monitoring-areas/test1/test2/')
        assert response.status_code == 200
