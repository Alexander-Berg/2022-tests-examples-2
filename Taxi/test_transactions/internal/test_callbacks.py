from typing import Optional

import pytest

from transactions.internal import callbacks

CONFIG_HOST = 'http://a.net'
CONFIG_BASE_URL = CONFIG_HOST + '/callback/'
CONFIG_PREFIX = '/callback/{invoice_id}'


def _make_invoice(
        id_: str,
        yandex_uid: str = 'some_yandex_uid',
        personal_phone_id: Optional[str] = 'some_personal_phone_id',
        billing_service='unknown',
):
    return {
        '_id': id_,
        'invoice_request': {
            'personal_phone_id': personal_phone_id,
            'billing_service': billing_service,
        },
        'yandex_uid': yandex_uid,
    }


@pytest.mark.config(
    TRANSACTIONS_TRUST_BACK_URL={
        'taxi': {'card': {'host': CONFIG_HOST, 'prefix': CONFIG_PREFIX}},
    },
)
@pytest.mark.parametrize(
    'invoice, experiments, expected',
    [
        pytest.param(
            _make_invoice('some_invoice_id'),
            [],
            None,
            id='it should return None by default',
        ),
        pytest.param(
            _make_invoice('some%_invoic/e_id', billing_service='card'),
            [],
            CONFIG_BASE_URL + 'some%25_invoic/e_id',
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_SEND_BACK_URL_TO_TRUST={
                        'taxi': {'card': 'enabled'},
                    },
                ),
            ],
            id='it should return callback url when enabled by config',
        ),
        pytest.param(
            _make_invoice('some_invoice_id', billing_service='card'),
            [],
            None,
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_SEND_BACK_URL_TO_TRUST={
                        'taxi': {'card': 'use_experiment'},
                    },
                ),
            ],
            id='it should return None when disabled by experiment',
        ),
        pytest.param(
            _make_invoice('some_invoice_id', billing_service='delivery'),
            [],
            None,
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_SEND_BACK_URL_TO_TRUST={
                        'taxi': {'delivery': 'enabled'},
                    },
                ),
            ],
            id='it should return None when no back url for service',
        ),
        pytest.param(
            _make_invoice('some_invoice_id', billing_service='card'),
            [
                {
                    'name': 'transactions_send_back_url_to_trust',
                    'value': {'enabled': True},
                },
            ],
            CONFIG_BASE_URL + 'some_invoice_id',
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_SEND_BACK_URL_TO_TRUST={
                        'taxi': {'card': 'use_experiment'},
                    },
                ),
            ],
            id='it should return callback url when enabled by experiment',
        ),
    ],
)
async def test_try_generate_back_url(
        mockserver, stq3_context, invoice, experiments, expected,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        del request  # unused
        return {'items': experiments}

    actual = await callbacks.try_generate_back_url(stq3_context, invoice)
    assert actual == expected


@pytest.mark.config(
    TRANSACTIONS_SEND_BACK_URL_TO_TRUST={'taxi': {'card': 'enabled'}},
)
@pytest.mark.parametrize(
    'invoice, expected',
    [
        pytest.param(
            _make_invoice('some_invoice_id'),
            None,
            id='it should return None by default',
        ),
        pytest.param(
            _make_invoice('some_invoce_id', billing_service='card'),
            'http://transactions.taxi.yandex.net'
            '/v1/callback/trust/payment/some_invoce_id',
            id='it should return callback url because default value',
        ),
    ],
)
async def test_default_back_url(mockserver, stq3_context, invoice, expected):
    actual = await callbacks.try_generate_back_url(stq3_context, invoice)
    assert actual == expected
