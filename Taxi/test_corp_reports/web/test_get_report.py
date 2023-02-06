import pytest

_CLIENT = 'client1'
_REPORT_ID = '466a6158ae043734c53bc655e1474339'


async def test_base(web_app_client):
    response = await web_app_client.get(
        '/corp-reports/v1/reports/report',
        params={'client_id': _CLIENT, 'report_id': _REPORT_ID},
    )
    assert response.status == 200
    assert (
        response.headers['Content-Disposition']
        == 'attachment; filename="some_order_report.xlsx"'
    )
    assert (
        response.headers['Content-Type']
        == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    assert (
        response.headers['X-Accel-Redirect'] == '/proxy-mds/get-taxi/5456/9506'
    )


@pytest.mark.parametrize(
    'client_id, report_id',
    [
        pytest.param(_CLIENT, 'foo', id='not existed report id'),
        pytest.param(
            _CLIENT,
            '3334cef306e974e25d38d7d851084333',
            id='report is not ready',
        ),
        pytest.param('foo', _REPORT_ID, id='not existed client'),
    ],
)
async def test_404(client_id, report_id, web_app_client):
    response = await web_app_client.get(
        '/corp-reports/v1/reports/report',
        params={'client_id': client_id, 'report_id': report_id},
    )
    assert response.status == 404
