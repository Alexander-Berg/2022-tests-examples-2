import json
import pytest

from taxi.core import arequests
from taxi.external import geotracks


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('params,status_code,exception', [
    (
        {
            'driver_id': 'test_driver_id',
            'db': 'test_db',
            'from': 'test_start_time',
            'to': 'test_end_time'
        }, 200, None
    ),
    (
        {
            'driver_id': 'test_driver_id',
            'db': 'test_db',
            'from': 'test_start_time',
            'to': 'test_end_time'
        }, 200, True
    ),
])
@pytest.inline_callbacks
def test_get_driver_track(params, status_code, exception,
                          areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        if exception is None:
            return areq_request.response(200, body=json.dumps({'a': 123}))
        else:
            raise arequests.RequestError("ERROR")
    if exception is None:
        response = yield geotracks.get_driver_track(
            params['driver_id'], params['db'], params['from'], params['to'],
            '')
        assert response == {'a': 123}
    else:
        with pytest.raises(geotracks.GeotracksRequestError):
            yield geotracks.get_driver_track(
                params['driver_id'], params['db'], params['from'],
                params['to'], ''
            )
