def make_settings(agglomeration, settings):
    return {
        'name': 'dispatch_buffer_agglomeration_settings',
        'consumers': ['lookup_dispatch/agglomeration_settings'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': agglomeration,
                'value': {**settings},
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': agglomeration,
                                    'arg_name': 'agglomeration',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
            },
        ],
        'default_value': {},
    }
