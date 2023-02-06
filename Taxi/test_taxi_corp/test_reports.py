# pylint: disable=redefined-outer-name
import copy
import datetime

import pytest


_NOW = datetime.datetime(2016, 3, 19, 12, 40)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['client_id', 'passport_mock', 'data', 'task_id'],
    [
        pytest.param(
            'client1',
            'client1',
            {
                'service': 'taxi',
                'since_date': '2020-05-01',
                'till_date': '2020-05-31',
            },
            'new_task_id',
            id='new client task',
        ),
        pytest.param(
            'client1',
            'manager1',
            {
                'service': 'taxi',
                'since_date': '2020-05-01',
                'till_date': '2020-05-31',
                'department_id': 'd1',
            },
            'new_task_id',
            id='test manager request with own department',
        ),
        pytest.param(
            'client1',
            'manager1',
            {
                'service': 'taxi',
                'since_date': '2020-05-01',
                'till_date': '2020-05-31',
                'department_id': 'd_1_1',
            },
            'new_task_id',
            id='test manager request with sub department',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'he'])
async def test_orders_report_generate(
        taxi_corp_real_auth_client,
        mockserver,
        client_id,
        passport_mock,
        data,
        task_id,
):
    idempotency_token = '456'

    @mockserver.json_handler('/corp-reports/corp-reports/v1/reports/generate')
    def _v1_reports_generate(request):
        assert request.headers['X-Request-Language'] == 'he'
        assert request.headers['X-Real-IP'] == '127.0.0.1'
        assert request.headers['X-Yandex-Login'] == passport_mock + '_login'
        assert request.headers['X-Yandex-UID'] == passport_mock + '_uid'
        assert request.headers['X-Idempotency-Token'] == idempotency_token
        assert request.query['client_id'] == client_id
        assert request.json == data
        return {'task_id': task_id}

    request_body = copy.deepcopy(data)
    request_body['idempotency_token'] = idempotency_token
    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{client_id}/reports/orders/generate',
        json=request_body,
        headers={'Accept-Language': 'he-IL'},
    )
    assert response.status == 200
    assert (await response.json()) == {'task_id': task_id}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['passport_mock', 'request_body', 'response_body', 'author'],
    [
        pytest.param(
            'client1',
            {'task_id': 'complete_task_id001'},
            {
                'task_id': 'complete_task_id001',
                'status': 'complete',
                'request': {
                    'service': 'taxi',
                    'department_id': 'd1_1',
                    'locale': 'ru',
                    'since': '2020-01-01T03:00:00+03:00',
                    'till': '2020-02-01T03:00:00+03:00',
                },
                'url': '/api/1.0/client/client1/reports/report?report_id=complete_task_id001',  # noqa: W605, E501 # pylint: disable=line-too-long
                'created_at': '2020-02-05T15:34:00+03:00',
            },
            'some_manager',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'en'])
async def test_orders_report_status(
        taxi_corp_real_auth_client,
        mockserver,
        passport_mock,
        request_body,
        response_body,
        author,
):
    @mockserver.json_handler('/corp-reports/corp-reports/v1/reports/status')
    def _v1_reports_status(request):
        assert request.query['client_id'] == passport_mock
        assert request.json == request_body
        return mockserver.make_response(
            json=response_body, headers={'X-Yandex-Login': author},
        )

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{client_id}/reports/status'.format(
            client_id=passport_mock,
        ),
        json=request_body,
    )
    assert response.status == 200
    expected_response = copy.deepcopy(response_body)
    expected_response['author'] = author
    assert (await response.json()) == expected_response


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['passport_mock', 'report_id'],
    [pytest.param('client1', 'complete_task_id000')],
    indirect=['passport_mock'],
)
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'en'])
async def test_orders_report_report(
        taxi_corp_real_auth_client, mockserver, passport_mock, report_id,
):
    report_body = b'<xl>Hello zipped xmls!</xl>'
    content_disposition = 'attachment; filename="Tru.xlsx"'
    content_type = (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    @mockserver.json_handler('/corp-reports/corp-reports/v1/reports/report')
    def _v1_reports_report(request):
        assert request.query['client_id'] == passport_mock
        assert request.query['report_id'] == report_id
        return mockserver.make_response(
            report_body,
            content_type=content_type,
            headers={'Content-Disposition': content_disposition},
        )

    response = await taxi_corp_real_auth_client.get(
        f'/1.0/client/{passport_mock}/reports/report',
        params={'report_id': report_id},
    )
    assert response.status == 200
    assert (await response.read()) == report_body
    assert response.headers['Content-Disposition'] == content_disposition
    assert response.headers['Content-Type'] == content_type
