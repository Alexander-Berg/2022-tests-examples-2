def create_eq_predicate(arg_name, value, arg_type='string'):
    return {
        'init': {'arg_name': arg_name, 'arg_type': arg_type, 'value': value},
        'type': 'eq',
    }


def create_experiment(name, consumers, predicates, value):
    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'name': name,
        'consumers': consumers,
        'clauses': [
            {
                'predicate': {
                    'init': {'predicates': predicates},
                    'type': 'all_of',
                },
                'value': value,
            },
        ],
    }
