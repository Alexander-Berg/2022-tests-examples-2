import datetime
from typing import Callable

import pytest

from support_info import app
from support_info.internal import autoreply_source


@pytest.mark.parametrize(
    ('unique_driver_id', 'mock_data', 'expected_result'),
    (
        (
            'unique_driver_id',
            {
                'unique_driver_id': 'unique_driver_id',
                'block_till': None,
                'block_time': None,
                'created': datetime.datetime(2019, 9, 25, 12, 57, 19, 813000),
                'last_online': datetime.datetime(2019, 10, 7, 14, 49, 58),
                'last_status_time': datetime.datetime(2019, 10, 7, 14, 49, 58),
                'remaining_time': 598,
                'tired_status': 'not_tired',
                'updated': datetime.datetime(2019, 10, 7, 14, 51, 59, 242000),
                'working_time': 10470,
                'working_time_no_rest': 602,
            },
            {
                'tired_status': 'not_tired',
                'working_time_no_rest': 602,
                'working_time': 10470,
            },
        ),
    ),
)
async def test_driver_weariness_data_source(
        support_info_app: app.SupportInfoApplication,
        patch_aiohttp_session,
        response_mock,
        patch_get_driver_weariness: Callable,
        unique_driver_id: str,
        mock_data: dict,
        expected_result: dict,
):
    patch_get_driver_weariness(unique_driver_id, expected_result)

    order_source = autoreply_source.DriverWearinessDataSource(
        driver_weariness_client=support_info_app.driver_weariness_client,
        config=support_info_app.config,
    )

    result = await order_source.get_data(
        {'unique_driver_id': unique_driver_id},
    )

    assert result == expected_result
