import datetime

import pytest
import pytz


async def test_happy_path(
        mocked_time,
        check_unprocessed_docs,
        register_billing_tasks,
        approve_billing_tasks,
):
    """
        Check registered tasks returning.
    """
    now = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.utc)
    mocked_time.set(now)

    await register_billing_tasks()
    approve_billing_tasks()

    await check_unprocessed_docs(
        expected=[
            {
                'billing_doc_id': '1',
                'billing_request_time': '2020-12-31T00:00:00+00:00',
                'operation_id': '12445',
                'history_event_id': 1,
            },
        ],
        full=True,
    )


@pytest.mark.parametrize(
    'approved_instant_age',
    [datetime.timedelta(hours=721), datetime.timedelta(hours=1)],
)
async def test_out_of_range(
        mocked_time,
        check_unprocessed_docs,
        register_billing_tasks,
        approve_billing_tasks,
        approved_instant_age,
):
    """
        Check registered tasks returning.
    """
    now = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.utc)
    mocked_time.set(now)

    await register_billing_tasks()
    approve_billing_tasks(approve_instant=now - approved_instant_age)

    # no documents in [outdated, delay]
    await check_unprocessed_docs(expected=[])
