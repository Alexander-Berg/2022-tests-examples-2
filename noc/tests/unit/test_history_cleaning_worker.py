import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta


from workers.history_cleaning_worker import select_ids_to_keep_in_history

HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=30, hours=12)
NOW = datetime.now()

RECENT_ROTATION_ID = 100000
DEFAULT_INSTANCE = "default"


def generate_rotation_history(hours=200 * 24):
    full_rotation_history = []

    for i in range(1, hours):
        full_rotation_history.append({"rotation_id": RECENT_ROTATION_ID - i, "created_at": str(NOW - HOUR * i)})

    return full_rotation_history


@pytest.mark.parametrize(
    "hours",
    [
        # > than half a year
        365 * 24,
        # a month
        30 * 24 + 12,
        # a week
        7 * 24 + 1,
        # < than a a day
        4,
        # Empty history
        0,
    ],
)
@patch("workers.history_cleaning_worker.collect_rotation_history", new_callable=Mock)
def test_select_correct_rotation_ids(mock_collect_rotation_history, hours):
    time_format = "%Y-%m-%d %H:%M:%S.%f"
    generated_history = generate_rotation_history(hours)

    daily_ids = set()
    weekly_ids = set()
    monthly_ids = set()
    six_months_ids = set()
    yealy_ids = set()

    for rotation_history_data in generated_history:

        if NOW - datetime.strptime(rotation_history_data["created_at"], time_format) <= DAY:
            daily_ids.add(rotation_history_data["rotation_id"])
        elif NOW - datetime.strptime(rotation_history_data["created_at"], time_format) <= WEEK:
            weekly_ids.add(rotation_history_data["rotation_id"])
        elif NOW - datetime.strptime(rotation_history_data["created_at"], time_format) < MONTH:
            monthly_ids.add(rotation_history_data["rotation_id"])
        elif NOW - datetime.strptime(rotation_history_data["created_at"], time_format) <= MONTH * 6 + DAY:
            six_months_ids.add(rotation_history_data["rotation_id"])
        else:
            yealy_ids.add(rotation_history_data["rotation_id"])

    mock_collect_rotation_history.return_value = generated_history

    ids_to_keep = select_ids_to_keep_in_history(DEFAULT_INSTANCE)
    _ids_to_keep = set(ids_to_keep)

    assert len(ids_to_keep) == len(_ids_to_keep)

    # keep full daily history
    assert _ids_to_keep & daily_ids == daily_ids
    # keep one id per week day (except first day)
    if weekly_ids:
        assert len(_ids_to_keep & weekly_ids) == 6
    # keep one id a week during the first month (except first week)
    if monthly_ids:
        assert len(_ids_to_keep & monthly_ids) == 3
    if six_months_ids:
        # keep one id per month during first 6 month (except first month)
        assert len(_ids_to_keep & six_months_ids) == 5
    if yealy_ids:
        # keep no id after 6 months
        assert len(_ids_to_keep & yealy_ids) == 0
