from taxi.clients import staff

from taxi_exp import settings
from taxi_exp.util import staff as staff_util

CONVERT_LOGIN_TO_EMAIL = {
    'another_login': {
        'login': 'another_login',
        'work_email': 'work_email@yandex-team.ru',
    },
    'first-login': {
        'login': 'first-login',
        'work_email': 'team-t@yandex-team.ru',
    },
}


async def test_enriment(taxi_exp_client, patch_staff):
    patch_staff.fill(CONVERT_LOGIN_TO_EMAIL)

    staff_client = staff.StaffClient(
        taxi_exp_client.app.session,
        settings.STAFF_API_URL,
        taxi_exp_client.app.tvm,
        retry_intervals=[10, 100],
    )

    data = [
        (
            'another_login',
            [
                {
                    'exp_id': 2,
                    'is_config': False,
                    'name': 'map_view',
                    'prev_rev': 2,
                    'current_rev': 3,
                },
            ],
            'other_data',
        ),
        (
            'first-login',
            [
                {
                    'exp_id': 1,
                    'is_config': False,
                    'name': 'superapp',
                    'prev_rev': 1,
                    'current_rev': 3,
                },
            ],
            'other_data_v2',
        ),
        (
            'unknown-login',
            [
                {
                    'exp_id': 1,
                    'is_config': False,
                    'name': 'superapp',
                    'prev_rev': 1,
                    'current_rev': 3,
                },
            ],
            'other_data_v3',
        ),
    ]
    result = []
    async for (
            watcher_login,
            email,
            other_data_p1,
            other_data_p2,
    ) in staff_util.enrichment(staff_client, data):
        result.append((watcher_login, email, other_data_p1, other_data_p2))
    assert result == [
        (
            'another_login',
            'work_email@yandex-team.ru',
            [
                {
                    'current_rev': 3,
                    'exp_id': 2,
                    'is_config': False,
                    'name': 'map_view',
                    'prev_rev': 2,
                },
            ],
            'other_data',
        ),
        (
            'first-login',
            'team-t@yandex-team.ru',
            [
                {
                    'current_rev': 3,
                    'exp_id': 1,
                    'is_config': False,
                    'name': 'superapp',
                    'prev_rev': 1,
                },
            ],
            'other_data_v2',
        ),
    ]
