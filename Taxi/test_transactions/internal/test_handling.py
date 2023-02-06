import pytest

from transactions.internal import handling


def _build_algorithm_spec(value):
    return {
        'primary_delay': value,
        'increased_delay': value,
        'num_attempts_with_primary_delay': value,
    }


@pytest.mark.config(
    TRANSACTIONS_POLLING_BACKOFF_ALGO_ENABLED=True,
    TRANSACTIONS_POLLING_BACKOFF_ALGO={
        'taxi': {
            'trust:hold:billing_service=uber:payment_type': (
                _build_algorithm_spec(1)
            ),
            'trust:hold': _build_algorithm_spec(2),
            '__default__': _build_algorithm_spec(3),
        },
        '__default__': {'__default__': _build_algorithm_spec(4)},
    },
)
@pytest.mark.parametrize(
    'stage_names, expected',
    [
        pytest.param(
            ['trust:hold:billing_service=uber:payment_type', 'trust:hold'],
            _build_algorithm_spec(1),
            id='it should return the first matching spec',
        ),
        pytest.param(
            ['trust:hold', 'trust:hold:billing_service=uber:payment_type'],
            _build_algorithm_spec(2),
            id='it should return the first matching spec',
        ),
        pytest.param(
            ['unknown', 'trust:hold'],
            _build_algorithm_spec(2),
            id='it should ignore unknown stages',
        ),
        pytest.param(
            ['try find this', 'or this'],
            _build_algorithm_spec(3),
            id='it should return the default spec if nothing matches',
        ),
        pytest.param(
            [],
            _build_algorithm_spec(3),
            id='it should return the default spec if there are no stages',
        ),
    ],
)
def test_get_backoff_algorithm_spec(stq3_context, stage_names, expected):
    # pylint: disable=protected-access
    actual = handling._get_backoff_algorithm_spec(
        stq3_context, stage_names, None,
    )
    assert actual == expected
