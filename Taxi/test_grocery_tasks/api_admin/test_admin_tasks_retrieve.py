import datetime

import pytest

from grocery_tasks.api.models import links
from grocery_tasks.crontasks import scheduled_crontasks
from grocery_tasks.utils import cron_links

_NOW = datetime.datetime(2020, 4, 13, 12, 40)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('grocery_tasks', files=['pg_schedule.sql'])
async def test_tasks_retrieve(web_app_client):
    response = await web_app_client.post('/admin/v1/tasks/retrieve')
    assert response.status == 200
    content = await response.json()
    scheduled_tasks_settings = {
        'autoorder-run_calc': {
            'runs': [
                {
                    'cron_link': cron_links.get_cron_link(
                        'autoorder-run_calc', '200',
                    ),
                    'duration': 60,
                    'end_at': '2020-04-14T07:05:00+03:00',
                    'start_at': '2020-04-14T07:04:00+03:00',
                    'status': 'warning',
                },
            ],
            'schedule': {
                'cron_schedule': '3 7 * * *',
                'next_scheduled_run': '2020-04-14T07:03:00+03:00',
                'next_manual_run': '2020-04-15T07:00:00+03:00',
            },
            'task_name': 'autoorder-run_calc',
        },
        'autoorder-run_data_copy': {
            'runs': [
                {
                    'cron_link': cron_links.get_cron_link(
                        'autoorder-run_data_copy', '101',
                    ),
                    'duration': 60,
                    'end_at': '2020-04-14T07:04:00+03:00',
                    'start_at': '2020-04-14T07:03:00+03:00',
                    'status': 'ok',
                },
                {
                    'cron_link': cron_links.get_cron_link(
                        'autoorder-run_data_copy', '100',
                    ),
                    'duration': 86460,
                    'end_at': '2020-04-14T07:04:00+03:00',
                    'report_short': 'abc',
                    'start_at': '2020-04-13T07:03:00+03:00',
                    'status': 'ok',
                },
            ],
            'schedule': {
                'cron_schedule': '3 4 * * *',
                'next_scheduled_run': '2020-04-14T04:03:00+03:00',
            },
            'task_name': 'autoorder-run_data_copy',
        },
        'selloncogs-update_experiment': {
            'runs': [
                {
                    'cron_link': cron_links.get_cron_link(
                        'selloncogs-update_experiment', '300',
                    ),
                    'duration': 60,
                    'end_at': '2020-04-14T07:06:00+03:00',
                    'start_at': '2020-04-14T07:05:00+03:00',
                    'status': 'ok',
                },
            ],
            'schedule': {
                'cron_schedule': '5 7 * * *',
                'next_manual_run': '2020-04-15T07:00:00+03:00',
                'next_scheduled_run': '2020-04-14T07:05:00+03:00',
            },
            'task_name': 'selloncogs-update_experiment',
        },
    }

    tasks_settings = []
    for task_name in sorted(scheduled_crontasks.TASKS.keys()):
        default_settings = {'runs': [], 'schedule': {}, 'task_name': task_name}
        task_settings = scheduled_tasks_settings.get(
            task_name, default_settings,
        )
        task_links = _get_links(task_name)
        if task_links is not None:
            task_settings['links'] = task_links
        tasks_settings.append(task_settings)

    assert content == {'tasks': tasks_settings}


def _get_links(task_name):
    link_objects = links.get_links(task_name)
    if link_objects:
        return [link.serialize() for link in link_objects]
    return link_objects
