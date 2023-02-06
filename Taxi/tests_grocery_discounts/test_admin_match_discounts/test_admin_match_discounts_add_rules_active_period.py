from datetime import datetime
from datetime import timezone
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common


def _create_check_request(load_json, start_time: Optional[str], end_time: str):
    request = load_json('request.json')
    active_period = {'end': end_time}
    if start_time:
        active_period['start'] = start_time
    request['active_period'] = active_period
    return request


def _create_approval_request(response_json):
    print(response_json)
    return response_json['data']


@pytest.mark.config(GROCERY_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=300)
@pytest.mark.parametrize(
    'start_time, end_time, check_time, check_error, approval_time, approval_error',
    (
        pytest.param(
            '2020-12-31T00:00:00+00:00',
            '2021-01-01T00:00:00+00:00',
            datetime(2020, 12, 30, 19, tzinfo=timezone.utc),
            None,
            datetime(2020, 12, 30, 20, tzinfo=timezone.utc),
            None,
            id='ok_with_start_time',
        ),
        pytest.param(
            None,
            '2021-01-01T00:00:00+00:00',
            datetime(2020, 12, 30, 20, tzinfo=timezone.utc),
            None,
            datetime(2020, 12, 30, 23, tzinfo=timezone.utc),
            None,
            id='ok_without_start_time',
        ),
        pytest.param(
            '2021-01-02T00:00:00+00:00',
            '2021-01-01T00:00:00+00:00',
            datetime(2020, 12, 30, 20, tzinfo=timezone.utc),
            common.StartsWith(
                'Exception in AnyOtherConditionsVectorFromGenerated',
            ),
            None,
            None,
            id='fail_start_more_end',
        ),
        pytest.param(
            '2020-12-31T00:00:00+00:00',
            '2021-01-02T00:00:00+00:00',
            datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
            common.StartsWith('Time in the past'),
            None,
            None,
            id='fail_check_time_more_start',
        ),
        pytest.param(
            '2020-12-31T00:00:00+00:00',
            '2021-01-02T00:00:00+00:00',
            datetime(2020, 12, 30, 20, tzinfo=timezone.utc),
            None,
            datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
            common.StartsWith('Time in the past'),
            id='fail_approval_time_more_start',
        ),
        pytest.param(
            None,
            '2021-01-01T00:00:00+00:00',
            datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
            common.StartsWith(
                'Exception in AnyOtherConditionsVectorFromGenerated',
            ),
            None,
            None,
            id='fail_check_start_more_end',
        ),
        pytest.param(
            None,
            '2021-01-01T00:00:00+00:00',
            datetime(2020, 12, 30, 20, tzinfo=timezone.utc),
            None,
            datetime(2021, 1, 1, 12, tzinfo=timezone.utc),
            common.StartsWith(
                'Exception in AnyOtherConditionsVectorFromGenerated',
            ),
            id='fail_approval_start_more_end',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
async def test_admin_match_discounts_add_rules_active_period(
        client,
        mocked_time,
        load_json,
        start_time: Optional[str],
        end_time: str,
        check_time: datetime,
        check_error,
        approval_time: Optional[datetime],
        approval_error,
):
    # check draft add-rules
    mocked_time.set(check_time)
    response = await client.post(
        '/v3/admin/match-discounts/add-rules/check',
        headers=common.get_headers(),
        json=_create_check_request(load_json, start_time, end_time),
    )

    if check_error:
        assert response.status == 400
        assert response.json()['message'] == check_error
        return
    else:
        assert response.status == 200

    # approval draft add-rules
    mocked_time.set(approval_time)
    response = await client.post(
        '/v3/admin/match-discounts/add-rules',
        headers=common.get_draft_headers(),
        json=_create_approval_request(response.json()),
    )

    if approval_error:
        assert response.status == 400
        assert response.json()['message'] == approval_error
    else:
        assert response.status == 200
