import pytest

from tests_eats_products import utils


def max_depth_experiment(enabled=True, value=100):
    return pytest.mark.experiments3(
        is_config=False,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_products_replace_max_depth_in_request',
        consumers=['eats_products/menu_goods'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': enabled, 'value': value},
                'predicate': {'type': 'true'},
            },
        ],
    )


CATEGORY_ID = 1


@pytest.mark.parametrize(
    ['max_depth', 'expected', 'category', 'category_uid'],
    [
        pytest.param(1, '1', CATEGORY_ID, CATEGORY_ID, id='exp missing'),
        pytest.param(None, '100', CATEGORY_ID, CATEGORY_ID, id='No max_depth'),
        pytest.param(
            1,
            '1',
            CATEGORY_ID,
            CATEGORY_ID,
            marks=max_depth_experiment(False),
            id='exp disabled',
        ),
        pytest.param(
            1,
            '100',
            CATEGORY_ID,
            None,
            marks=max_depth_experiment(True),
            id='exp enabled. 1->100, categoryId filled',
        ),
        pytest.param(
            1,
            '100',
            None,
            CATEGORY_ID,
            marks=max_depth_experiment(True),
            id='exp enabled. 1->100, category_uid filled',
        ),
        pytest.param(
            1,
            '1',
            None,
            None,
            marks=max_depth_experiment(True),
            id='exp enabled, but requesting top_level only',
        ),
        pytest.param(
            10,
            '50',
            CATEGORY_ID,
            CATEGORY_ID,
            marks=max_depth_experiment(True, 50),
            id='exp enabled. 10->50',
        ),
        pytest.param(
            None,
            '100',
            CATEGORY_ID,
            CATEGORY_ID,
            marks=max_depth_experiment(True),
            id='exp enabled. None->100',
        ),
    ],
)
async def test_max_depth_experiment(
        taxi_eats_products,
        mockserver,
        max_depth,
        expected,
        category,
        category_uid,
):
    body = {'slug': 'slug', 'maxDepth': max_depth}
    if category:
        body['category'] = category
    if category_uid:
        body['category_uid'] = str(category_uid)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        assert request.query['max_depth'] == expected

    await taxi_eats_products.post(utils.Handlers.MENU_GOODS, json=body)
