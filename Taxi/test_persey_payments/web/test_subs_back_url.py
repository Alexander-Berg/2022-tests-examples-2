import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'cancel_subs_technical': {
            'body': '{firstname} {personal_account_link}',
            'theme': 'donation',
        },
    },
)
@pytest.mark.parametrize(
    'blackbox_resp, exp_sticker_req',
    [
        (
            {'users': [{'attributes': {'27': 'Ivan'}}]},
            'expected_sticker_request.json',
        ),
        (
            {
                'users': [
                    {
                        'attributes': {'27': 'Ivan'},
                        'aliases': {'1': 'some_login'},
                    },
                ],
            },
            'expected_sticker_request_strict_login.json',
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        pgsql,
        get_subs_events,
        mock_blackbox,
        mock_send_raw,
        blackbox_resp,
        exp_sticker_req,
):
    blackbox_mock = mock_blackbox(blackbox_resp)
    sticker_mock = mock_send_raw(exp_sticker_req)

    response = await taxi_persey_payments_web.post(
        '/v1/charity/subs/back_url',
        json={
            'type': 'SUBS_EVENT',
            'event_ts_msec': '777',
            'service_id': 684,
            'event_data': {
                'order_id': 'some_order_id',
                'event_type': 'RENEWAL_CANCELED',
                'reason': 'RENEWAL_ERROR',
            },
        },
    )
    assert response.status == 200
    assert await response.json() == {'status': 'success'}
    assert blackbox_mock.times_called == 1
    assert sticker_mock.times_called == 1
    assert get_subs_events() == [('delete',)]

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.subs')
    assert list(cursor) == [('canceled',)]
