import pytest

from tests_grocery_caas_markdown.common import constants


LAVKA_SELLONCOGS_EXPERIMENT_WITH_NO_ENABLED = pytest.mark.experiments3(
    name='lavka_selloncogs',
    consumers=['grocery-caas-markdown'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {'title': 'No enabled', 'predicate': {'type': 'true'}, 'value': {}},
    ],
    is_config=True,
)


CLAUSES = [
    ('depot_id', constants.DEPOT_ID_WITH_MARKDOWNS),
    ('yandex_uid', constants.YANDEX_UID_WITH_MARKDOWNS),
    ('country_iso3', constants.COUNTRY_ISO3_WITH_MARKDOWNS),
]


LAVKA_SELLONCOGS_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_selloncogs',
    consumers=['grocery-caas-markdown'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': f'Enabled for {arg_name} {arg_value}',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': arg_name,
                    'arg_type': 'string',
                    'value': arg_value,
                },
            },
            'value': {'enabled': True},
        }
        for arg_name, arg_value in CLAUSES
    ],
    is_config=True,
)
