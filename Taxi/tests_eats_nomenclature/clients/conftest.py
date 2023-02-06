import pytest


@pytest.fixture(name='set_assortment_name_exp')
def _set_assortment_name_exp(experiments3):
    def do_set_assortment_name_exp(
            experiment_on,
            assortment_name,
            brand_ids=None,
            excluded_place_ids=None,
    ):
        experiment_data = _get_exp_data()
        exp_clause = experiment_data['experiments'][0]['clauses'][0]
        exp_clause['value']['assortment_name'] = assortment_name
        predicates = exp_clause['predicate'] = {
            'init': {'predicates': []},
            'type': 'all_of',
        }
        if brand_ids is not None:
            predicates['init']['predicates'].append(
                {
                    'init': {
                        'set': brand_ids,
                        'arg_name': 'brand_id',
                        'set_elem_type': 'int',
                    },
                    'type': 'in_set',
                },
            )
        if excluded_place_ids is not None:
            predicates['init']['predicates'].append(
                {
                    'init': {
                        'predicate': {
                            'init': {
                                'set': excluded_place_ids,
                                'arg_name': 'place_id',
                                'set_elem_type': 'int',
                            },
                            'type': 'in_set',
                        },
                    },
                    'type': 'not',
                },
            )
        experiment_data['experiments'][0]['match']['predicate']['type'] = (
            'true' if experiment_on else 'false'
        )
        experiments3.add_experiments_json(experiment_data)

    return do_set_assortment_name_exp


def _get_exp_data():
    return {
        'experiments': [
            {
                'clauses': [
                    {
                        'is_signal': False,
                        'predicate': {'init': {}, 'type': 'true'},
                        'title': 'any-title',
                        'value': {
                            'assortment_name': 'experiment_assortment_name',
                        },
                    },
                ],
                'default_value': None,
                'description': 'description',
                'last_modified_at': 133838,
                'match': {
                    'action_time': {
                        'from': '2020-07-02T21:56:00+03:00',
                        'to': '2122-07-02T21:56:00+03:00',
                    },
                    'consumers': [
                        {'name': 'eats_nomenclature/assortment_name'},
                    ],
                    'enabled': True,
                    'predicate': {'init': {}, 'type': 'true'},
                    'schema': '',
                },
                'name': 'eats_nomenclature_assortment_name',
            },
        ],
    }


@pytest.fixture(name='sql_delete_brand_place')
def _sql_delete_brand_place(pg_cursor):
    def do_sql_delete_brand_place(place_id):
        pg_cursor.execute(
            """
            delete from eats_nomenclature.brand_places
            where place_id = %s
            """,
            (place_id,),
        )

    return do_sql_delete_brand_place
