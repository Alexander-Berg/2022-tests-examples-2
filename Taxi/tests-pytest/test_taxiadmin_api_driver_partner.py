import json

from django.test import Client
import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.internal import personal


GOOD_REPORT = {'data': 'some good data'}
GOOD_ANSWER = {'report': GOOD_REPORT}


@pytest.mark.parametrize(
    'report',
    [
        'order-payments',
        'payment-orders'
    ]
)
@pytest.mark.parametrize('data,status,content',
    [
        (
            {  # no search params
                'date_from': '2018-01-02',
                'date_to': '2018-01-03'
            },
            400,
            {
                'code': 'general',
                'message':
                    'At least one of "license", "phone", "clid" or "db_id" should be specified',
                'status': 'error'
            }
        ),
        (
            {  # db_id
                'db_id': 'db1',
                'date_from': '2018-01-02',
                'date_to': '2018-01-03'
            },
                200,
                GOOD_ANSWER
        ),
        (
            {  # clid
                'clid': 'clid1',
                'date_from': '2018-01-02',
                'date_to': '2018-01-03'
            },
                200,
                GOOD_ANSWER
        ),
        (
            {  # non-existant clid
                'clid': 'does_not_exist',
                'date_from': '2018-01-02',
                'date_to': '2018-01-03'
            },
            404,
            {
                'code': 'general',
                'message': 'No drivers found',
                'status': 'error'
            }
        ),
        (
            {  # phone and license
                'phone': '+70000000001',
                'license': '001',
                'date_from': '2018-01-02',
                'date_to': '2018-01-03'
            },
                200,
                GOOD_ANSWER
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_report(data, status, content, areq_request, monkeypatch, report, patch):
    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def bulk_store(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_DRIVER_LICENSES
        yield
        async.return_value([{'id': 'pd_id_' + i, 'license': i} for i in request_ids])

    @patch('taxi.internal.driver_manager._get_all_countries')
    @async.inline_callbacks
    def _get_all_countries():
        yield
        async.return_value(
            []
        )

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/find":
            phone = kwargs['json']['value']
            response = {'value': phone, 'id': 'id_' + phone}
            return areq_request.response(200, body=json.dumps(response))
        assert url == 'http://test-host/service/financial-reports/' + report
        if data:
            return areq_request.response(200, body=json.dumps(GOOD_REPORT))
        else:
            return areq_request.response(200)

    monkeypatch.setattr(
        settings, 'DRIVER_PARTNER_API_HOST', 'http://test-host'
    )

    response = Client().post(
        '/api/driver-partner/financial-reports/' + report,
        json.dumps(data),
        'application/json'
    )
    assert response.status_code == status, response.content
    assert json.loads(response.content) == content, 'content is wrong'


@pytest.mark.asyncenv('blocking')
def test_wrong_report_type(areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(200, body=GOOD_REPORT)
    monkeypatch.setattr(
        settings, 'DRIVER_PARTNER_API_HOST', 'http://test-host'
    )

    response = Client().post(
        '/api/driver-partner/financial-reports/wrong-type',
        json.dumps({}),
        'application/json'
    )
    assert response.status_code == 404, response.content
