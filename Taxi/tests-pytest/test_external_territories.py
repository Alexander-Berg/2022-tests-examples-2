import json
import pytest

from taxi.conf import settings
from taxi.external import territories


@pytest.mark.disable_territories_api_mock
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('status_code', [200, 400, 404, 406, 500])
@pytest.inline_callbacks
def test_get_all_countries(status_code, areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert kwargs['headers']['YaTaxi-Api-Key'] == 'secret'
        if status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps({'countries': [{'_id': 'rus'}]})
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'TERRITORIES_API_TOKEN', 'secret')
    try:
        countries = yield territories.get_all_countries(
            retries=5,
            retry_interval=0,
        )
        assert status_code == 200
        assert len(requests_request.calls) == 1
        assert countries == [{'_id': 'rus'}]
    except territories.BadRequestError:
        assert len(requests_request.calls) == 1
        assert status_code == 400
    except territories.NotFoundError:
        assert len(requests_request.calls) == 1
        assert status_code == 404
    except territories.RequestRetriesExceeded:
        assert len(requests_request.calls) == 5
