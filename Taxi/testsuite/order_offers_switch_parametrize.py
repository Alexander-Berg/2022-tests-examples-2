import pytest


ORDER_OFFERS_SAVE_SWITCH = pytest.mark.parametrize(
    'order_offers_save_enabled',
    [
        pytest.param(False, id='order_offers_disabled'),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    is_config=True,
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='protocol_save_offer_via_service',
                    consumers=['protocol/routestats'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {
                                'enabled': True,
                                'compress_requests': True,
                            },
                        },
                    ],
                ),
                pytest.mark.experiments3(
                    is_config=True,
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='estimate_save_offer_via_service',
                    consumers=['integration/ordersestimate'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {'enabled': True},
                        },
                    ],
                ),
            ],
            id='order_offers_enabled',
        ),
    ],
)


ORDER_OFFERS_MATCH_SWITCH = pytest.mark.parametrize(
    'order_offers_match_enabled',
    [
        pytest.param(False, id='order_offers_match_disabled'),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='match_offer_via_service',
                    consumers=['protocol/ordercommit'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {'enabled': True},
                        },
                    ],
                ),
            ],
            id='order_offers_match_enabled',
        ),
    ],
)


ORDER_OFFERS_MATCH_COMPARE_SWITCH = pytest.mark.parametrize(
    'order_offers_match_compare_enabled',
    [
        pytest.param(False, id='order_offers_match_compare_disabled'),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='match_offer_via_service_compare',
                    consumers=['protocol/ordercommit'],
                    clauses=[
                        {
                            'enabled': True,
                            'predicate': {'type': 'true'},
                            'value': {'enabled': True},
                        },
                    ],
                ),
            ],
            id='order_offers_match_compare_enabled',
        ),
    ],
)
