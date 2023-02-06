import pytest

ENDPOINT = '/dashboard/v1/widget/active-drivers'


@pytest.mark.parametrize(
    ['grouped', 'summary', 'expected'],
    [
        pytest.param(
            'grouped.json', 'summary.json', 'expected.json', id='with_data',
        ),
    ],
)
async def test_success(
        web_app_client,
        headers,
        mockserver,
        load_json,
        grouped,
        summary,
        expected,
):
    @mockserver.json_handler(
        'driver-orders-metrics/v1/parks/orders/metrics-by-intervals',
    )
    def _mock_order_core(request):
        assert request.method == 'POST'
        if request.query['type'] == 'hourly':
            res = grouped
        else:
            res = summary
        response_and_code = load_json(res)
        return mockserver.make_response(
            json=response_and_code['body'],
            status=response_and_code['status_code'],
        )

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        json={
            'date_from': '2021-11-26T00:00:00+03:00',
            'date_to': '2021-11-27T00:00:00+03:00',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == load_json(expected)
