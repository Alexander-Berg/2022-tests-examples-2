import pytest


@pytest.mark.parametrize(
    'data, expected_status, expected_stq_args',
    [
        (
            {
                'db': '59de5222293145d09d31cd1604f8f656',
                'request_id': '123456',
                'driver_signal': 'Harry',
                'subject': 'ZOMG!',
                'tags': ['some', 'tags'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
            },
            200,
            (
                'some_driver_uuid',
                {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_signal': 'Harry',
                    'subject': 'ZOMG!',
                    'tags': ['some', 'tags'],
                    'app_version': '1.0',
                    'device_model': 'iPhone X',
                    'activity': 0.5,
                    'rating': 5.0,
                    'request_id': '123456',
                    'driver_loyal_status': None,
                },
            ),
        ),
        (
            {
                'db': '59de5222293145d09d31cd1604f8f656',
                'request_id': '123456',
                'driver_signal': 'Harry',
                'subject': 'ZOMG!',
                'tags': ['some', 'tags'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
                'driver_loyal_status': 'some_status',
            },
            200,
            (
                'some_driver_uuid',
                {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_signal': 'Harry',
                    'subject': 'ZOMG!',
                    'tags': ['some', 'tags'],
                    'app_version': '1.0',
                    'device_model': 'iPhone X',
                    'activity': 0.5,
                    'rating': 5.0,
                    'request_id': '123456',
                    'driver_loyal_status': 'some_status',
                },
            ),
        ),
    ],
)
async def test_callback_request(
        taxi_driver_support_client,
        mock_stq_put,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
        data,
        expected_status,
        expected_stq_args,
):
    response = await taxi_driver_support_client.post(
        '/v1/callback_request',
        json=data,
        headers={'Authorization': 'some_driver_session'},
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    stq_put_call = mock_stq_put.calls[0]
    assert stq_put_call['args'] == expected_stq_args


# This test for new endpoints behind dap
@pytest.mark.parametrize(
    'data, expected_status, expected_stq_args',
    [
        (
            {
                'request_id': '123456',
                'driver_signal': 'Harry',
                'subject': 'ZOMG!',
                'tags': ['some', 'tags'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
            },
            200,
            (
                'some_driver_uuid',
                {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_signal': 'Harry',
                    'subject': 'ZOMG!',
                    'tags': ['some', 'tags'],
                    'app_version': '1.0',
                    'device_model': 'iPhone X',
                    'activity': 0.5,
                    'rating': 5.0,
                    'request_id': '123456',
                    'driver_loyal_status': None,
                },
            ),
        ),
        (
            {
                'request_id': '123456',
                'driver_signal': 'Harry',
                'subject': 'ZOMG!',
                'tags': ['some', 'tags'],
                'app_version': '1.0',
                'device_model': 'iPhone X',
                'activity': 0.5,
                'rating': 5.0,
                'driver_loyal_status': 'some_status',
            },
            200,
            (
                'some_driver_uuid',
                {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_signal': 'Harry',
                    'subject': 'ZOMG!',
                    'tags': ['some', 'tags'],
                    'app_version': '1.0',
                    'device_model': 'iPhone X',
                    'activity': 0.5,
                    'rating': 5.0,
                    'request_id': '123456',
                    'driver_loyal_status': 'some_status',
                },
            ),
        ),
    ],
)
async def test_callback_request_new(
        taxi_driver_support_client,
        mock_stq_put,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
        data,
        expected_status,
        expected_stq_args,
):
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/callback_request',
        json=data,
        headers={
            'X-YaTaxi-Park-Id': '59de5222293145d09d31cd1604f8f656',
            'X-YaTaxi-Driver-Profile-Id': 'some_driver_uuid',
        },
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    stq_put_call = mock_stq_put.calls[0]
    assert stq_put_call['args'] == expected_stq_args
