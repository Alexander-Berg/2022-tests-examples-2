import datetime as dt

import pytest
import pytz


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'warn_subs': {
            'body': (
                '{firstname} {payment_date} {user_account} '
                '{amount} {personal_account_link}'
            ),
            'theme': 'donation',
        },
        'warn_subs_no_card': {
            'body': (
                '{firstname} {payment_date} {amount} {personal_account_link}'
            ),
            'theme': 'donation',
        },
    },
)
@pytest.mark.now('2020-05-02T12:00:00+0')
@pytest.mark.parametrize(
    'payment_methods_response, expected_sticker_request',
    [
        ('payment_methods_response.json', 'expected_sticker_request.json'),
        (
            'payment_methods_response_no_card.json',
            'expected_sticker_request_no_card.json',
        ),
        (
            'payment_methods_response_another_card.json',
            'expected_sticker_request_another_card.json',
        ),
    ],
)
async def test_simple(
        cron_runner,
        pgsql,
        mock_check_subs,
        mock_payment_methods,
        mock_send_raw,
        mock_blackbox,
        payment_methods_response,
        expected_sticker_request,
):
    bb_mock = mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]})
    check_subs = mock_check_subs('check_subs_response.json')
    payment_methods = mock_payment_methods(payment_methods_response)
    sticker_mock = mock_send_raw(expected_sticker_request)

    await cron_runner.charity_subs()
    assert check_subs.times_called == 1
    assert payment_methods.times_called == 1
    assert sticker_mock.times_called == 1
    assert bb_mock.times_called == 1

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT subs_id, subs_until_ts FROM persey_payments.charge_warnings',
    )
    data = list(cursor)
    assert len(data) == 1
    assert data[0][0] == 1
    assert data[0][1].astimezone(pytz.UTC) == dt.datetime(
        2020, 5, 2, 21, tzinfo=pytz.UTC,
    )

    # no notification attempt
    await cron_runner.charity_subs()
    assert check_subs.times_called == 1
    assert payment_methods.times_called == 1
    assert sticker_mock.times_called == 1


@pytest.mark.pgsql('persey_payments', files=['stuck_subs.sql'])
@pytest.mark.now('2017-09-05T00:30:01+0')
async def test_stuck_subs(cron_runner, pgsql, mock_check_subs):
    check_subs = mock_check_subs('check_subs_response_stuck_subs.json')

    await cron_runner.charity_subs()
    assert check_subs.times_called == 1

    db = pgsql['persey_payments']

    cursor = db.cursor()
    cursor.execute(
        'SELECT subs_until_ts, hold_until_ts FROM persey_payments.subs',
    )
    data = [[item.astimezone(pytz.UTC) for item in entry] for entry in cursor]
    assert data == [
        [
            dt.datetime(2017, 9, 5, tzinfo=pytz.UTC),
            dt.datetime(2020, 6, 3, 8, 20, 50, tzinfo=pytz.UTC),
        ],
    ]
