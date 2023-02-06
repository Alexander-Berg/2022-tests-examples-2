import pytest


USER_ID = '9233529b223647959c04fbdd553c7250'
INTERVAL = 86400


@pytest.mark.parametrize('role', ['executer', 'supervisor', 'city_head'])
async def test_load(tap, api, role):
    # pylint: disable=redefined-outer-name,unused-argument
    with tap.plan(4, f'Запрос получения KPI показателей кладовщиков, '
                      f'роль {role}'):
        t = await api(role=role)
        await t.post_ok(
            'api_tsd_user_stats_load',
            json={
                'user_id': USER_ID,
                'interval': INTERVAL
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('stats', [])
        return
