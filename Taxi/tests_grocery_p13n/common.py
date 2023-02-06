import pytest

from tests_grocery_p13n import experiments

DEFAULT_ACCOUNT_ID = 'w/12345678-9abc-def0-0000-000000000000'

BOTH_CASHBACK_ENABLED_AND_DISABLED = [
    pytest.param(False, id='cashback is disabled'),
    pytest.param(
        True,
        id='cashback is enabled',
        marks=[experiments.CASHBACK_EXPERIMENT_RUSSIA],
    ),
]


def get_tags_from_match_request(request):
    return request['common_conditions'].get('tags')


def get_product_tags_from_request(request):
    tags = []

    for subquery in request['subqueries']:
        product_tags = subquery['conditions'].get('labels')
        if product_tags is not None:
            tags.append((subquery['subquery_id'], product_tags))
    return tags
