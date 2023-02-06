import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run

CONVERT_LOGIN_TO_PHONE = {
    'regular_employee': 'work_email@yandex-team.ru',
    'dismissed_person_a': 'person_a@yandex-team.ru',
    'rotated_person_b': 'person_b@yandex-team.ru',
    'group_head': 'group_head@yandex-team.ru',
    'parent_group_head': 'parent_group_head@yandex-team.ru',
    'dismissed_person_c': 'person_c@yandex-team.ru',
}


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', files=['owners_and_experiments.sql'])
@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.config(
    EXP3_EXPIRATION_SETTINGS={
        'alert_settings': [
            {
                'days_left': 2,
                'message': (
                    'Experiments{group_info} are expiring in 2 days: '
                    '{experiments}'
                ),
                'escalation_level': 2,
            },
        ],
    },
    EXP_COPY_EMAILS_FOR_ALERT=['serg-novikov@yandex-team.ru'],
    EXP_BACK_EMAIL_FOR_ALERTS='serg-novikov@yandex-team.ru',
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'send_alert_by_expiration_v2': True,
                'send_alert_by_expiration_v2_lost_experiments': True,
            },
        },
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
async def test_send_alert(
        taxi_exp_client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(f'{settings.STAFF_API_URL}/v3/persons')
    def _email_from_staff(*args, **kwargs):
        assert 'params' in kwargs
        if 'department_group.id' in kwargs['params']['_fields']:
            return response_mock(
                json={
                    'links': {},
                    'page': 1,
                    'limit': 50,
                    'result': [
                        {
                            'id': 1,
                            'login': 'regular_employee',
                            'work_email': 'work_email@yandex-team.ru',
                            'official': {'is_dismissed': False},
                            'department_group': {'id': 10},
                        },
                        {
                            'id': 2,
                            'login': 'dismissed_person_a',
                            'work_email': 'person_a@yandex-team.ru',
                            'official': {'is_dismissed': True},
                            'department_group': {'id': 10},
                        },
                        {
                            'id': 3,
                            'login': 'rotated_person_b',
                            'work_email': 'person_b@yandex-team.ru',
                            'official': {'is_dismissed': False},
                            'department_group': {'id': 20},
                        },
                        {
                            'id': 4,
                            'login': 'dismissed_person_c',
                            'work_email': 'person_c@yandex-team.ru',
                            'official': {'is_dismissed': True},
                            'department_group': {'id': 20},
                        },
                        {
                            'id': 5,
                            'login': 'group_head',
                            'work_email': 'group_head@yandex-team.ru',
                            'official': {'is_dismissed': False},
                            'department_group': {'id': 10},
                        },
                    ],
                    'total': 5,
                    'pages': 1,
                },
            )
        if 'work_email' in kwargs['params']['_fields']:
            logins = kwargs['params']['login'].split(',')
            return response_mock(
                json={
                    'page': 1,
                    'pages': 1,
                    'result': [
                        {
                            'work_email': (CONVERT_LOGIN_TO_PHONE[login]),
                            'login': login,
                            'id': index,
                        }
                        for index, login in enumerate(logins)
                    ],
                },
            )
        return response_mock(
            json={
                'links': {},
                'page': 1,
                'limit': 50,
                'result': [
                    {
                        'id': 10,
                        'is_deleted': False,
                        'department': {
                            'heads': [{'person': {'login': 'group_head'}}],
                        },
                        'parent': {
                            'department': {
                                'heads': [
                                    {'person': {'login': 'parent_group_head'}},
                                ],
                            },
                        },
                    },
                    {
                        'id': 20,
                        'is_deleted': True,
                        'department': {
                            'heads': [{'person': {'login': 'placeholder'}}],
                        },
                        'parent': {
                            'department': {
                                'heads': [
                                    {
                                        'person': {
                                            'login': 'second_placeholder',
                                        },
                                    },
                                ],
                            },
                        },
                    },
                ],
                'total': 2,
                'pages': 1,
            },
        )

    @patch_aiohttp_session(f'{settings.STICKER_API_URL}/send-internal/')
    def _send_email(method, url, headers, **kwargs):
        if not hasattr(_send_email, 'data'):
            _send_email.data = [kwargs['json']]
        else:
            _send_email.data.append(kwargs['json'])
        return response_mock(text='{}')

    # running cron
    await cron_run.main(
        ['taxi_exp.stuff.send_alert_by_expiration_experiments', '-t', '0'],
    )
    assert _send_email.calls
    assert _send_email.data == [
        {
            'send_to': 'group_head@yandex-team.ru',
            'idempotence_token': (
                '3d3e1785aacab11896c09857e486208f'
                '58561287e05eab8c724542fa7570605a'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Experiments are expiring in 2 days (unittests)</subject>'
                '<body>Experiments which you are the owner/watcher of '
                'are expiring in 2 days: \n\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/market_exp_with_owner?type=experiments\n\n'
                'Experiments in your department group with their owners '
                'dismissed/transferred to another department '
                'are expiring in 2 days: \n\n'
                'User dismissed_person_a (dismissed) is the owner of the '
                'following experiments: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_owned_by_dismissed_person_a?type=experiments\n\n'
                'User rotated_person_b (transferred) is the owner of the '
                'following experiments: \n\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/exp_owned_by_rotated_person_b?type=experiments\n\n'
                'Users dismissed_person_a (dismissed),'
                'rotated_person_b (transferred) are the owners of the '
                'following experiments: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_owned_by_person_a_and_person_b?type=experiments'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'parent_group_head@yandex-team.ru',
            'idempotence_token': (
                '1fd44949af0a62687a8d6dc67c5c1b8e'
                '0f5f7f73bbfabeb58077dff39bb77493'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Experiments are expiring in 2 days (unittests)</subject>'
                '<body>Experiments in your department group with their owners '
                'dismissed/transferred to another department '
                'are expiring in 2 days: \n\n'
                'User dismissed_person_a (dismissed) is the owner of the '
                'following experiments: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_owned_by_dismissed_person_a?type=experiments\n\n'
                'User rotated_person_b (transferred) is the owner of the '
                'following experiments: \n\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/exp_owned_by_rotated_person_b?type=experiments\n\n'
                'Users dismissed_person_a (dismissed),'
                'rotated_person_b (transferred) are the owners of the '
                'following experiments: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_owned_by_person_a_and_person_b?type=experiments'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'work_email@yandex-team.ru',
            'idempotence_token': (
                '19a508d3bc64808c4ebe76fbfa6e9d31'
                '1a6ba413b7ac2db227db382dfe27651d'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Experiments are expiring in 2 days (unittests)</subject>'
                '<body>Experiments which you are the owner/watcher of '
                'are expiring in 2 days: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_with_owner?type=experiments\n\n'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'person_b@yandex-team.ru',
            'idempotence_token': (
                '90876a2208745472b49026b5173ba239'
                '005be92080963119d194325650add8ba'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Experiments are expiring in 2 days (unittests)</subject>'
                '<body>Experiments which you are the owner/watcher of '
                'are expiring in 2 days: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_owned_by_person_a_and_person_b?type=experiments\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/exp_owned_by_rotated_person_b?type=experiments\n\n'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'serg-novikov@yandex-team.ru',
            'idempotence_token': (
                'c6920138dc77035c0a88f96539a62e2b'
                'b90efb602a1bff70b8eb79dc674d50d5'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'ATTENTION Unattended experiments are expiring '
                '(unittests)</subject>'
                '<body>Experiments without owners are expiring in 2 days: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_with_dismissed_owner_and_deleted_group?'
                'type=experiments\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/exp_with_no_owners?type=experiments'
                '</body></mail></mails>'
            ),
        },
    ]
