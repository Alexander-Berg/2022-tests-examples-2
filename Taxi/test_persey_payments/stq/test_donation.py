import datetime as dt

import pytest
import pytz

from taxi.clients import stq_agent
from taxi.util import dates


def _get_eta(date, shift_sec):
    return (date + dt.timedelta(seconds=shift_sec)).strftime(
        stq_agent.ETA_FORMAT,
    )


@pytest.mark.parametrize(
    'payment_status, status_begin, status_end, clear_times_called, '
    'check_times_called, reschedule_times_called, bb_times_called, '
    'sticker_times_called',
    [
        ('authorized', 'started', 'cleared', 1, 1, 1, 0, 0),
        ('started', 'started', 'started', 0, 1, 1, 0, 0),
        ('3ds_started', 'started', 'started', 0, 1, 1, 0, 0),
        ('not_authorized', 'started', 'not_authorized', 0, 1, 0, 0, 0),
        ('cleared', 'started', 'finished', 0, 1, 0, 1, 1),
        (None, 'not_authorized', 'not_authorized', 0, 0, 0, 0, 0),
        (None, 'finished', 'finished', 0, 0, 0, 0, 0),
        ('authorized', 'cleared', 'cleared', 0, 1, 1, 0, 0),
        ('cleared', 'cleared', 'finished', 0, 1, 0, 1, 1),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'create_donation_success': {
            'body': '{from_string} {firstname} {amount}',
            'theme': 'donation',
        },
    },
)
@pytest.mark.now('2019-11-11T12:00:00+0')
async def test_started_cleared(
        pgsql,
        load,
        load_json,
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        trust_clear_init_success,
        mock_trust_check_basket,
        payment_status,
        status_begin,
        status_end,
        clear_times_called,
        check_times_called,
        reschedule_times_called,
        mock_blackbox,
        mock_send_raw,
        bb_times_called,
        sticker_times_called,
):
    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(load('simple.sqlt').format(status_begin))

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'persey_payments_donation',
            'eta': _get_eta(dates.utcnow(), 20),
            'task_id': '1',
        }
        return {}

    sticker_mock = mock_send_raw('expected_sticker_request.json')
    blackbox_mock = mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]})
    check_mock = mock_trust_check_basket({'payment_status': payment_status})
    clear_mock = trust_clear_init_success()

    await stq_runner.persey_payments_donation.call(
        task_id='1', args=(1, 'create_donation'),
    )

    assert clear_mock.times_called == clear_times_called
    assert check_mock.times_called == check_times_called
    assert blackbox_mock.times_called == bb_times_called
    assert sticker_mock.times_called == sticker_times_called
    assert _stq_reschedule.times_called == reschedule_times_called

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.donation')
    rows = list(cursor)
    assert rows == [(status_end,)]


@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'create_donation_success': {
            'body': '{from_string} {firstname} {amount}',
            'theme': 'donation',
        },
    },
)
@pytest.mark.now('2019-11-11T12:00:00+0')
async def test_empty_yandex_uid(
        pgsql,
        load,
        load_json,
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        trust_clear_init_success,
        mock_trust_check_basket,
        mock_blackbox,
        mock_send_raw,
):
    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(load('simple.sqlt').format('cleared'))
    cursor = db.cursor()
    cursor.execute('update persey_payments.donation set yandex_uid = NULL')

    sticker_mock = mock_send_raw('expected_sticker_anon_request.json')
    blackbox_mock = mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]})
    check_mock = mock_trust_check_basket({'payment_status': 'cleared'})

    await stq_runner.persey_payments_donation.call(
        task_id='1', args=(1, 'create_donation'),
    )

    assert check_mock.times_called == 1
    assert sticker_mock.times_called == 1
    assert blackbox_mock.times_called == 0
    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.donation')
    rows = list(cursor)
    assert rows == [('finished',)]


@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['subs.sql'])
@pytest.mark.parametrize(
    'payment_status, reschedule_times_called, clear_times_called, '
    'check_subs_times_called, subs_status',
    [
        ('not_authorized', 0, 0, 0, 'canceled'),
        ('authorized', 1, 1, 1, 'in_progress'),
    ],
)
async def test_subs(
        pgsql,
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        get_subs_events,
        trust_clear_init_success,
        mock_trust_check_basket,
        mock_check_subs,
        payment_status,
        reschedule_times_called,
        clear_times_called,
        check_subs_times_called,
        subs_status,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'persey_payments_donation',
            'eta': _get_eta(dates.utcnow(), 20),
            'task_id': '1',
        }
        return {}

    check_mock = mock_trust_check_basket({'payment_status': payment_status})
    check_subs_mock = mock_check_subs('check_subs_response.json')
    clear_mock = trust_clear_init_success()

    await stq_runner.persey_payments_donation.call(
        task_id='1', args=(1, 'create_subs'),
    )

    assert check_mock.times_called == 1
    assert check_subs_mock.times_called == check_subs_times_called
    assert clear_mock.times_called == clear_times_called
    assert _stq_reschedule.times_called == reschedule_times_called

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT subs_until_ts, status FROM persey_payments.subs')
    data = list(cursor)
    assert len(data) == 1

    if subs_status == 'canceled':
        assert data[0][0] is None
        assert data[0][1] == 'canceled'
        assert get_subs_events() == []
    elif subs_status == 'in_progress':
        assert data[0][0].astimezone(pytz.UTC) == dt.datetime(
            2020, 6, 2, 13, 53, 10, tzinfo=pytz.UTC,
        )
        assert data[0][1] == 'in_progress'
        assert get_subs_events() == [('create',)]
    else:
        raise ValueError()


@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'create_subs_success': {
            'body': '{firstname} {personal_account_link}',
            'theme': 'donation',
        },
        'prolong_subs_success': {
            'body': (
                '{firstname} {amount} {user_account} {personal_account_link}'
            ),
            'theme': 'donation',
        },
    },
)
@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['subs_finish.sql'])
@pytest.mark.parametrize(
    'action, expected_sticker_request',
    [
        ('create_subs', 'expected_sticker_request_create_subs.json'),
        ('prolong_subs', 'expected_sticker_request_prolong_subs.json'),
    ],
)
async def test_subs_finish(
        pgsql,
        stq_runner,
        mock_trust_check_basket,
        mock_blackbox,
        mock_send_raw,
        action,
        expected_sticker_request,
):
    bb_mock = mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]})
    sticker_mock = mock_send_raw(expected_sticker_request)
    check_mock = mock_trust_check_basket(
        {'payment_status': 'cleared', 'user_account': '000'},
    )

    await stq_runner.persey_payments_donation.call(
        task_id='1', args=(1, action),
    )

    assert bb_mock.times_called == 1
    assert sticker_mock.times_called == 1
    assert check_mock.times_called == 1


@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'create_donation_success': {
            'body': '{from_string} {firstname} {amount}',
            'theme': 'donation',
        },
    },
)
@pytest.mark.pgsql('persey_payments', files=['no_user_email.sql'])
@pytest.mark.now('2019-11-11T12:00:00+0')
async def test_no_user_email(pgsql, stq_runner, mock_trust_check_basket):
    check_mock = mock_trust_check_basket({'payment_status': 'cleared'})

    await stq_runner.persey_payments_donation.call(
        task_id='1', args=(1, 'create_donation'),
    )

    assert check_mock.times_called == 1

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.donation')
    rows = list(cursor)
    assert rows == [('finished',)]


@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'create_donation_success': {
            'body': (
                'jinja:{% if firstname %}hello, {{ firstname }}'
                '{% else %}:O{% endif %}'
            ),
            'theme': 'donation',
        },
    },
)
@pytest.mark.parametrize(
    'bb_fail, expected_sticker_request',
    [
        (True, 'expected_sticker_request_jinja_bb_fail.json'),
        (False, 'expected_sticker_request_jinja_bb_ok.json'),
    ],
)
async def test_subs_notify_jinja(
        pgsql,
        load,
        stq_runner,
        mockserver,
        trust_clear_init_success,
        mock_trust_check_basket,
        mock_blackbox,
        mock_send_raw,
        bb_fail,
        expected_sticker_request,
):
    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(load('simple.sqlt').format('cleared'))

    sticker_mock = mock_send_raw(expected_sticker_request)
    mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]}, bb_fail)
    mock_trust_check_basket({'payment_status': 'cleared'})

    await stq_runner.persey_payments_donation.call(
        task_id='1', args=(1, 'create_donation'),
    )

    assert sticker_mock.times_called == 1
