import copy

import pytest

from . import data
from . import util

URI = 'v1/operator'
HEADERS = {'X-WFM-Domain': 'taxi'}


THIRD_OPERATOR = copy.deepcopy(data.THIRD_OPERATOR)
THIRD_OPERATOR['login'] = 'chakchakchak'


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        ({'yandex_uid': 'uid1'}, 200, data.FIRST_OPERATOR),
        ({'yandex_uid': 'no-operator'}, 404, None),
        ({'login': 'abd-damir'}, 200, data.FIRST_OPERATOR),
        ({'login': 'chakchak'}, 200, data.SECOND_OPERATOR),
        ({'login': 'chakchakchak'}, 200, THIRD_OPERATOR),
        ({'login': 'cha'}, 400, None),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees(
        operators_list=[
            {
                'yandex_uid': 'uid1',
                'employee_uid': '00000000-0000-0000-0000-000000000001',
                'login': 'abd-damir',
                'staff_login': 'abd-damir',
                'departments': ['1'],
                'full_name': 'Abdullin Damir',
                'employment_status': 'in_staff',
                'phone_pd_id': '111',
                'supervisor_login': 'aladin227',
                'mentor_login': 'supervisor@unit.test',
                'employment_datetime': '2020-07-21T00:00:00+03:00',
                'positions': ['nokia', 'nokia2'],
                'source': 'taxi',
                'tags': ['naruto'],
            },
            {
                'yandex_uid': 'uid2',
                'employee_uid': '00000000-0000-0000-0000-000000000002',
                'login': 'chakchak',
                'staff_login': 'chakchak',
                'departments': ['2'],
                'full_name': 'Gilgenberg Valeria',
                'employment_status': 'in_staff',
                'supervisor_login': 'abd-damir',
                'created_at': '2020-07-21 00:00:00Z',
                'updated_at': '2020-07-21 00:00:00Z',
                'mentor_login': 'mentor@unit.test',
                'employment_datetime': '2020-07-21T00:00:00+03:00',
                'positions': ['nokia', 'nokia2'],
                'telegram_login_pd_id': 'vasya_iz_derevni',
                'source': 'taxi',
                'tags': ['naruto', 'driver'],
            },
            {
                'yandex_uid': 'uid3',
                'employee_uid': '00000000-0000-0000-0000-000000000003',
                'login': 'chakchakchak',
                'staff_login': 'tatarstan',
                'departments': ['999'],
                'full_name': 'Minihanov Minihanov',
                'employment_status': 'in_staff',
                'supervisor_login': 'abd-damir',
                'created_at': '2020-07-21 00:00:00Z',
                'updated_at': '2020-07-21 00:00:00Z',
                'mentor_login': 'supervisor@unit.test',
                'employment_datetime': '2020-07-21T00:00:00+03:00',
                'positions': ['iphone', 'iphone2'],
                'telegram_login_pd_id': 'morozhenka',
                'source': 'taxi',
            },
        ],
    )
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    res = await taxi_workforce_management_web.get(
        URI, params=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == util.remove_deprecated_fields(
        expected_result, 'rate',
    )
