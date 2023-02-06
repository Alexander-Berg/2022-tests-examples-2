def create_true_predicate():
    return {'init': {}, 'type': 'true'}


def create_false_predicate():
    return {'init': {}, 'type': 'false'}


def create_not_null_predicate(arg_name):
    return {'init': {'arg_name': arg_name}, 'type': 'not_null'}


def create_eq_predicate(arg_name, value, arg_type='string'):
    return {
        'init': {'arg_name': arg_name, 'arg_type': arg_type, 'value': value},
        'type': 'eq',
    }


def create_gte_predicate(arg_name, value, arg_type):
    return {
        'init': {'arg_name': arg_name, 'arg_type': arg_type, 'value': value},
        'type': 'gte',
    }


def create_all_of_predicate(predicates):
    return {'init': {'predicates': predicates}, 'type': 'all_of'}


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
