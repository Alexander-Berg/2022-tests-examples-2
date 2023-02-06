import pytest


@pytest.mark.parametrize(
    'order_id, expected_response, link',
    [
        ('00000000000000000000000000000001', 200, '111'),
        ('00000000000000000000000000000002', 409, '222'),
        ('00000000000000000000000000000003', 404, '333'),
        ('00000000000000000000000000000004', 404, '444'),
        ('00000000000000000000000000000005', 200, '555'),
        ('00000000000000000000000000000006', 404, '666'),
    ],
)
@pytest.mark.now('2021-10-12 12:00:00.0000+03')
async def test_v1_prepare_logs_restore_check_correct_request(
        taxi_pricing_admin,
        order_id,
        expected_response,
        link,
        mockserver,
        order_archive_mock,
        load_json,
):
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    @mockserver.json_handler('/logs-from-yt/v1/tasks/')
    def _mock_tasks(request):
        def create_mock_response(response_code):
            if response_code == 409:
                return mockserver.make_response(status=409)
            if response_code == 200:
                return mockserver.make_response(
                    status=200,
                    json={
                        'task_id': '1',
                        'status': 'finished',
                        'author': 'nik-carlson',
                        'created_at': '2021-10-12T18:13:12.576+00:00',
                        'request': request.json,
                    },
                )
            return mockserver.make_response(status=500)

        if order_id == '00000000000000000000000000000002':
            return create_mock_response(409)
        request_json = request.json
        request_filter = request_json['filters'][0]
        assert request_filter['key'] == 'link'
        assert request_filter['value'] == link
        assert request_filter['service_names'][0] == 'pricing-data-preparer'
        assert request_json['start_time'] == '2021-10-12T17:13:12.576+00:00'
        assert request_json['end_time'] == '2021-10-12T19:13:12.576+00:00'
        return create_mock_response(200)

    response = await taxi_pricing_admin.post(
        'v1/prepare_logs_restore',
        json={'order_id': order_id},
        headers={'X-Yandex-Login': 'nik-carlson'},
    )
    if response.status_code != 404:
        assert _mock_tasks.has_calls
    assert response.status_code == expected_response
