import pytest


@pytest.mark.now('2020-05-01T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_MAILS_TEMPLATES={
        'cancel_subs_user': {
            'body': '{firstname} {personal_account_link}',
            'theme': 'donation',
        },
    },
)
async def test_simple(
        web_app_client,
        pgsql,
        get_subs_events,
        mock_cancel_subs,
        mock_send_raw,
        mock_blackbox,
):
    bb_mock = mock_blackbox({'users': [{'attributes': {'27': 'Ivan'}}]})
    sticker_mock = mock_send_raw('expected_sticker_request.json')
    cancel_subs_mock = mock_cancel_subs()

    response = await web_app_client.post(
        '/payments/v1/charity/subs/cancel',
        json={'subs_id': 'some_external_id'},
        headers={'X-Yandex-UID': '41'},
    )
    assert response.status == 200
    assert await response.json() == {}
    assert bb_mock.times_called == 1
    assert sticker_mock.times_called == 1
    assert cancel_subs_mock.times_called == 1
    assert get_subs_events() == [('delete',)]
