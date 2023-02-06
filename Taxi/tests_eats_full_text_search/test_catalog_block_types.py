import pytest

from . import catalog
from . import experiments
from . import utils


@pytest.mark.parametrize(
    'expected',
    (
        # Тест проверяет, что если нет эксперимента, то срабатывает фоллбэк на
        # захардкоженные значения.
        pytest.param(
            [
                {'id': 'open', 'type': 'open', 'condition': None},
                {'id': 'closed', 'type': 'closed', 'condition': None},
            ],
            id='fallback',
        ),
        # Тест проверяет, что если эксперимент возвращает пустой список, то
        # срабатывает фоллбэк на захардкоженные значения.
        pytest.param(
            [
                {'id': 'open', 'type': 'open', 'condition': None},
                {'id': 'closed', 'type': 'closed', 'condition': None},
            ],
            marks=[experiments.eats_fts_blocks_for_catalog([])],
            id='empty_exp',
        ),
        # Тест проверяет, что если в эксперименте указано только одно
        # значение, то оно и будет использовано.
        pytest.param(
            [{'id': 'closed', 'type': 'closed', 'condition': None}],
            marks=experiments.eats_fts_blocks_for_catalog(
                [catalog.BlockParam('closed')],
            ),
            id='one_value',
        ),
        # Тест проверяет, что если значения в эксперименте соответствуют
        # захардкоженным значениям, то ничего не ломается.
        pytest.param(
            [
                {'id': 'open', 'type': 'open', 'condition': None},
                {'id': 'closed', 'type': 'closed', 'condition': None},
            ],
            marks=experiments.eats_fts_blocks_for_catalog(
                [catalog.BlockParam('open'), catalog.BlockParam('closed')],
            ),
            id='exp_as_fallback',
        ),
        # Тест проверяет, что значения выставленные в эксперименте являются
        # более приоритетными чем захардкоженные.
        pytest.param(
            [
                {
                    'id': 'open_delivery_or_pickup',
                    'type': 'open_delivery_or_pickup',
                    'condition': None,
                },
                {'id': 'closed', 'type': 'closed', 'condition': None},
            ],
            marks=experiments.eats_fts_blocks_for_catalog(
                [
                    catalog.BlockParam('open_delivery_or_pickup'),
                    catalog.BlockParam('closed'),
                ],
            ),
            id='retail',
        ),
        # Тест проверяет, что все значения из эксперимента будут использованы.
        pytest.param(
            [
                {'id': 'any', 'type': 'any', 'condition': None},
                {
                    'id': 'open_delivery_or_pickup',
                    'type': 'open_delivery_or_pickup',
                    'condition': None,
                },
                {'id': 'closed', 'type': 'closed', 'condition': None},
                {'id': 'open', 'type': 'open', 'condition': None},
            ],
            marks=experiments.eats_fts_blocks_for_catalog(
                [
                    catalog.BlockParam('any'),
                    catalog.BlockParam('open_delivery_or_pickup'),
                    catalog.BlockParam('closed'),
                    catalog.BlockParam('open'),
                ],
            ),
            id='multiple_values',
        ),
        pytest.param(
            [
                {
                    'id': 'open_brands_42',
                    'type': 'open',
                    'condition': {
                        'type': 'in_set',
                        'init': {
                            'arg_name': 'brand_id',
                            'set_elem_type': 'int',
                            'set': [42],
                        },
                    },
                },
            ],
            marks=experiments.eats_fts_blocks_for_catalog(
                [catalog.BlockParam('open', brand_ids=[42])],
            ),
            id='brand_condition',
        ),
        pytest.param(
            [
                {
                    'id': 'open_brands_42_places_1_businesses_restaurant',
                    'type': 'open',
                    'condition': {
                        'type': 'all_of',
                        'predicates': [
                            {
                                'type': 'in_set',
                                'init': {
                                    'arg_name': 'brand_id',
                                    'set_elem_type': 'int',
                                    'set': [42],
                                },
                            },
                            {
                                'type': 'in_set',
                                'init': {
                                    'arg_name': 'place_id',
                                    'set_elem_type': 'int',
                                    'set': [1],
                                },
                            },
                            {
                                'type': 'in_set',
                                'init': {
                                    'arg_name': 'business',
                                    'set_elem_type': 'string',
                                    'set': ['restaurant'],
                                },
                            },
                        ],
                    },
                },
            ],
            marks=experiments.eats_fts_blocks_for_catalog(
                [
                    catalog.BlockParam(
                        'open',
                        brand_ids=[42],
                        place_ids=[1],
                        businesses=['restaurant'],
                    ),
                ],
            ),
            id='complex_condition',
        ),
    ),
)
async def test_catalog_block_types(
        taxi_eats_full_text_search, mockserver, expected,
):
    @mockserver.json_handler(
        '/eats-catalog/internal/v1/catalog-for-full-text-search',
    )
    def catalog_for_fts(request):
        print(expected)
        for block, expected_block in zip(request.json['blocks'], expected):
            for key, value in expected_block.items():
                assert block.get(key) == value
        return {'blocks': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'text': 'My Search Text',
        },
        headers=utils.get_headers(),
    )

    assert catalog_for_fts.times_called == 1
    assert response.status_code == 200
