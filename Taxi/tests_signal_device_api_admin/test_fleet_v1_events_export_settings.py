import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/events/export/settings'
URL_TEMPLATE = (
    'https://fleet.yandex-team.ru/signalq/stream/{}/{}?grouping={}&park_id={}'
)


@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            {'max_depth_days': 10, 'url_template': URL_TEMPLATE},
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_EVENTS_EXPORT_SETTINGS_V3={
                    'max_depth_days': 10,
                    'url_template': URL_TEMPLATE,
                },
            ),
        ),
        pytest.param(
            {'max_depth_days': 32, 'url_template': URL_TEMPLATE},
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_EVENTS_EXPORT_SETTINGS_V3={
                    'max_depth_days': 32,
                    'url_template': URL_TEMPLATE,
                },
            ),
        ),
    ],
)
async def test_v1_events_export_settings(
        taxi_signal_device_api_admin, expected_response,
):
    headers = {**web_common.YA_TEAM_HEADERS}

    response1 = await taxi_signal_device_api_admin.get(
        ENDPOINT, headers=headers,
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == expected_response
