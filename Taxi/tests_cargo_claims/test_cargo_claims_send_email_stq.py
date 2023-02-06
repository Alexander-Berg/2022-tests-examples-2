import pytest


@pytest.fixture(name='mock_sticker')
def _mock_sticker(mockserver):
    @mockserver.handler('/sticker/send/')
    def _mock_sticker_send(request, *args, **kwargs):
        return mockserver.make_response('{}', status=200)

    return _mock_sticker_send


@pytest.mark.parametrize(
    'status,expect_done,expect_fail',
    [
        ('performer_draft', False, True),
        ('failed', False, False),
        ('performer_found', True, False),
    ],
)
@pytest.mark.config(
    CARGO_CLAIMS_ORDER_CONFIRM_EMAIL={
        '__default__': {
            'body_xml': """<?xml version="1.0" encoding="UTF-8"?><mails><mail>
                <from>cargo@yandex.ru</from>
                <subject>Order confirmation</subject>
                <body>
                  Taxi order details:
                  - Driver {driver_name}
                  - Driver phone number {driver_phone}
                  - Car {car_model} {car_number}
                </body></mail></mails>
            """,
            'act_file_name': 'act.pdf',
        },
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                        '__default__': {
                            'enabled': True,
                            'yt-use-runtime': False,
                            'yt-timeout-ms': 1000,
                            'ttl-days': 3650,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                        '__default__': {'enabled': False},
                    },
                ),
            ],
        ),
    ],
)
async def test_stq(
        status,
        expect_done,
        expect_fail,
        stq_runner,
        mock_sticker,
        state_controller,
        create_default_documents,
):
    claim_info = await state_controller.apply(target_status=status)
    claim_id = claim_info.claim_id

    create_default_documents(claim_id)

    await stq_runner.cargo_claims_send_email.call(
        task_id=claim_id,
        kwargs={
            'claim_id': claim_id,
            'receiver_email_id': 'some_recipient_id',
            'claim_status': 'new',
        },
        expect_fail=expect_fail,
    )
    if not expect_done:
        assert mock_sticker.times_called == 0
    else:
        assert mock_sticker.times_called == 1
        result = await mock_sticker.wait_call()
        assert result['request'].json['send_to'] == ['some_recipient_id']
        assert result['request'].json['body'] is not None
        assert result['request'].json['attachments'] is not None
