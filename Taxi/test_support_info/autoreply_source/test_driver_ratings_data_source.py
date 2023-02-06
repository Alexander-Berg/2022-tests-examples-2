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
                'ratings': [
                    {
                        'data': {
                            'rating': 5.0,
                            'rating_count': 5,
                            'total': 5.0,
                        },
                        'revision': '0_1571814254_612',
                        'unique_driver_id': '5d8cc4e8b8e3f879682682ae',
                    },
                ],
            },
            {
                'ratings': {'rating': 5.0, 'rating_count': 5, 'total': 5.0},
                'rating': 5.0,
                'rating_count': 5,
            },
        ),
    ),
)
async def test_driver_ratings_data_source(
        support_info_app: app.SupportInfoApplication,
        patch_aiohttp_session,
        response_mock,
        patch_get_driver_ratings: Callable,
        unique_driver_id: str,
        mock_data: dict,
        expected_result: dict,
):
    patch_get_driver_ratings(unique_driver_id, mock_data)

    order_source = autoreply_source.DriverRatingsDataSource(
        driver_ratings_client=support_info_app.driver_ratings_client,
        config=support_info_app.config,
    )

    result = await order_source.get_data(
        {'unique_driver_id': unique_driver_id},
    )

    assert result == expected_result
