import pytest


@pytest.mark.parametrize(
    [
        'handler_identifier',
        'request_body_json',
        'request_query_parameters',
        'expected_response_code',
        'expected_response',
    ],
    [
        (
            'phones',
            {'id': '2bddf24967bb4a35ac18b8b6b3d48275'},
            {'source': 'testing'},
            200,
            'expected_response_phones1.json',
        ),
        ('phones', {'id': '12345'}, {'source': 'testing'}, 404, None),
        (
            'driver_licenses',
            {'id': '24f87daa40994792a7057d4808c3a8c5'},
            {'source': 'testing'},
            200,
            'expected_response_driver_licenses1.json',
        ),
        ('driver_licenses', {'id': '12345'}, {'source': 'testing'}, 404, None),
        (
            'orders',
            {},
            {'id': 'e8fd4b44babe3f0a87e79eb7842ce521'},
            200,
            'expected_response_orders1.json',
        ),
        ('orders', {}, {'id': '12345'}, 404, None),
        (
            'profiles',
            {'phone': '+70123456789'},
            {},
            200,
            'expected_response_profiles1.json',
        ),
        ('profiles', {'phone': '+79999999999'}, {}, 404, None),
        (
            'antifraud_flags',
            {
                'driver_license_personal_id': (
                    '24f87daa40994792a7057d4808c3a8c5'
                ),
                'order_id': 'e8fd4b44babe3f0a87e79eb7842ce521',
            },
            {},
            200,
            'expected_response_antifraud_flags1.json',
        ),
        ('antifraud_flags', {'order_id': '12345'}, {}, 404, None),
        (
            'antifraud_flags',
            {'driver_license_personal_id': '24f87daa40994792a7057d4808c3a8c5'},
            {},
            200,
            'expected_response_antifraud_flags2.json',
        ),
        (
            'antifraud_flags',
            {'driver_license_personal_id': '12345'},
            {},
            404,
            None,
        ),
    ],
)
async def test_handler(
        web_app_client,
        load_json,
        handler_identifier,
        request_body_json,
        request_query_parameters,
        expected_response_code,
        expected_response,
        taxi_config,
):
    url = f'/cc/v1/callcenter-exams/v1/support_form_mock/{handler_identifier}/'
    response = await web_app_client.post(
        url, json=request_body_json, params=request_query_parameters,
    )
    assert response.status == expected_response_code
    if expected_response_code == 200:
        response_json = await response.json()
        expected_json = load_json(expected_response)
        assert response_json == expected_json
