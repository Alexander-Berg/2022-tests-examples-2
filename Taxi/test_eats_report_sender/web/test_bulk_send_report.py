import pytest


@pytest.mark.parametrize(
    'request_name, status_code, stq_has_calls',
    [
        ('default', 200, True),
        ('empty_client_ids', 400, False),
        ('without_date', 400, False),
    ],
)
async def test_requests(
        request_name,
        status_code,
        stq_has_calls,
        stq,
        web_app_client,
        load_json,
):
    response = await web_app_client.post(
        '/v1/accountant-reports/bulk-send',
        json=load_json('request.json')[request_name],
    )
    assert response.status == status_code
    assert (
        stq.eats_report_sender_send_accountant_reports.has_calls
        == stq_has_calls
    )
