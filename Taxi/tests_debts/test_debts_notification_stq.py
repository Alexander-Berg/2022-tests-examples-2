import datetime

import pytest

NOW = datetime.datetime(2022, 5, 18, 17, 5, 1, 104308)


# pylint: disable=invalid-name
def make_debts_notifications_settings(
        custom_intervals=None, repeat_interval=None,
):
    if custom_intervals is None:
        custom_intervals = []

    schedule = {'custom_intervals': custom_intervals}
    if repeat_interval is not None:
        schedule['repeat_interval'] = repeat_interval

    return dict(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='taxi_debts_notifications_settings',
        consumers=['taxi_debts/stq'],
        clauses=[
            {
                'value': {
                    'enabled': True,
                    'schedule': schedule,
                    'texts': {
                        'title': 'some_title_key',
                        'subtitle': 'some_subtitle_key',
                    },
                },
                'predicate': {
                    'init': {'predicates': [{'type': 'true'}]},
                    'type': 'all_of',
                },
            },
        ],
    )


async def test_debts_notification_no_config_no_call(
        stq, stq_runner, mock_ucommunications_push, mock_archive_order,
):
    ucommunications_mock = mock_ucommunications_push()
    archive_order_mock = mock_archive_order()

    await stq_runner.taxi_debts_notifications.call(
        task_id='order_id_1-1', args=('order_id_1', 0, True),
    )
    assert ucommunications_mock.times_called == 0
    assert archive_order_mock.times_called == 0

    assert not stq.taxi_debts_notifications.has_calls


@pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=True)
async def test_debts_notification_no_debts_no_call(
        stq, stq_runner, mock_ucommunications_push, mock_archive_order,
):
    ucommunications_mock = mock_ucommunications_push()
    archive_order_mock = mock_archive_order()

    await stq_runner.taxi_debts_notifications.call(
        task_id='order_id_1-1', args=('order_id_1', 0, True),
    )
    assert ucommunications_mock.times_called == 0
    assert archive_order_mock.times_called == 0

    assert not stq.taxi_debts_notifications.has_calls


@pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=True)
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_debts_notification_no_settings_no_call(
        stq, stq_runner, mock_ucommunications_push, mock_archive_order,
):
    ucommunications_mock = mock_ucommunications_push()
    archive_order_mock = mock_archive_order()

    await stq_runner.taxi_debts_notifications.call(
        task_id='order_id_1-1', args=('order_id_1', 0, True),
    )
    assert ucommunications_mock.times_called == 0
    assert archive_order_mock.times_called == 1

    assert not stq.taxi_debts_notifications.has_calls


@pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=True)
@pytest.mark.experiments3(
    **make_debts_notifications_settings(custom_intervals=[10]),
)
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_debts_notification_no_l10n_no_call(
        stq, stq_runner, mock_ucommunications_push, mock_archive_order,
):
    ucommunications_mock = mock_ucommunications_push()
    archive_order_mock = mock_archive_order()

    await stq_runner.taxi_debts_notifications.call(
        task_id='order_id_1-1', args=('order_id_1', 0, True),
    )
    assert ucommunications_mock.times_called == 0
    assert archive_order_mock.times_called == 1

    assert not stq.taxi_debts_notifications.has_calls


@pytest.mark.parametrize(
    ['next_call'],
    [
        pytest.param(
            None,
            marks=pytest.mark.experiments3(
                **make_debts_notifications_settings(custom_intervals=[]),
            ),
            id='no custom_intervals, no repeat interval',
        ),
        pytest.param(
            {
                'args': [],
                'eta': NOW + datetime.timedelta(seconds=600),
                'id': 'order_id_1_1',
                'kwargs': {
                    'attempt': 1,
                    'initial_run': False,
                    'order_id': 'order_id_1',
                },
                'queue': 'taxi_debts_notifications',
            },
            marks=pytest.mark.experiments3(
                **make_debts_notifications_settings(custom_intervals=[600]),
            ),
            id='enough custom intervals',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'some_title_key': {'ru': 'Some title'},
        'some_subtitle_key': {'ru': 'Some subtitle'},
    },
)
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=True)
@pytest.mark.now(NOW.isoformat())
async def test_debts_notification_initial_run(
        stq,
        stq_runner,
        mock_ucommunications_push,
        mock_archive_order,
        next_call,
):
    ucommunications_mock = mock_ucommunications_push(
        order_id='order_id_1', attempt=0,
    )
    archive_order_mock = mock_archive_order()

    await stq_runner.taxi_debts_notifications.call(
        task_id='order_id_1-0', args=('order_id_1', 0, True),
    )
    assert ucommunications_mock.times_called == 0
    assert archive_order_mock.times_called == 1

    if next_call is not None:
        call = stq.taxi_debts_notifications.next_call()
        call['kwargs'].pop('log_extra')
        assert call == next_call
    else:
        assert not stq.taxi_debts_notifications.has_calls


@pytest.mark.parametrize(
    ['attempt', 'next_call'],
    [
        pytest.param(
            100,
            None,
            marks=pytest.mark.experiments3(
                **make_debts_notifications_settings(custom_intervals=[]),
            ),
            id='not enough custom_intervals, no repeat interval',
        ),
        pytest.param(
            2,
            {
                'args': [],
                'eta': NOW + datetime.timedelta(seconds=300),
                'id': 'order_id_1_3',
                'kwargs': {
                    'attempt': 3,
                    'initial_run': False,
                    'order_id': 'order_id_1',
                },
                'queue': 'taxi_debts_notifications',
            },
            marks=pytest.mark.experiments3(
                **make_debts_notifications_settings(
                    custom_intervals=[100, 200, 300],
                ),
            ),
            id='enough custom_intervals',
        ),
        pytest.param(
            100,
            {
                'args': [],
                'eta': NOW + datetime.timedelta(seconds=200),
                'id': 'order_id_1_101',
                'kwargs': {
                    'attempt': 101,
                    'initial_run': False,
                    'order_id': 'order_id_1',
                },
                'queue': 'taxi_debts_notifications',
            },
            marks=pytest.mark.experiments3(
                **make_debts_notifications_settings(
                    custom_intervals=[100], repeat_interval=200,
                ),
            ),
            id='not enough custom_intervals, repeat interval exists',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'some_title_key': {'ru': 'Some title'},
        'some_subtitle_key': {'ru': 'Some subtitle'},
    },
)
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=True)
@pytest.mark.now(NOW.isoformat())
async def test_debts_notification(
        stq,
        stq_runner,
        mock_ucommunications_push,
        mock_archive_order,
        attempt,
        next_call,
):
    ucommunications_mock = mock_ucommunications_push(
        order_id='order_id_1', attempt=attempt,
    )
    archive_order_mock = mock_archive_order(order_id='order_id_1')

    await stq_runner.taxi_debts_notifications.call(
        task_id='order_id_1-1', args=('order_id_1', attempt, False),
    )
    assert ucommunications_mock.times_called == 1
    assert archive_order_mock.times_called == 1
    assert archive_order_mock.times_called == 1

    if next_call is not None:
        call = stq.taxi_debts_notifications.next_call()
        call['kwargs'].pop('log_extra')
        assert call == next_call
