import datetime

import pytest

from taxi import discovery

from support_info import app
from support_info.internal import autoreply_source


@pytest.mark.parametrize(
    (
        'driver_license_personal_id',
        'order_date',
        'mock_data',
        'expected_result',
    ),
    (
        pytest.param(
            'driver_license_personal_id',
            '2019-02-04',
            {'status': 'sgovor'},
            {'antifraud_orders_feedback': 'sgovor'},
            marks=[
                pytest.mark.now(
                    datetime.datetime(2019, 2, 4, 12, 15).isoformat(),
                ),
            ],
        ),
    ),
)
async def test_antifraud_data_source(
        support_info_app: app.SupportInfoApplication,
        patch_aiohttp_session,
        response_mock,
        driver_license_personal_id: str,
        order_date: str,
        mock_data: dict,
        expected_result: dict,
):
    antifraud = discovery.find_service('antifraud-py').url

    @patch_aiohttp_session(
        antifraud + '/v1/get_autoreply_status_for_driver', 'GET',
    )
    def get_antifraud(method, url, **kwargs):
        assert kwargs['params'] == {
            'driver_license_personal_id': driver_license_personal_id,
            'date': order_date,
        }
        return response_mock(json=mock_data)

    antifraud_source = autoreply_source.AntifraudDataSource(
        antifraud_client=support_info_app.antifraud_client,
        config=support_info_app.config,
    )

    result = await antifraud_source.get_data(
        {
            'driver_license_personal_id': driver_license_personal_id,
            'order_date_ymd': order_date,
        },
    )

    assert result == expected_result
    assert len(get_antifraud.calls) == 1
