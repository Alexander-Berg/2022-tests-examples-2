import datetime

import pytest


@pytest.mark.parametrize(
    'expect_call,created_ts',
    [
        pytest.param(
            False,
            datetime.datetime.utcnow() - datetime.timedelta(minutes=2),
            marks=pytest.mark.config(CARGO_CLAIMS_SEND_CANCEL_SMS_TIMEOUT=1),
        ),
        pytest.param(True, datetime.datetime.utcnow()),
    ],
)
@pytest.mark.config(CARGO_CLAIMS_ALLOW_SMS_SENDER_BY_COUNTRY=True)
async def test_stq(
        stq_runner,
        mock_ucommunications,
        create_claim_with_performer,
        taxi_cargo_claims,
        get_segment_id,
        build_segment_update_request,
        expect_call,
        created_ts,
):
    segment_id = await get_segment_id()
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    'taxi_order_id_1',
                    with_performer=False,
                    revision=3,
                    resolution='failed',
                ),
            ],
        },
    )
    assert response.status_code == 200

    await stq_runner.cargo_claims_send_cancel_sms.call(
        task_id=create_claim_with_performer.claim_id,
        kwargs={'created_ts': created_ts},
    )

    if expect_call:
        assert mock_ucommunications.times_called == 1
        result = await mock_ucommunications.wait_call()
        assert result['request'].json == {
            'phone_id': '+79098887777_id',
            'text': {
                'keyset': 'notify',
                'key': 'cargo_claims_send_cancel_sms_cancelled_by_taxi',
                'params': {'fullname': 'Свободы, 30'},
            },
            'locale': 'en',
            'intent': 'cargo_failed',
            'sender': 'go',
        }
    else:
        assert mock_ucommunications.times_called == 0
