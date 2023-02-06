import pytest

from . import consts


def _create_mapping():
    result = {}
    for country in consts.COUNTRIES:
        result[country] = f'{country.name}-client-id'
    return result


def _create_clauses():
    clauses = []
    for country in consts.COUNTRIES:
        clauses.append(
            {
                'title': f'Settings for {country.name}',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': country.country_iso3,
                        'arg_name': 'country_iso3',
                        'arg_type': 'string',
                    },
                },
                'value': {'balance_client_id': MAPPING[country]},
            },
        )
    return clauses


MAPPING = _create_mapping()

CONFIG = pytest.mark.experiments3(
    name='grocery_balance_client_id',
    consumers=['grocery-payments'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=_create_clauses(),
    is_config=True,
)
