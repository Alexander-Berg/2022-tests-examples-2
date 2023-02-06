import datetime as dt
from typing import Optional

import pytest

from transactions.internal import experiments as experiments_module
from transactions.models import const


def _make_config_mark(scope, billing_service, is_enabled):
    return pytest.mark.config(
        TRANSACTIONS_FETCH_EXPERIMENTS_FOR_INVOICE={
            scope: {billing_service: is_enabled},
        },
    )


def _make_invoice(
        id_: str,
        yandex_uid: str = 'some_yandex_uid',
        personal_phone_id: Optional[str] = 'some_personal_phone_id',
        billing_service='unknown',
        currency='RUB',
):
    return {
        '_id': id_,
        'invoice_request': {
            'billing_service': billing_service,
            'currency': currency,
            'invoice_due': dt.datetime(2022, 1, 1),
            'personal_phone_id': personal_phone_id,
        },
        'yandex_uid': yandex_uid,
    }


@pytest.mark.parametrize(
    'invoice, experiments, expected',
    [
        pytest.param(
            _make_invoice('some_invoice_id'),
            [],
            set(),
            id='it should return empty set by default',
        ),
        pytest.param(
            _make_invoice('some_invoice_id', billing_service='card'),
            [{'name': 'use_psp_in_transactions', 'value': {'enabled': True}}],
            set(),
            id='it should return empty set when disabled by config',
            marks=[_make_config_mark('taxi', 'card', False)],
        ),
        pytest.param(
            _make_invoice('some_invoice_id', billing_service='card'),
            Exception,
            set(),
            id='it should return empty set when experiments are down',
            marks=[_make_config_mark('taxi', 'card', True)],
        ),
        pytest.param(
            _make_invoice('some_invoice_id', billing_service='card'),
            [
                {
                    'name': 'use_psp_in_transactions',
                    'value': {'enabled': True},
                },
                {
                    'name': 'some_disabled_experiment',
                    'value': {'enabled': False},
                },
                {
                    'name': 'some_disabled_experiment_with_empty_value',
                    'value': {},
                },
                {
                    'name': 'some_enabled_experiment',
                    'value': {'enabled': True},
                },
            ],
            {'use_psp_in_transactions', 'some_enabled_experiment'},
            id='it should return enabled experiments when enabled by config',
            marks=[_make_config_mark('taxi', 'card', True)],
        ),
    ],
)
async def test_fetch_for_invoice(
        mockserver, stq3_context, invoice, experiments, expected,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        del request  # unused
        if experiments is Exception:
            return mockserver.make_response('error', status=500)
        return {'items': experiments}

    actual = await experiments_module.fetch_for_invoice(
        context=stq3_context,
        invoice=invoice,
        payment_type=const.PaymentType.CARD,
        wait_for_cvn=False,
        log_extra=None,
    )
    assert actual == expected
