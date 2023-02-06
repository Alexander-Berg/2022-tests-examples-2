import datetime

import pytest


from taxi_api_admin.generated.cron import run_cron


@pytest.mark.now('2020-06-10T20:00:00')
async def test_sender_audit_actions_cron(
        api_admin_cron_app, db, patch, mockserver,
):
    @patch('taxi.clients.audit.AuditClient.retrieve_logs')
    # pylint: disable=unused-variable
    async def retrieve_logs(*args, **kwargs):
        logs = [
            {
                'login': 'user',
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'arguments': {},
                'action': 'action_id_1',
                'id': 'log_id_1',
            },
            {
                'login': 'user',
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'arguments': {},
                'action': 'action_id_2',
                'id': 'log_id_2',
            },
        ]
        return logs

    @mockserver.json_handler('/startrack_reports/v2/create_comments/')
    # pylint: disable=unused-variable
    async def patch_reports_comments(request):
        data = request.json
        assert request.headers.get('Accept-Language') == 'ru'
        data_tickets = data.pop('tickets')
        keys, summonees = [], []
        for ticket in data_tickets:
            keys.append(ticket['key'])
            summonees.extend(ticket.get('summonees', []))
        assert all(key in ['TAXISUPERUSER-300'] for key in keys)
        assert all(
            summonee in ['test_login', 'test_manager']
            for summonee in summonees
        )
        if data['action'] == 'taxi-api-admin:link_to_journal':
            assert data == {
                'action': 'taxi-api-admin:link_to_journal',
                'audit_action_id': '',
                'data': {},
                'template_kwargs': {
                    'url': '/audit',
                    'date_from': '2020-06-10',
                    'date_from_time': '20:00:00',
                    'date_till': '2020-06-10',
                    'date_till_time': '22:00:00',
                    'login': 'test_login_3',
                },
            }
        elif data['action'] == 'taxi-api-admin:table_audit_actions':
            assert data == {
                'action': 'taxi-api-admin:table_audit_actions',
                'audit_action_id': '',
                'data': {},
                'template_kwargs': {
                    'text': (
                        '#|\n'
                        '|| Время| Аудит действие| Ссылка на аудит лог||'
                        '|| 10.06.2020 20:00:00| action_id_1| '
                        '((/audit/log_id_1 Аудит лог))||'
                        '|| 10.06.2020 20:00:00| action_id_2|'
                        ' ((/audit/log_id_2 Аудит лог))|||#'
                    ),
                },
            }
        elif data['action'] == 'taxi-api-admin:unset_superuser':
            assert data == {
                'action': 'taxi-api-admin:unset_superuser',
                'audit_action_id': '',
                'data': {},
                'template_kwargs': {'date': '10.06.2020 22:00:00'},
            }
        else:
            assert data == {}

    @patch('taxi.clients.startrack.StartrackAPIClient.execute_transition')
    async def _execute_transition(*args, **kwargs):
        return {}

    await run_cron.main(
        ['taxi_api_admin.cron.sender_audit_actions', '-t', '0'],
    )
    users = await db.staff.find().to_list(None)
    assert users == [
        {
            '_id': 'id_1',
            'admin_superuser': True,
            'yandex_team_login': 'test_login_1',
            'audit_st_ticket': 'TAXISUPERUSER-100',
            'end_superuser': datetime.datetime(2020, 6, 10, 22, 0),
            'start_superuser': datetime.datetime(2020, 6, 10, 18, 0),
        },
        {
            '_id': 'id_2',
            'admin_superuser': True,
            'end_superuser': datetime.datetime(2020, 6, 10, 20, 12),
            'yandex_team_login': 'test_login_2',
            'audit_st_ticket': 'TAXISUPERUSER-200',
            'start_superuser': datetime.datetime(2020, 6, 10, 18, 0),
        },
        {
            '_id': 'id_3',
            'admin_superuser': False,
            'end_superuser': datetime.datetime(2020, 6, 10, 19, 0),
            'yandex_team_login': 'test_login_3',
            'start_superuser': datetime.datetime(2020, 6, 10, 17, 0),
            'updated': datetime.datetime(2020, 6, 10, 20, 0),
        },
    ]
