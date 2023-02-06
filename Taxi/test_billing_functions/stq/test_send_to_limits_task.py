import pytest

from billing_functions.stq import send_to_limits


@pytest.mark.now('2020-12-31T23:59:59.999999+03:00')
async def test_limits_are_sent(stq3_context, mock_limits):
    await send_to_limits.task(
        stq3_context,
        '100',
        'RUB',
        '2021-03-15T03:00:00+03:00',
        'limit_ref',
        'payment_ref',
    )
    assert mock_limits.requests == [
        {
            'amount': '100',
            'currency': 'RUB',
            'event_at': '2021-03-15T03:00:00+03:00',
            'limit_ref': 'limit_ref',
        },
    ]
