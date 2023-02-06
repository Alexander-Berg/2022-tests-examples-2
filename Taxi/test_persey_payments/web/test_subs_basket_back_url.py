import datetime as dt

import pytest
import pytz


@pytest.mark.pgsql('persey_payments', files=['initial.sql'])
async def test_initial(
        taxi_persey_payments_web, load_json, stq, pgsql, mock_check_subs,
):
    check_subs_mock = mock_check_subs('check_subs_response.json')

    response = await taxi_persey_payments_web.post(
        '/v1/charity/subs/basket_back_url',
        data={
            'purchase_token': 'trust-basket-token',
            'subs_stage': 'initial',
            'status': 'success',
            'status_code': 'success',
            'service_order_id': 'some_order_id',
        },
    )
    assert response.status == 200
    assert await response.json() == {'status': 'success'}
    assert check_subs_mock.times_called == 1
    assert stq.persey_payments_donation.times_called == 1
    call = stq.persey_payments_donation.next_call()
    assert call['args'] == [1, 'create_subs']

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT subs_until_ts, hold_until_ts FROM persey_payments.subs',
    )
    data = list(cursor)
    assert len(data) == 1
    assert data[0][0].astimezone(pytz.UTC) == dt.datetime(
        2020, 6, 2, 13, 53, 10, tzinfo=pytz.UTC,
    )


@pytest.mark.pgsql('persey_payments', files=['prolongation.sql'])
async def test_prolong(
        taxi_persey_payments_web, load_json, stq, pgsql, mock_check_subs,
):
    check_subs_mock = mock_check_subs('check_subs_response.json')

    response = await taxi_persey_payments_web.post(
        '/v1/charity/subs/basket_back_url',
        data={
            'purchase_token': 'trust-basket-token',
            'subs_stage': 'prolongation',
            'status': 'success',
            'status_code': 'success',
            'service_order_id': 'some_order_id',
        },
    )
    assert response.status == 200
    assert await response.json() == {'status': 'success'}
    assert check_subs_mock.times_called == 1
    assert stq.persey_payments_donation.times_called == 1
    call = stq.persey_payments_donation.next_call()
    assert call['args'] == [1, 'prolong_subs']

    db = pgsql['persey_payments']

    cursor = db.cursor()
    cursor.execute(
        'SELECT subs_until_ts, hold_until_ts FROM persey_payments.subs',
    )
    data = list(cursor)
    assert len(data) == 1
    assert data[0][0].astimezone(pytz.UTC) == dt.datetime(
        2020, 6, 2, 13, 53, 10, tzinfo=pytz.UTC,
    )

    cursor = db.cursor()
    cursor.execute(
        'SELECT purchase_token, subs_id, status FROM persey_payments.donation',
    )
    data = list(cursor)
    assert data == [('trust-basket-token', 1, 'started')]


@pytest.mark.pgsql('persey_payments', files=['prolongation.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'prolong_subs_fail': {
            'body': (
                '{firstname} {recommendations} {user_account} {amount} '
                '{next_attempt_date} {personal_account_link}'
            ),
            'theme': 'donation',
        },
    },
)
@pytest.mark.now('2020-06-03T11:19:00+0300')
async def test_prolong_retries(
        taxi_persey_payments_web,
        load_json,
        stq,
        pgsql,
        mock_check_subs,
        mock_blackbox,
        mock_send_raw,
        mock_trust_check_basket,
):
    blackbox_mock = mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]})
    sticker_mock = mock_send_raw('expected_sticker_request_hold.json')
    check_mock = mock_trust_check_basket(
        {'payment_status': 'not_authorized', 'user_account': 'some_account'},
    )
    check_subs_mock = mock_check_subs('check_subs_response_hold.json')

    response = await taxi_persey_payments_web.post(
        '/v1/charity/subs/basket_back_url',
        data={
            'purchase_token': 'trust-basket-token',
            'subs_stage': 'prolongation',
            'status': 'cancelled',
            'status_code': 'not_enough_funds',
            'service_order_id': 'some_order_id',
        },
    )
    assert response.status == 200
    assert await response.json() == {'status': 'success'}
    assert check_subs_mock.times_called == 1
    assert check_mock.times_called == 1
    assert sticker_mock.times_called == 1
    assert blackbox_mock.times_called == 1
    assert stq.persey_payments_donation.times_called == 1
    call = stq.persey_payments_donation.next_call()
    assert call['args'] == [1, 'prolong_subs']

    db = pgsql['persey_payments']

    cursor = db.cursor()
    cursor.execute(
        'SELECT subs_until_ts, hold_until_ts FROM persey_payments.subs',
    )
    data = [[item.astimezone(pytz.UTC) for item in entry] for entry in cursor]
    assert data == [
        [
            dt.datetime(2020, 6, 3, 8, 5, 50, tzinfo=pytz.UTC),
            dt.datetime(2020, 6, 3, 8, 20, 50, tzinfo=pytz.UTC),
        ],
    ]

    cursor = db.cursor()
    cursor.execute(
        'SELECT purchase_token, subs_id, status FROM persey_payments.donation',
    )
    data = list(cursor)
    assert data == [('trust-basket-token', 1, 'started')]
