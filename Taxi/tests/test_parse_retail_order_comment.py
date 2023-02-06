import pytest


# pylint: disable=import-only-modules
from taximeter_emulator.taximeter import RetailOrderExchangePosition
from taximeter_emulator.taximeter import Taximeter


@pytest.mark.parametrize(
    'command, parsed_value',
    [
        pytest.param(
            'retail_order_change - РН201821:1->РН201821:1',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=1,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_ignore - 3',
            {'retail_order_ignore': 3},
        ),
        pytest.param(
            'retail_order_change - РН201821:1->РН201817:1',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201817',
                        quantity=1,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821:1->РН201821:1',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=1,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->РН201821',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=None,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->РН201821:1',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=1,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->РН201821:1, '
            'retail_order_ignore - 3',
            {
                'retail_order_ignore': 3,
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=1,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->РН201821:1,'
            'РН201829:1->РН201828:1',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=1,
                    ),
                    RetailOrderExchangePosition(
                        old_item_id='РН201829',
                        new_item_id='РН201828',
                        quantity=1,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id=None,
                        quantity=None,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - ->РН201821',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id=None,
                        new_item_id='РН201821',
                        quantity=None,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->,РН201822->РН201823',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id=None,
                        quantity=None,
                    ),
                    RetailOrderExchangePosition(
                        old_item_id='РН201822',
                        new_item_id='РН201823',
                        quantity=None,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->РН201821:1.5',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=1.5,
                    ),
                ],
            },
        ),
        pytest.param(
            'retail_order_change - РН201821->РН201821:w200',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН201821',
                        new_item_id='РН201821',
                        quantity=None,
                        weight=200,
                    ),
                ],
            },
        ),
        pytest.param(
            'speed - 999, retail_order_change - РН000655->РН000655:w2000',
            {
                'retail_order_change': [
                    RetailOrderExchangePosition(
                        old_item_id='РН000655',
                        new_item_id='РН000655',
                        quantity=None,
                        weight=2000,
                    ),
                ],
                'speed': '999',
            },
        ),
    ],
)
def test_parse_retail_order_comment(command, parsed_value):
    assert Taximeter.parse_retail_commands(command) == parsed_value
