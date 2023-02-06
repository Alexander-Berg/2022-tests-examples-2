import pytest

GROCERY_FEEDBACK_PREDEFINED_COMMENTS = pytest.mark.experiments3(
    name='grocery_feedback_predefined_comments',
    consumers=['grocery-eats-gateway/feedback'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'options': [
                    {
                        'evaluation': 1,
                        'title': 'bad_feedback',
                        'predefined_comments': [
                            {
                                'comment_id': 'comment_id_1',
                                'eats_id': 1,
                                'tanker_key': 'comment_key_1',
                            },
                        ],
                    },
                    {
                        'evaluation': 2,
                        'title': 'bad_feedback',
                        'predefined_comments': [
                            {
                                'comment_id': 'comment_id_2',
                                'eats_id': 2,
                                'tanker_key': 'comment_key_2',
                            },
                        ],
                    },
                ],
            },
        },
    ],
    is_config=True,
)
