import pytest


URI = 'v1/operators/preprofiles/values'
HEADERS = {'X-WFM-Domain': 'taxi', 'X-Yandex-UID': 'uid1'}
PREPROFILE = {
    'callcenter_id': '1',
    'employment_date': '2020-07-21',
    'full_name': 'Kazimir Malevich',
    'login': 'kazimir_black_square',
    'mentor_login': 'admin@unit.test',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'role_in_telephony': 'artist',
    'roles': [],
    'schedules': [],
    'skills': [],
    'state': 'preprofile_approved',
    'supervisor': {
        'full_name': 'Minihanov Minihanov',
        'login': 'tatarstan',
        'state': 'ready',
        'yandex_uid': 'uid3',
    },
    'supervisor_login': 'tatarstan',
    'telegram': 'alphabet',
    'yandex_uid': 'uid10',
}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PREPROFILE_ACCESS_SETTINGS={
        'default': {},
        'taxi': {'super_users_uids': ['uid3']},
    },
)
@pytest.mark.parametrize(
    'tst_request, tst_uid, expected_status, expected_result',
    [
        pytest.param(
            {'limit': 10, 'offset': 0, 'parent_state': 'preprofile'},
            'uid1',
            200,
            {'preprofiles': [PREPROFILE], 'full_count': 1},
            id='one_preprofile',
        ),
        pytest.param(
            {'limit': 10, 'offset': 0, 'states': ['preprofile_approved']},
            'uid1',
            200,
            {'preprofiles': [PREPROFILE], 'full_count': 1},
            id='one_preprofile',
        ),
        pytest.param(
            {'limit': 10, 'offset': 0, 'states': ['preprofile_cancelled']},
            'uid1',
            200,
            {'preprofiles': [], 'full_count': 0},
            id='no_preprofile',
        ),
        pytest.param(
            {'limit': 10, 'offset': 0, 'parent_state': 'preprofile'},
            'uid2',
            200,
            {'preprofiles': [], 'full_count': 0},
            id='no_preprofiles_for_provided_user',
        ),
        pytest.param(
            {'limit': 10, 'offset': 0, 'states': ['preprofile_approved']},
            'uid3',
            200,
            {'preprofiles': [PREPROFILE], 'full_count': 1},
            id='super_user',
        ),
    ],
)
async def test_v1_preprofiles_values_base(
        taxi_workforce_management_web,
        tst_request,
        tst_uid,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers={**HEADERS, 'X-Yandex-UID': tst_uid},
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_result
