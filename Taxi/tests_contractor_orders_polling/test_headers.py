import pytest

from tests_contractor_orders_polling import utils


def make_expretiment3_kwargs(enabled, value):
    return dict(
        match={'predicate': {'type': enabled}, 'enabled': True},
        name='contractor_orders_polling_polling_power_policy_override',
        consumers=['contractor-orders-polling/header-settings'],
        clauses=[],
        default_value=value,
        is_config=False,
    )


@pytest.mark.parametrize(
    'polling_times',
    [
        pytest.param(
            ['full=5s'],
            id='EnabledSimpleExp',
            marks=pytest.mark.experiments3(
                **make_expretiment3_kwargs('true', {'full': 5}),
            ),
        ),
        pytest.param(
            ['full=5s', 'background=30s'],
            id='EnabledComplexExp',
            marks=pytest.mark.experiments3(
                **make_expretiment3_kwargs(
                    'true', {'full': 5, 'background': 30},
                ),
            ),
        ),
        pytest.param(
            ['background=30s', 'full=10s', 'idle=30s', 'powersaving=30s'],
            id='DisabledExp',
            marks=pytest.mark.experiments3(
                **make_expretiment3_kwargs('false', {}),
            ),
        ),
        pytest.param(
            ['background=30s', 'full=10s', 'idle=30s', 'powersaving=30s'],
            id='NoExp',
        ),
    ],
)
async def test_polling_pp_header_with_exp3(
        taxi_contractor_orders_polling, polling_times,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    parts = response.headers['X-Polling-Power-Policy'].split(', ')
    parts.sort()
    assert set(parts) == set(polling_times)


@pytest.mark.parametrize(
    'expected_delay',
    [
        pytest.param(None, id='None'),
        pytest.param(
            '20',
            marks=pytest.mark.config(
                TAXIMETER_POLLING_DELAYS={'/driver/polling/order': 20},
            ),
            id='Happy path',
        ),
    ],
)
async def test_polling_legacy_header(
        taxi_contractor_orders_polling, expected_delay,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )
    assert response.status_code == 200

    delay = response.headers.get('X-Polling-Delay')
    if expected_delay is None:
        assert delay == '10'
    else:
        assert delay == expected_delay
