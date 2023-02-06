import pytest


def item_refresh_delay_config(
        batch_size=10, items_limit=100, refresh_period=1800,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_picker_item_categories_item_refresh_delay',
        consumers=['eats-picker-item-categories/item-refresh-delay'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'batch_size': batch_size,
            'items_limit': items_limit,
            'refresh_period': refresh_period,
        },
    )
