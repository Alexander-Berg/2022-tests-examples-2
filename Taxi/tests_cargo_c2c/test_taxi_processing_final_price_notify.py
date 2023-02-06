import uuid

import pytest


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.translations(
        tariff={
            'currency_sign.rub': {'ru': '₽'},
            'currency.byn': {'ru': 'р.'},
        },
    ),
]


@pytest.mark.config(
    CARGO_C2C_CASH_FINAL_PRICE_TANKER_BY_COUNTRY_MAP={
        '__default__': 'c2c.recipient.cash_order_final_price_notify',
        'blr': 'c2c.recipient.cash_order_final_price_notify_blr',
    },
)
@pytest.mark.parametrize(
    ('zone', 'code', 'expected_symbol', 'expected_key'),
    [
        ('moscow', 'RUB', '₽', 'c2c.recipient.cash_order_final_price_notify'),
        (
            'minsk',
            'BYN',
            'р.',
            'c2c.recipient.cash_order_final_price_notify_blr',
        ),
    ],
)
async def test_final_price_send(
        stq_runner,
        mockserver,
        zone: str,
        code: str,
        expected_symbol: str,
        expected_key: str,
):
    phone_id = uuid.uuid4().hex

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _sms(request):
        assert request.json == {
            'intent': 'cargo_c2c_taxi_cash_order_final_price_notify',
            'locale': 'ru',
            'phone_id': phone_id,
            'sender': 'go',
            'text': {
                'key': expected_key,
                'keyset': 'cargo',
                'params': {'cost': '90', 'currency': expected_symbol},
            },
        }
        return mockserver.make_response(
            json={
                'code': '200',
                'message': 'OK',
                'message_id': uuid.uuid4().hex,
                'status': 'sent',
            },
            status=200,
        )

    await stq_runner.cargo_c2c_taxi_cash_order_final_price_notify.call(
        task_id=uuid.uuid4().hex,
        args=[],
        kwargs={
            'cost': 90.00,
            'currency': code,
            'phone_id': phone_id,
            'locale': 'ru',
            'zone': zone,
        },
    )


@pytest.mark.config(CARGO_SMS_SENDER_BY_COUNTRY={})
async def test_skip_sms_sending(stq_runner):
    await stq_runner.cargo_c2c_taxi_cash_order_final_price_notify.call(
        task_id=uuid.uuid4().hex,
        args=[],
        kwargs={
            'cost': 90.00,
            'currency': 'RUB',
            'phone_id': uuid.uuid4().hex,
            'locale': 'ru',
            'zone': 'moscow',
        },
    )
