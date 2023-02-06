import pytest


async def test_configs(
        taxi_driver_support_client,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
):
    response = await taxi_driver_support_client.get(
        '/v1/support_chat/config',
        headers={'Authorization': 'driver_with_new_taximeter_session'},
        params={'db': '59de5222293145d09d31cd1604f8f656'},
    )

    assert response.status == 200
    assert await response.json() == (
        {
            'update_timeout': 60000,
            'allow_upload_files': True,
            'allowed_file_mime_types': ['image/png', 'image/jpeg'],
            'picture_preview': {'width': 150, 'height': 200},
            'reopen_reasons': ['problem_not_solved'],
        }
    )


async def test_failed_get_configs(taxi_driver_support_client):
    response = await taxi_driver_support_client.get(
        '/v1/support_chat/config',
        headers={'Authorization': 'some_driver_session'},
    )
    assert response.status == 400
    assert await response.json() == {'errors': [{'db': 'Required field'}]}


@pytest.mark.parametrize(
    'authorization, expected_upload_files',
    [
        ('driver_with_new_taximeter_session', True),
        ('driver_with_old_taximeter_session', False),
    ],
)
async def test_configs_upload_file(
        taxi_driver_support_client,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
        authorization,
        expected_upload_files,
):
    response = await taxi_driver_support_client.get(
        '/v1/support_chat/config',
        headers={'Authorization': authorization},
        params={'db': '59de5222293145d09d31cd1604f8f656'},
    )

    assert response.status == 200
    result = await response.json()
    assert result['allow_upload_files'] == expected_upload_files


# This test for new endpoints behind dap
async def test_configs_new(
        taxi_driver_support_client, mock_driver_profiles, mock_personal,
):
    response = await taxi_driver_support_client.get(
        '/driver/v1/driver-support/v1/support_chat/config',
        headers={
            'X-YaTaxi-Park-Id': '59de5222293145d09d31cd1604f8f656',
            'X-YaTaxi-Driver-Profile-Id': 'driver_with_new_taximeter_uuid',
        },
    )

    assert response.status == 200
    assert await response.json() == (
        {
            'update_timeout': 60000,
            'allow_upload_files': True,
            'allowed_file_mime_types': ['image/png', 'image/jpeg'],
            'picture_preview': {'width': 150, 'height': 200},
            'reopen_reasons': ['problem_not_solved'],
        }
    )


@pytest.mark.parametrize(
    'headers, expected_upload_files',
    [
        (
            {
                'X-YaTaxi-Park-Id': '59de5222293145d09d31cd1604f8f656',
                'X-YaTaxi-Driver-Profile-Id': 'driver_with_new_taximeter_uuid',
            },
            True,
        ),
        (
            {
                'X-YaTaxi-Park-Id': '59de5222293145d09d31cd1604f8f656',
                'X-YaTaxi-Driver-Profile-Id': 'driver_with_old_taximeter_uuid',
            },
            False,
        ),
    ],
)
async def test_configs_upload_file_new(
        taxi_driver_support_client,
        headers,
        expected_upload_files,
        mock_driver_profiles,
        mock_personal,
):
    response = await taxi_driver_support_client.get(
        '/driver/v1/driver-support/v1/support_chat/config', headers=headers,
    )

    assert response.status == 200
    result = await response.json()
    assert result['allow_upload_files'] == expected_upload_files
