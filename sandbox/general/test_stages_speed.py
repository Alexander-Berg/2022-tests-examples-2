# coding: utf8
import logging
import datetime
import requests

from sandbox.projects.common.gencfg import solomon


SANDBOX_API_URL = 'http://sandbox.yandex-team.ru/api/v1.0/'


def get_sandbox_tasks_list(task_type):
    return requests.get(
        SANDBOX_API_URL + 'task'
        '?limit=2000'
        '&order=-id'
        '&children=true'
        '&type={}'.format(task_type)
    ).json().get('items', [])


def get_times_from_info(info_data):
    stages = {}
    for i, line in enumerate(info_data.split('\n')):
        line = line.strip()

        if '[TIME]' not in line:
            continue

        if 'failed' in line:
            continue

        try:
            line = line.replace('<div class="hr">', '').replace('</div>[TIME]', '')
            datastamp, timestamp, stage, work_time = line.split(' ')
            year, month, day = map(int, datastamp.split('-'))
            hour, minute, second = map(int, timestamp.split(':'))
            date = datetime.datetime(year, month, day, hour, minute, second)
            stages[stage] = (date, float(work_time))
        except Exception as e:
            logging.info('{}: {}; {}'.format(type(e).__name__, e, line))

    return stages


def get_stages_info_tasks(task_type):
    tasks_stages_info = []
    for task in get_sandbox_tasks_list(task_type):
        if task['results']['info'] and 'prepare_gencfg_paths' in task['results']['info']:
            info = {
                'id': task['id'],
                'stages': get_times_from_info(task['results']['info'])
            }
            tasks_stages_info.append(info)
    return tasks_stages_info


def get_time_distribution(tasks_stages_time):
    stages = {}
    for info in tasks_stages_time:
        for stage_name, stage_data in info['stages'].items():
            if stage_name not in stages:
                stages[stage_name] = []
            stages[stage_name].append(stage_data)

    for stage_name, stage_distribution in stages.items():
        stages[stage_name] = sorted(stages[stage_name], key=lambda x: x[0])

    return stages


def update_speed_test_stages_chart(days_count):
    client = solomon.SolomonClient(project='gencfg', cluster='monitoring', service='health')

    tasks_stages_time = get_stages_info_tasks('TEST_CONFIG_GENERATOR_2')
    logging.info('Tasks: {}'.format(len(tasks_stages_time)))

    stages_time_distribution = get_time_distribution(tasks_stages_time)
    logging.info('Stages: {}'.format(len(stages_time_distribution)))

    for stage_name, stage_distribution in stages_time_distribution.items():
        for date_time, work_time in stage_distribution:
            if (datetime.datetime.now() - date_time).days >= days_count:
                continue
            client.add_sensor('work_time_{}'.format(stage_name), work_time, date_time)
        if len(client.sensors_collected) > 100:
            client.flush()
    client.flush()
    logging.info('success with work_time_*!')
