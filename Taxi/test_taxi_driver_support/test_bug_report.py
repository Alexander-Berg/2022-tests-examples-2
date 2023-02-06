import pytest


@pytest.mark.config(STARTRACK_CUSTOM_FIELDS_MAP={'driver-support': {}})
@pytest.mark.parametrize(
    'data, expected_status',
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'Claim test\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            400,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "app_version": "1.1",
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            400,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="request_id"\r\n\r\n'
            '123123123\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'My claim description\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "app_version": "1.1",
                "device_model": "iPhone 11"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            200,
        ),
    ],
)
@pytest.mark.parametrize(
    'session_header_name', ['X-Driver-Session', 'Authorization'],
)
@pytest.mark.parametrize('db_parameter', ['db', 'park_id'])
async def test_body_bug_report(
        taxi_driver_support_client,
        mock_st_create_ticket,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
        data,
        expected_status,
        session_header_name,
        db_parameter,
):

    response = await taxi_driver_support_client.post(
        '/v1/bug_reports',
        data=data,
        headers={
            session_header_name: 'some_driver_session',
            'User-Agent': 'taximeter-beta 9.10 (123)',
            'Content-type': (
                'multipart/form-data; '
                'boundary=f329de09cd544a86a5cf95375c2e0438'
            ),
        },
        params={db_parameter: '59de5222293145d09d31cd1604f8f656'},
    )
    assert response.status == expected_status


@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP={
        'driver-support': {
            'taximeter_version': 'taximeterVersion',
            'device_model': 'deviceModel',
            'park_db_id': 'parkDbId',
            'driver_uuid': 'driverUuid',
            'city': 'city',
        },
    },
)
@pytest.mark.parametrize(
    'multipart_data, expected_create_ticket, expected_attach_files',
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="request_id"\r\n\r\n'
            '123123123\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'My claim description\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "device_model": "iPhone 11"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'queue': 'TAXIMETERBUGS',
                'summary': (
                    'Баг-репорт. Версия приложения 9.10 (123). '
                    'Модель устройства iPhone 11'
                ),
                'description': 'My claim description',
                'unique': '123123123',
                'tags': ['bug_report', 'taximeter_bug'],
                'custom_fields': {
                    'deviceModel': 'iPhone 11',
                    'taximeterVersion': '9.10 (123)',
                    'driverUuid': 'some_driver_uuid',
                    'parkDbId': '59de5222293145d09d31cd1604f8f656',
                    'city': '',
                },
            },
            [],
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="request_id"\r\n\r\n'
            '123123123\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'My claim description\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "device_model": "iPhone 11"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="attachment"; '
            'filename="gmail_1.jpg"\r\n'
            'Content-Type: image/jpeg\r\n\r\n'
            'Attachment_1 binary data\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="attachment"; '
            'filename="gmail_2.jpg"\r\n'
            'Content-Type: image/jpeg\r\n\r\n'
            'Attachment_2 binary data\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'queue': 'TAXIMETERBUGS',
                'summary': (
                    'Баг-репорт. Версия приложения 9.10 (123). '
                    'Модель устройства iPhone 11'
                ),
                'description': 'My claim description',
                'unique': '123123123',
                'tags': ['bug_report', 'taximeter_bug'],
                'custom_fields': {
                    'deviceModel': 'iPhone 11',
                    'taximeterVersion': '9.10 (123)',
                    'driverUuid': 'some_driver_uuid',
                    'parkDbId': '59de5222293145d09d31cd1604f8f656',
                    'city': '',
                },
            },
            [
                {
                    'ticket_id': 'TAXIMETERBUGS-1',
                    'filename': 'gmail_1.jpg',
                    'file_data': b'Attachment_1 binary data',
                },
                {
                    'ticket_id': 'TAXIMETERBUGS-1',
                    'filename': 'gmail_2.jpg',
                    'file_data': b'Attachment_2 binary data',
                },
            ],
        ),
    ],
)
async def test_create_ticket(
        taxi_driver_support_client,
        mock_driver_session,
        mock_st_create_ticket,
        mock_st_attach_file,
        mock_driver_profiles,
        mock_personal,
        multipart_data,
        expected_create_ticket,
        expected_attach_files,
):
    response = await taxi_driver_support_client.post(
        '/v1/bug_reports',
        data=multipart_data,
        headers={
            'Authorization': 'some_driver_session',
            'User-Agent': 'taximeter-beta 9.10 (123)',
            'Content-type': (
                'multipart/form-data; '
                'boundary=f329de09cd544a86a5cf95375c2e0438'
            ),
        },
        params={'db': '59de5222293145d09d31cd1604f8f656'},
    )
    assert response.status == 200

    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == expected_create_ticket

    if expected_attach_files:
        calls = mock_st_attach_file.calls
        for i, _ in enumerate(calls):
            attach_files_kwargs = calls[i]['kwargs']
            del attach_files_kwargs['log_extra']
            assert attach_files_kwargs == expected_attach_files[i]


# This test for new endpoints behind dap
@pytest.mark.config(STARTRACK_CUSTOM_FIELDS_MAP={'driver-support': {}})
@pytest.mark.parametrize(
    'data, expected_status',
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'Claim test\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            400,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "app_version": "1.1",
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            400,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="request_id"\r\n\r\n'
            '123123123\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'My claim description\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "app_version": "1.1",
                "device_model": "iPhone 11"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            200,
        ),
    ],
)
async def test_body_bug_report_new(
        taxi_driver_support_client,
        mock_st_create_ticket,
        mock_driver_profiles,
        mock_personal,
        data,
        expected_status,
):

    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/bug_reports',
        data=data,
        headers={
            'X-YaTaxi-Park-Id': '59de5222293145d09d31cd1604f8f656',
            'X-YaTaxi-Driver-Profile-Id': 'some_driver_uuid',
            'User-Agent': 'taximeter-beta 9.10 (123)',
            'Content-type': (
                'multipart/form-data; '
                'boundary=f329de09cd544a86a5cf95375c2e0438'
            ),
        },
    )
    assert response.status == expected_status


@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP={
        'driver-support': {
            'taximeter_version': 'taximeterVersion',
            'device_model': 'deviceModel',
            'park_db_id': 'parkDbId',
            'driver_uuid': 'driverUuid',
            'city': 'city',
        },
    },
)
@pytest.mark.parametrize(
    'multipart_data, expected_create_ticket, expected_attach_files',
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="request_id"\r\n\r\n'
            '123123123\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'My claim description\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "device_model": "iPhone 11"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'queue': 'TAXIMETERBUGS',
                'summary': (
                    'Баг-репорт. Версия приложения 9.10 (123). '
                    'Модель устройства iPhone 11'
                ),
                'description': 'My claim description',
                'unique': '123123123',
                'tags': ['bug_report', 'taximeter_bug'],
                'custom_fields': {
                    'deviceModel': 'iPhone 11',
                    'taximeterVersion': '9.10 (123)',
                    'driverUuid': 'some_driver_uuid',
                    'parkDbId': '59de5222293145d09d31cd1604f8f656',
                    'city': '',
                },
            },
            [],
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="request_id"\r\n\r\n'
            '123123123\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="claim"\r\n\r\n'
            'My claim description\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="meta_info"\r\n\r\n'
            """
            {
                "device_model": "iPhone 11"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="attachment"; '
            'filename="gmail_1.jpg"\r\n'
            'Content-Type: image/jpeg\r\n\r\n'
            'Attachment_1 binary data\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="attachment"; '
            'filename="gmail_2.jpg"\r\n'
            'Content-Type: image/jpeg\r\n\r\n'
            'Attachment_2 binary data\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'queue': 'TAXIMETERBUGS',
                'summary': (
                    'Баг-репорт. Версия приложения 9.10 (123). '
                    'Модель устройства iPhone 11'
                ),
                'description': 'My claim description',
                'unique': '123123123',
                'tags': ['bug_report', 'taximeter_bug'],
                'custom_fields': {
                    'deviceModel': 'iPhone 11',
                    'taximeterVersion': '9.10 (123)',
                    'driverUuid': 'some_driver_uuid',
                    'parkDbId': '59de5222293145d09d31cd1604f8f656',
                    'city': '',
                },
            },
            [
                {
                    'ticket_id': 'TAXIMETERBUGS-1',
                    'filename': 'gmail_1.jpg',
                    'file_data': b'Attachment_1 binary data',
                },
                {
                    'ticket_id': 'TAXIMETERBUGS-1',
                    'filename': 'gmail_2.jpg',
                    'file_data': b'Attachment_2 binary data',
                },
            ],
        ),
    ],
)
async def test_create_ticket_new(
        taxi_driver_support_client,
        mock_st_create_ticket,
        mock_st_attach_file,
        mock_driver_profiles,
        mock_personal,
        multipart_data,
        expected_create_ticket,
        expected_attach_files,
):
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/bug_reports',
        data=multipart_data,
        headers={
            'X-YaTaxi-Park-Id': '59de5222293145d09d31cd1604f8f656',
            'X-YaTaxi-Driver-Profile-Id': 'some_driver_uuid',
            'User-Agent': 'taximeter-beta 9.10 (123)',
            'Content-type': (
                'multipart/form-data; '
                'boundary=f329de09cd544a86a5cf95375c2e0438'
            ),
        },
    )
    assert response.status == 200

    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == expected_create_ticket

    if expected_attach_files:
        calls = mock_st_attach_file.calls
        for i, _ in enumerate(calls):
            attach_files_kwargs = calls[i]['kwargs']
            del attach_files_kwargs['log_extra']
            assert attach_files_kwargs == expected_attach_files[i]
