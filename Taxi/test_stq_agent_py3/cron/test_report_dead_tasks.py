import pytest

from stq_agent_py3.generated.cron import run_cron


@pytest.mark.filldb(stq_dead_tasks='non_empty')
async def test_report_not_lettered_tasks(
        mockserver,
        mock_clownductor,
        # mock_staff,
        mock_sticker,
        stq_db,
        cron_context,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return {
            'hosts': [
                {'queue_name': f'azaza11', 'hosts': ['host1_1', 'host1_2']},
                {'queue_name': f'azaza', 'hosts': ['host2_1', 'host2_2']},
            ],
        }

    # pylint: disable=unused-variable
    @mock_clownductor('/v1/branches/')
    async def _clownductor_branches(request):
        group = request.query['direct_link']
        branch_id, service_id, env = {
            'taxi_prestable_stq': (0, 1, 'env0'),
            'taxi_stq': (1, 2, 'env1'),
        }[group]
        return [
            {
                'id': branch_id,
                'name': f'branch_{group}',
                'service_id': service_id,
                'direct_link': group,
                'env': env,
            },
        ]

    # pylint: disable=unused-variable
    @mock_clownductor('/v1/services/duty_info/')
    async def _clownductor_duty_info(request):
        service_id = request.json['service_id']
        person_on_duty, duty_group_id = {
            1: ('some1', '123'),
            2: ('another1', '234'),
        }[service_id]
        return {
            'duty_group_id': duty_group_id,
            'duty_person_logins': [person_on_duty],
        }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/client-staff/v3/persons')
    async def _staff_persons(request):
        login = request.query['login']
        work_email = {
            'some1': 'some1@yandex-team.ru',
            'another1': 'another1@yandex-team.ru',
        }[login]
        return {'work_email': work_email}

    letters = []

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sticker/send-internal/')
    async def _sticker_send_internal(request):
        letters.append(request.json)
        return {}

    await cron_context.mongo.stq_dead_tasks.update_many(
        {}, {'$currentDate': {'cleaned_at': True}},
    )

    await run_cron.main(['stq_agent_py3.crontasks.report_dead_tasks'])

    tasks_to_letter = await cron_context.mongo.stq_dead_tasks.find(
        {'reported_at': {'$exists': False}},
    ).to_list(None)

    assert not tasks_to_letter

    assert len(letters) == 2

    reports = [
        ('some1@yandex-team.ru', 'task_to_letter_1'),
        ('some1@yandex-team.ru', 'task_to_letter_2'),
        ('another1@yandex-team.ru', 'task_to_letter_3'),
        ('another1@yandex-team.ru', 'task_to_letter_4'),
    ]
    tasks_reported = 0

    for (mail, task) in reports:
        for letter in letters:
            assert 'task_not_to_letter' not in letter['body']
            assert '(total of &lt;b&gt;2&lt;/b&gt; tasks)' in letter['body']
            if letter['send_to'] == mail and task in letter['body']:
                tasks_reported += 1
                break
    assert tasks_reported == 4
