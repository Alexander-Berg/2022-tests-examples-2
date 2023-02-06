import datetime

import pytest

from chatterbox.internal import supporters_manager as supporters_manager_module
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    ('login', 'expected_result'),
    (
        (
            'user_not_found',
            {
                'in_additional': False,
                'lines': [],
                'login': 'user_not_found',
                'db_status': 'offline',
                'updated': None,
                'languages': [],
                'max_tickets_per_shift': None,
                'shift_start': None,
                'shift_finish': None,
                'in_additional_permitted': True,
                'off_shift_tickets_disabled': False,
            },
        ),
        (
            'user_without_status_and_with_profile',
            {
                'in_additional': False,
                'lines': [],
                'login': 'user_without_status_and_with_profile',
                'db_status': 'offline',
                'updated': None,
                'languages': ['ru'],
                'max_tickets_per_shift': 10,
                'shift_start': datetime.datetime(
                    2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'shift_finish': datetime.datetime(
                    2019, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'in_additional_permitted': False,
                'off_shift_tickets_disabled': True,
            },
        ),
        (
            'user_with_status_and_without_profile',
            {
                'in_additional': True,
                'lines': ['first', 'new'],
                'login': 'user_with_status_and_without_profile',
                'db_status': 'online',
                'updated': datetime.datetime(
                    2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'languages': [],
                'max_tickets_per_shift': None,
                'shift_start': None,
                'shift_finish': None,
                'in_additional_permitted': True,
                'off_shift_tickets_disabled': False,
            },
        ),
        (
            'user_with_status_and_profile',
            {
                'in_additional': False,
                'lines': ['first'],
                'login': 'user_with_status_and_profile',
                'db_status': 'online',
                'updated': datetime.datetime(
                    2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'languages': ['en'],
                'max_tickets_per_shift': None,
                'shift_start': None,
                'shift_finish': None,
                'in_additional_permitted': True,
                'off_shift_tickets_disabled': False,
            },
        ),
    ),
)
async def test_get_supporter_success(
        cbox: conftest.CboxWrap, login: str, expected_result: dict,
):
    supporter = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )
    assert supporter == supporters_manager_module.SupporterState(
        config=cbox.app.config, **expected_result,
    )
