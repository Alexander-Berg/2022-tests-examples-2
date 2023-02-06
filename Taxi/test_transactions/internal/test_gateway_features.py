from typing import List

import pytest

from transactions.internal import gateway_features


_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS = [
    {'name': 'use_trust_unhold_on_full_cancel', 'value': {}},
]

_DISABLED_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS = [
    {'name': 'use_trust_unhold_on_full_cancel', 'value': {'enabled': False}},
]
_ENABLED_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS = [
    {'name': 'use_trust_unhold_on_full_cancel', 'value': {'enabled': True}},
]


@pytest.mark.parametrize(
    'is_error, matched_experiments, expected_experiment_enabled',
    [
        (False, [], False),
        (False, _USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS, True),
        (False, _ENABLED_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS, True),
        (False, _DISABLED_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS, False),
        (True, _USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS, False),
        (True, _ENABLED_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS, False),
        (True, _DISABLED_USE_TRUST_UNHOLD_ON_FULL_CANCEL_EXPS, False),
    ],
)
async def test_use_trust_unhold_on_full_cancel(
        stq3_context,
        mock_experiments3_call,
        *,
        is_error: bool,
        matched_experiments: List[dict],
        expected_experiment_enabled: bool,
):
    external_payment_id = 'purchase-token'
    uid = 'uid'
    mock_experiments3_call(
        consumer='transactions',
        args=[
            {'name': 'transactions_scope', 'type': 'string', 'value': 'taxi'},
            {
                'name': 'external_payment_id',
                'type': 'string',
                'value': external_payment_id,
            },
            {'name': 'uid', 'type': 'string', 'value': uid},
        ],
        matched_experiments=matched_experiments,
        is_error=is_error,
    )
    features = gateway_features.Features(stq3_context)
    experiment_enabled = await features.use_trust_unhold_on_full_cancel(
        external_payment_id=external_payment_id, uid=uid,
    )
    assert experiment_enabled == expected_experiment_enabled


@pytest.fixture(name='mock_experiments3_call')
def _mock_experiments3_call(mockserver):
    def _do_mock(
            consumer: str,
            args: List[dict],
            matched_experiments: List[dict],
            is_error: bool = False,
    ):
        @mockserver.json_handler('/experiments3/v1/experiments')
        def _handler(request):
            if is_error:
                return mockserver.make_response(
                    '500 Internal Server Error', status=500,
                )

            assert request.json == {'consumer': consumer, 'args': args}
            return {'items': matched_experiments}

        return _handler

    return _do_mock
