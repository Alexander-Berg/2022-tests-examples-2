from typing import Optional

import bson
import pytest


HANDLE_URL = '/internal/tips/v1/get-current-tips-sum'


@pytest.mark.parametrize(
    [
        'order',
        'archive_status_code',
        'expected_status_code',
        'expected_tips_sum',
    ],
    [
        ({'payment_tech': {'sum_to_pay': {'tips': 10}}}, 200, 200, 10),
        ({}, 404, 404, None),
        ({}, 500, 500, None),
    ],
)
async def test_get_tips_sum_from_archive(
        taxi_tips,
        mockserver,
        order: dict,
        archive_status_code: int,
        expected_status_code: int,
        expected_tips_sum: Optional[int],
):
    @mockserver.json_handler('archive-api/archive/order')
    def _archive_order(_):
        if archive_status_code == 200:
            return mockserver.make_response(
                bson.BSON.encode({'doc': order}), archive_status_code,
            )
        return mockserver.make_response(json={}, status=archive_status_code)

    response = await taxi_tips.post(
        HANDLE_URL, json={'order_id': 'some_order_id'},
    )
    assert response.status_code == expected_status_code
    assert response.json().get('current_tips_sum') == expected_tips_sum
