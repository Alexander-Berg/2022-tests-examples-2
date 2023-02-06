import pytest


@pytest.mark.ydb(files=['init_order_proc_user_uid_request_due_index.sql'])
@pytest.mark.parametrize(
    ['request_json', 'expected_response'],
    [
        pytest.param(
            {
                'yandex_uid': 'uid_2',
                'date_upper_bound': '2022-02-25T04:30:00Z',
            },
            {
                'order_infos': [
                    {
                        'id': 'order_id_3',
                        'request_due_or_created': '2022-02-24T04:30:00+00:00',
                    },
                ],
            },
            id='Result contains 1 id',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid_1',
                'date_upper_bound': '2022-02-25T04:30:00Z',
            },
            {
                'order_infos': [
                    {
                        'id': 'order_id_1',
                        'request_due_or_created': '2008-08-08T00:06:00+00:00',
                    },
                    {
                        'id': 'order_id_2',
                        'request_due_or_created': '2014-03-18T04:30:00+00:00',
                    },
                ],
            },
            id='Result contains > 1 id',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid_1',
                'date_upper_bound': '2022-02-25T04:30:00Z',
                'date_lower_bound': '2012-02-25T04:30:00Z',
            },
            {
                'order_infos': [
                    {
                        'id': 'order_id_2',
                        'request_due_or_created': '2014-03-18T04:30:00+00:00',
                    },
                ],
            },
            id='with date_lower_bound',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid_1',
                'date_upper_bound': '2002-02-25T04:30:00Z',
            },
            {'order_infos': []},
            id='Empty result',
        ),
    ],
)
async def test_ok(taxi_order_archive, request_json, expected_response):
    uri = '/v1/order_proc/takeout/find_order_ids_by_uid'
    async with taxi_order_archive.capture_logs() as capture:
        response = await taxi_order_archive.post(uri, json=request_json)

    request_logs = capture.select(_type='request', uri=uri)
    assert len(request_logs) == 1
    assert request_logs[0]['body'] == ''

    response_logs = capture.select(_type='response', uri=uri)
    assert len(response_logs) == 1
    assert response_logs[0]['body'] == ''

    assert response.status_code == 200
    data = response.json()
    assert data == expected_response
