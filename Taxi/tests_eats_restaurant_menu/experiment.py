import typing

import pytest

ALWAYS = {'predicate': {'type': 'true'}, 'enabled': True}


def always_match(
        name: str,
        consumers: typing.List[str],
        value: dict,
        is_config: bool = False,
):
    return pytest.mark.experiments3(
        is_config=is_config,
        match=ALWAYS,
        name=name,
        consumers=consumers,
        clauses=[
            {
                'title': 'Always match',
                'value': value,
                'predicate': {'type': 'true'},
            },
        ],
        enable_debug=True,
    )


ENABLE_INFORMERS_CATEGORY = always_match(
    name='add_promo_informers_category',
    consumers=['eats_restaurant_menu'],
    value={'enabled': True},
    is_config=True,
)
