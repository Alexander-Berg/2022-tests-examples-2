import datetime

import freezegun
import pytest

from support_metrics.generated.cron import run_cron


NOW = '2022-06-13T10:00:00+03:00'


async def _check_result(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM sessions.chatterbox_sessions ORDER BY task_id ASC',
    )
    expected_stat = sorted(
        expected_result, key=lambda x: (x['task_id'], x['opened_ts']),
    )
    assert len(expected_result) == len(result)
    for i, record in enumerate(result):
        assert record['task_id'] == expected_stat[i]['task_id'], dict(record)
        assert record['opened_ts'] == expected_stat[i]['opened_ts']
        assert record['duration'] == expected_stat[i]['duration']
        assert record['line'] == expected_stat[i]['line']
        assert record['login'] == expected_stat[i]['login']


@pytest.mark.config(
    SUPPORT_METRICS_OFFSET_IN_MINUTES_FOR_SESSION_FORMATION=5,
    SUPPORT_METRICS_BORDER_ACTIONS_OF_SESSION={
        'opening_actions': ['create', 'reopen'],
        'closing_actions': ['comment', 'dismiss', 'close'],
    },
    SUPPORT_METRICS_LINES_FOR_WHICH_TO_FORM_SESSIONS=['eda_first'],
)
@pytest.mark.parametrize(
    'expected_result',
    [
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 55, 1, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': None,
                    'line': None,
                    'login': None,
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['filter_actions_by_time.sql'],
            ),
            id='filter_actions_by_time',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': None,
                    'line': None,
                    'login': None,
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['filter_actions_by_line.sql'],
            ),
            id='filter_actions_by_line',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': None,
                    'line': None,
                    'login': None,
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['filter_events_by_type.sql'],
            ),
            id='filter_events_by_type',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 120,
                    'line': 'eda_first',
                    'login': 'operator_1',
                },
                {
                    'task_id': 'task_2',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 120,
                    'line': 'eda_first',
                    'login': 'operator_2',
                },
                {
                    'task_id': 'task_3',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 60,
                    'line': 'eda_first',
                    'login': 'operator_3',
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['filter_actions_by_type.sql'],
            ),
            id='filter_actions_by_type',
        ),
        pytest.param(
            [],
            marks=pytest.mark.pgsql(
                'support_metrics',
                files=['action_without_specified_task_id.sql'],
            ),
            id='action_without_specified_task_id',
        ),
        pytest.param(
            [],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['closing_in_absence_of_opening.sql'],
            ),
            id='closing_in_absence_of_opening',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 57, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': None,
                    'line': None,
                    'login': None,
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['closing_before_opening.sql'],
            ),
            id='closing_before_opening',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 60,
                    'line': 'eda_first',
                    'login': 'operator_1',
                },
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 57, 20, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 40,
                    'line': 'eda_first',
                    'login': 'operator_2',
                },
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 58, 40, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 20,
                    'line': 'eda_first',
                    'login': 'operator_3',
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['more_than_one_session.sql'],
            ),
            id='more_than_one_session',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 120,
                    'line': 'eda_first',
                    'login': 'operator',
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['two_actions_in_row.sql'],
            ),
            id='two_actions_in_row',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 54, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 120,
                    'line': 'eda_first',
                    'login': 'operator_1',
                },
                {
                    'task_id': 'task_2',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 54, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 180,
                    'line': 'eda_first',
                    'login': 'operator_2',
                },
                {
                    'task_id': 'task_3',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 54, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': None,
                    'line': None,
                    'login': None,
                },
                {
                    'task_id': 'task_4',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 55, 30, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 30,
                    'line': 'eda_first',
                    'login': 'operator_3',
                },
                {
                    'task_id': 'task_4',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 57, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 60,
                    'line': 'eda_first',
                    'login': 'operator_3',
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics',
                files=['opened_session_in_sessions_table.sql'],
            ),
            id='opened_session_in_sessions_table',
        ),
        pytest.param(
            [
                {
                    'task_id': 'task_1',
                    'opened_ts': datetime.datetime(
                        2022, 6, 13, 6, 56, tzinfo=datetime.timezone.utc,
                    ),
                    'duration': 60,
                    'line': 'eda_first',
                    'login': 'operator',
                },
            ],
            marks=pytest.mark.pgsql(
                'support_metrics', files=['already_existed_same_session.sql'],
            ),
            id='already_existed_same_session',
        ),
    ],
)
async def test_update_sessions(cron_context, expected_result):
    with freezegun.freeze_time(NOW):
        await run_cron.main(
            ['support_metrics.crontasks.update_sessions', '-t', '0'],
        )

    db = cron_context.postgresql.support_metrics[0]
    await _check_result(db, expected_result)
