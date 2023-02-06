import datetime

import pytest

from taxi import staff_util


from taxi_api_admin.generated.cron import run_cron


@pytest.mark.now('2020-06-10T20:00:00')
async def test_del_users_in_cron(api_admin_cron_app, db, patch, mongodb):
    @patch('taxi.clients.idm.IdmApiClient._request')
    async def _request(url, method, params, **kwargs):
        data = {}
        if 'api/v1/roles/' in url:
            user = params['user']
            if user != 'test_login_4':
                update = {'$set': {'admin_superuser': False}}
                query = {'yandex_team_login': user}
                result = mongodb.staff.update(query, update)
                assert result['ok']
            data = {
                'errors': 1,
                'errors_ids': [
                    {
                        'id': 9220419,
                        'message': 'Роль находится в состоянии Отозвана',
                    },
                ],
                'successes': 1,
                'successes_ids': [{'id': 19062346}],
            }
        return data

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _create_ticket(*args, **kwargs):
        return {'key': f'{args[1]}-100'}

    await run_cron.main(
        ['taxi_api_admin.cron.temporary_superusers', '-t', '0'],
    )
    users = await staff_util.get_superusers(db)
    assert users == [
        {
            '_id': 'id_1',
            'admin_superuser': True,
            'yandex_team_login': 'test_login_1',
        },
        {
            '_id': 'id_4',
            'admin_superuser': True,
            'start_superuser': datetime.datetime(2020, 6, 10, 18, 10),
            'end_superuser': datetime.datetime(2020, 6, 10, 20, 10),
            'yandex_team_login': 'test_login_4',
            'audit_st_ticket': 'TAXISUPERUSER-100',
            'updated': datetime.datetime(2020, 6, 10, 20, 0),
        },
    ]
    assert len(_request.calls) == 2
