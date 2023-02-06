import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files


CONVERT_LOGIN_TO_PHONE = {
    'somebody': 'once_told_me@yandex-team.ru',
    'another_one': 'bites_the_dust@yandex-team.ru',
    'mister_sandman': 'bring_me_a_dream@yandex-team.ru',
    'dismissed_login': 'dismissed_account@yandex-team.ru',
}


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.config(
    EXP3_EXPIRATION_SETTINGS={
        'manual_shutdown_only_extend_settings': {
            'days_left': 5,
            'extend_by': 90,
            'message': (
                'Experiments{group_info} have been extended by 90 days '
                'because they had no more than {days_left} days '
                'of action time left: {experiments}'
            ),
            'subject': 'Expiring experiments have been extended',
            'escalation_level': 2,
        },
    },
    EXP_COPY_EMAILS_FOR_ALERT=['serg-novikov@yandex-team.ru'],
    EXP_BACK_EMAIL_FOR_ALERTS='serg-novikov@yandex-team.ru',
)
async def test_send_alert(
        taxi_exp_client, patch_aiohttp_session, response_mock, mockserver,
):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    async def _update_exp(request):
        response_ = await taxi_exp_client.put(
            '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params={
                'name': request.query.get('name'),
                'last_modified_at': request.query.get('last_modified_at'),
            },
            json=request.json,
        )
        return {'status': response_.status}

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
                            'login': 'somebody',
                            'work_email': 'once_told_me@yandex-team.ru',
                            'official': {'is_dismissed': False},
                            'department_group': {'id': 10},
                        },
                        {
                            'id': 2,
                            'login': 'dismissed_login',
                            'work_email': 'dismissed_account@yandex-team.ru',
                            'official': {'is_dismissed': True},
                            'department_group': {'id': 10},
                        },
                    ],
                    'total': 2,
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
                        'department': {
                            'heads': [{'person': {'login': 'another_one'}}],
                        },
                        'is_deleted': False,
                        'parent': {
                            'department': {
                                'heads': [
                                    {'person': {'login': 'mister_sandman'}},
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

    response = await files.post_file(taxi_exp_client, 'file.txt', b'aaaa')
    assert response.status == 200, await response.text()
    file_id = (await response.json())['id']

    name = 'test_exp'
    test_exp_with_no_namespace = experiment.generate(
        name=name,
        action_time={
            'from': '2019-01-08T12:00:00+03:00',
            'to': '2019-01-10T09:00:00+03:00',
        },
        owners=['somebody', 'dismissed_login'],
        shutdown_mode='manual_shutdown_only',
        match_predicate=(
            experiment.allof_predicate([experiment.infile_predicate(file_id)])
        ),
    )
    test_exp_with_namespace = experiment.generate(
        name=name,
        action_time={
            'from': '2019-01-08T12:00:00+03:00',
            'to': '2019-01-12T09:00:00+03:00',
        },
        owners=['dismissed_login'],
        shutdown_mode='manual_shutdown_only',
    )

    await helpers.init_exp(
        taxi_exp_client, name=name, body=test_exp_with_no_namespace,
    )

    await helpers.init_exp(
        taxi_exp_client,
        name=name,
        namespace='market',
        body=test_exp_with_namespace,
    )

    test_exp_with_namespace.pop('owners')

    await helpers.init_exp(
        taxi_exp_client,
        name=name + '_with_no_owners',
        namespace='market',
        body=test_exp_with_namespace,
    )

    # filling owner_group
    await db.set_owner_group(
        app=taxi_exp_client.app,
        owner='somebody',
        exp_name=name,
        owner_group=10,
    )
    await db.set_owner_group(
        app=taxi_exp_client.app,
        owner='dismissed_login',
        exp_name=name,
        owner_group=10,
    )
    await db.set_owner_group(
        app=taxi_exp_client.app,
        owner='dismissed_login',
        exp_name=name,
        namespace='market',
        owner_group=10,
    )

    # running cron
    await cron_run.main(
        ['taxi_exp.stuff.extend_manual_shutdown_only_experiments', '-t', '0'],
    )
    assert _send_email.calls
    resp = await helpers.get_experiment(taxi_exp_client, name=name)
    assert resp['match']['action_time']['to'] == '2019-04-10T09:00:00+03:00'

    resp = await helpers.get_experiment(
        taxi_exp_client, name=name, namespace='market',
    )
    assert resp['match']['action_time']['to'] == '2019-04-12T09:00:00+03:00'
    assert resp['namespace'] == 'market'

    assert _send_email.data == [
        {
            'send_to': 'bites_the_dust@yandex-team.ru',
            'idempotence_token': (
                '7f939c465e75655d12521c3ecec7dfaa'
                'bbf32fee864950711e59f332b2525b34'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Expiring experiments have been extended (unittests)</subject>'
                '<body>Experiments in your department group '
                'with their owners dismissed/transferred '
                'to another department have been extended '
                'by 90 days because they had no more than 5 days '
                'of action time left: \n\n'
                'User dismissed_login (dismissed) is the owner of the '
                'following experiments: \n\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/test_exp?type=experiments'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'bring_me_a_dream@yandex-team.ru',
            'idempotence_token': (
                '415b68db8fadf53a193bd27115f50088'
                '188810661a333435a6a678f857e04a5c'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Expiring experiments have been extended (unittests)</subject>'
                '<body>Experiments in your department group '
                'with their owners dismissed/transferred '
                'to another department have been extended '
                'by 90 days because they had no more than 5 days '
                'of action time left: \n\n'
                'User dismissed_login (dismissed) is the owner of the '
                'following experiments: \n\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/test_exp?type=experiments'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'once_told_me@yandex-team.ru',
            'idempotence_token': (
                '1a70001639668e1e0398af6704afcd85'
                'decc9eb368dab06ea6367181f33373e5'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'Expiring experiments have been extended (unittests)</subject>'
                '<body>Experiments which you are the owner/watcher of '
                'have been extended by 90 days because they had no more than '
                '5 days of action time left: \n\n'
                'https://tariff-editor.taxi.yandex-team.ru/experiments3'
                '/show/test_exp?type=experiments\n\n'
                '</body></mail></mails>'
            ),
            'copy_send_to': ['serg-novikov@yandex-team.ru'],
        },
        {
            'send_to': 'serg-novikov@yandex-team.ru',
            'idempotence_token': (
                '66119117705c96893bb41f385674770d'
                '5c661096738110be5aea2c188af890df'
            ),
            'body': (
                '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<mails><mail>'
                '<from>serg-novikov@yandex-team.ru</from>'
                '<subject encoding="base64">'
                'ATTENTION Unattended experiments have been extended '
                '(unittests)</subject><body>'
                'Experiments without owners have been extended: \n\n'
                'https://market.tplatform.yandex-team.ru/experiments3'
                '/show/test_exp_with_no_owners?type=experiments'
                '</body></mail></mails>'
            ),
        },
    ]
