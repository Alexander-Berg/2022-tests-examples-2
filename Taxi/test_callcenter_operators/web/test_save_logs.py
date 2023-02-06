import pytest


@pytest.mark.parametrize(
    ['yandex_uid', 'request_body', 'response_status', 'logs_saved'],
    (
        pytest.param(
            'uid',
            {
                'logs': [
                    {'timestamp': '2020-12-12T12:00:00', 'message': 'log 1'},
                    {'timestamp': '2020-12-12T12:00:01', 'message': 'log 2'},
                    {'timestamp': '2020-12-12T12:00:02', 'message': 'log 3'},
                ],
            },
            200,
            True,
        ),
        pytest.param('uid', {'logs': []}, 200, False),
        pytest.param('uid', {}, 200, False),
        pytest.param(
            'uid',
            {'logs': [{'timestamp': 'bad timestamp', 'message': 'bad log'}]},
            400,
            False,
        ),
        pytest.param(
            None,
            {'logs': [{'timestamp': '2020-12-12T12:00:02', 'message': 'log'}]},
            400,
            False,
        ),
        pytest.param(
            'uid',
            {'logs': [{'timestamp': '2020-12-12T12:00:00', 'message': 'log'}]},
            200,
            False,
            marks=pytest.mark.config(CALLCENTER_OPERATORS_SAVE_LOGS=False),
        ),
    ),
)
async def test_save_logs(
        taxi_callcenter_operators_web,
        testpoint,
        yandex_uid,
        request_body,
        response_status,
        logs_saved,
):
    @testpoint('save_logs_testpoint')
    def save_logs_testpoint(data):
        pass

    headers = {'X-Yandex-Login': 'login'}
    if yandex_uid:
        headers['X-Yandex-UID'] = yandex_uid
    response = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/save_logs',
        json=request_body,
        headers=headers,
    )
    assert response.status == response_status
    assert save_logs_testpoint.times_called == int(logs_saved)
