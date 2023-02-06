import datetime

import pytest
import pytz

from taxi.stq import async_worker_ng

from workforce_management.stq import schedule_change_draft


TASK_INFO = async_worker_ng.TaskInfo(
    id='1',
    exec_tries=0,
    reschedule_counter=0,
    queue='workforce_management_schedule_change_audit',
)


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SCHEDULE_AUDIT_SETTINGS={
        'taxi': {
            'startrack_queue': 'some_queue',
            'administrative_tags': ['naruto'],
            'ignore_exceptions': {'schedule_change': True},
        },
    },
)
@pytest.mark.parametrize(
    'kwargs, expected_st_data',
    [
        (
            {
                'draft_type': 'schedule_change',
                'draft_status': 'created',
                'domain': 'taxi',
                'yandex_uid': 'uid1',
                'author_yandex_uid': 'uid1',
                'new_schedule': {
                    'starts_at': datetime.datetime(
                        year=2020, month=9, day=1, tzinfo=pytz.UTC,
                    ),
                    'schedule_type_id': 2,
                    'schedule_offset': 0,
                },
            },
            {
                'author': 'abd-damir',
                'description': (
                    '\n'
                    '    **Сотрудники:**\n'
                    '    Damir Abdullin (abd-damir)\n'
                    '    **Часовой пояс сотрудника**\n'
                    '    Europe/Saratov\n'
                    '    **Дата изменения графика:**\n'
                    '    2020-09-01\n'
                    '    **Текущий график:**\n'
                    '    16-04 / blabla\n'
                    '    **Новый график:**\n'
                    '    14-04 / blablaa\n'
                    '    **Будет работать в праздничные дни:**\n'
                    '    Нет\n'
                    '    **Меняется тарифная ставка:**\n'
                    '    Нет\n'
                    '    **Комментарий:**\n'
                    '    Тикет создан автоматически из WFM Effrat\n'
                    '    '
                ),
                'employees': ['abd-damir'],
                'followers': ['robot-support-taxi', 'robot-agent'],
                'queue': 'some_queue',
                'raiseDate': '2020-09-01',
                'summary': 'Изменение графика Damir Abdullin (abd-damir)',
            },
        ),
        (
            {
                'draft_type': 'schedule_change',
                'draft_status': 'created',
                'domain': 'taxi',
            },
            None,
        ),
    ],
)
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
async def test_schedule_change(
        stq_runner,
        stq3_context,
        patch_aiohttp_session,
        response_mock,
        kwargs,
        expected_st_data,
):
    @patch_aiohttp_session('https://st-api.test.yandex-team.ru/v2/issues')
    def request(*args, json, **kwargs):
        json.pop('unique')
        assert json == expected_st_data
        return response_mock(json={'key': 'asd'})

    await schedule_change_draft.task(
        context=stq3_context, task_info=TASK_INFO, **kwargs,
    )
    assert request.calls if expected_st_data else True


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SCHEDULE_AUDIT_SETTINGS={
        'taxi': {
            'startrack_queue': 'some_queue',
            'administrative_tags': ['naruto'],
        },
    },
)
@pytest.mark.parametrize(
    'kwargs, expected_st_data, expected_comment',
    [
        (
            {
                'draft_type': 'preprofile_new_schedule',
                'draft_status': 'created',
                'domain': 'taxi',
                'yandex_uid': 'uid1',
                'author_yandex_uid': 'uid1',
                'new_schedule': {
                    'starts_at': datetime.datetime(
                        year=2020, month=9, day=1, tzinfo=pytz.UTC,
                    ),
                    'schedule_type_id': 2,
                    'schedule_offset': 0,
                },
            },
            {'tags': {'add': ['wfm_effrat']}},
            {
                'text': (
                    '        **Сотрудник:**\n'
                    '        Damir Abdullin (abd-damir)\n'
                    '        **Часовой пояс сотрудника**\n'
                    '        Europe/Saratov\n'
                    '        **Первый рабочий день:**\n'
                    '        2020-09-01\n'
                    '        **График:**\n'
                    '        14-04 / blablaa\n'
                    '        '
                ),
            },
        ),
        pytest.param(
            {
                'draft_type': 'preprofile_new_schedule',
                'draft_status': 'created',
                'domain': 'taxi',
                'yandex_uid': 'uid10',
                'author_yandex_uid': 'uid10',
                'new_schedule': {
                    'starts_at': datetime.datetime(
                        year=2020, month=9, day=1, tzinfo=pytz.UTC,
                    ),
                    'schedule_type_id': 2,
                    'schedule_offset': 0,
                },
            },
            None,
            None,
            id='empty_ticket_reschedule',
        ),
    ],
)
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
async def test_schedule_preprofile(
        stq,
        stq3_context,
        patch_aiohttp_session,
        response_mock,
        kwargs,
        expected_st_data,
        expected_comment,
):
    request_num = 0

    @patch_aiohttp_session('https://st-api.test.yandex-team.ru/v2/issues')
    def _(*args, json, **kwargs):
        nonlocal request_num
        request_num += 1
        if request_num == 1:
            assert json == expected_st_data
            return response_mock(json={'key': 'asd'})
        if request_num == 2:
            assert json == expected_comment
            return response_mock(json={'key': 'asd'})
        #  actually always assert false, this construction is meant to beat
        #  stupid linter
        assert request_num == 0, 'st requests count more than expected'
        return response_mock(json={'key': 'asd'})

    await schedule_change_draft.task(
        context=stq3_context, task_info=TASK_INFO, **kwargs,
    )
    if not expected_comment:
        queue = stq.workforce_management_schedule_change_draft
        assert queue.next_call()
