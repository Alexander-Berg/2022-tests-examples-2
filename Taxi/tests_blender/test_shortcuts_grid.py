import copy

import pytest

from tests_blender import shortcuts_grid_helpers as helpers


def _drop_ids(resp):
    resp['grid'].pop('id')
    for block in resp['grid']['blocks']:
        block.pop('id')
        block.pop('shortcut_ids')
    for cell in resp['grid']['cells']:
        cell['shortcut'].pop('id')


def _check_equals(resp_body, expected):
    _drop_ids(resp_body)
    _drop_ids(expected)
    assert resp_body == expected


@pytest.fixture(name='response_fetcher')
def _response_fetcher(taxi_blender, load_json):
    return helpers.ResponceFetcher(taxi_blender, load_json)


@pytest.mark.experiments3(filename='experiments3.json')
async def test_baseline_shortcuts_grid(taxi_blender, load_json):
    req_body = load_json('simple_request.json')
    response = await taxi_blender.post(
        'blender/v1/shortcuts-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()
    assert 'grid' in resp_body

    assert resp_body['grid']['id'] != ''
    assert resp_body['grid']['width'] == 6


# pylint: disable=redefined-outer-name
@pytest.mark.experiments3(filename='experiments3.json')
async def test_single_shortcut(response_fetcher):
    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': ['Домой'],
                'eats_place': [],
                'grocery_category': [],
            },
        )
    ).layout == []

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': ['Домой'],
                'eats_place': [],
                'grocery_category': [],
                'promo_stories': ['promo'],
            },
        )
    ).layout == [['Домой', 4], ['promo', 2]]


# pylint: disable=redefined-outer-name
@pytest.mark.experiments3(filename='experiments3.json')
async def test_only_taxi_small_top(response_fetcher):
    # FIXME organic doesnot work like this
    # assert (
    #     await response_fetcher.response(
    #         {
    #             'taxi_expected_destination': ['Домой', 'На работу'],
    #             'eats_place': [],
    #             'grocery_category': [],
    #         },
    #     )
    # ).layout == [['Домой', 3], ['На работу', 3]]

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': [
                    'Домой',
                    'Константинопольская набережная, 82',
                ],
                'eats_place': [],
                'grocery_category': [],
            },
        )
    ).layout == [['Домой', 2], ['Константинопольская набережная, 82', 4]]

    # FIXME doesnot work like this
    # assert (
    #     (
    #         await response_fetcher.response(
    #             {
    #                 'taxi_expected_destination': [
    #                     'Льва Толстого, 16, строение 1',
    #                     'Константинопольская набережная, 82',
    #                 ],
    #                 'eats_place': [],
    #                 'grocery_category': [],
    #             },
    #         )
    #     ).layout
    #     == [
    #         ['Льва Толстого, 16, строение 1', 3],
    #         ['Константинопольская набережная, 82', 3],
    #     ]
    # )


# pylint: disable=redefined-outer-name
@pytest.mark.skip
@pytest.mark.experiments3(filename='experiments3.json')
async def test_first_line(response_fetcher):
    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': ['Домой', 'На работу'],
                'eats_place': ['Якитория'],
                'grocery_category': ['Завтрак'],
            },
        )
    ).layout == [['Домой', 2], ['На работу', 2], ['Якитория', 2]]

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': [
                    'Домой',
                    'Константинопольская набережная, 82',
                ],
                'eats_place': ['Якитория'],
                'grocery_category': ['Завтрак'],
            },
        )
    ).layout[:2] == [['Домой', 2], ['Константинопольская набережная, 82', 4]]

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': ['Домой', 'На работу'],
                'eats_place': ['РесторанЯкитория'],
                'grocery_category': ['Завтрак'],
            },
        )
    ).layout == [['Домой', 2], ['На работу', 2], ['Завтрак', 2]]

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': ['Домой', 'На работу'],
                'eats_place': ['РесторанЯкитория'],
                'grocery_category': ['ПрекрасныйЗавтрак'],
            },
        )
    ).layout[:2] == [['Домой', 3], ['На работу', 3]]

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': [
                    'Константинопольская набережная, 81',
                    'Константинопольская набережная, 82',
                ],
                'eats_place': [],
                'grocery_category': ['Завтрак'],
            },
        )
    ).layout == [['Константинопольская набережная, 81', 4], ['Завтрак', 2]]

    assert (
        await response_fetcher.response(
            {
                'taxi_expected_destination': [],
                'eats_place': ['eda 1', 'eda 2', 'eda 3'],
                'grocery_category': ['groc 1'],
            },
        )
    ).layout == [['eda 1', 2], ['eda 2', 2], ['groc 1', 2]]


# pylint: disable=redefined-outer-name
@pytest.mark.experiments3(filename='experiments3.json')
async def test_long_layout_with_single_scenario(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [f'taxi {i}' for i in range(18)],
            'eats_place': [],
            'grocery_category': [],
        },
    )

    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)


# pylint: disable=redefined-outer-name
@pytest.mark.experiments3(filename='experiments3.json')
async def test_long_layout_with_several_scenario(response_fetcher):

    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [f'taxi {i}' for i in range(5)],
            'eats_place': [f'eda {i}' for i in range(5)],
            'grocery_category': [f'lavka {i}' for i in range(5)],
            'promo_stories': ['promo'],
            'lavka_referral': ['lref'],
            'media_stories': [f'media {i}' for i in range(3)],
        },
    )

    layout_without_media = list(
        filter(lambda cell: 'media' not in cell.title, resp.layout),
    )
    helpers.check_layout_without_gaps(layout_without_media)
    helpers.check_layout_diversity(layout_without_media)
    assert layout_without_media == [
        ['taxi 0', 2],
        ['promo', 2],
        ['taxi 1', 2],
        ['eda 0', 4],
        ['lref', 2],
        ['eda 1', 2],
        ['eda 2', 4],
        ['eda 3', 3],
        ['eda 4', 3],
        ['lavka 0', 2],
        ['lavka 1', 2],
        ['lavka 2', 2],
        ['lavka 3', 4],
        ['lavka 4', 2],
    ]

    assert resp.blocks == [
        ['organic', ['taxi 0', 'taxi 1', 'promo', 'eda 0', 'lref']],
        ['eats_place', [f'eda {i}' for i in range(1, 5)]],
        ['grocery_category', [f'lavka {i}' for i in range(0, 5)]],
        ['media_stories', [f'media {i}' for i in range(2)]],
    ]


# pylint: disable=redefined-outer-name
@pytest.mark.experiments3(filename='experiments3_max_lines.json')
async def test_long_layout_with_single_scenario_max_lines(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [f'taxi {i}' for i in range(18)],
            'eats_place': [],
            'grocery_category': [],
        },
    )

    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)
    lines = helpers.split_to_lines(
        resp.layout, width_function=lambda cell: cell.width,
    )
    assert len(lines) == 3


# pylint: disable=redefined-outer-name
@pytest.mark.experiments3(filename='experiments3.json')
async def test_fit_long_titles(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [
                'Домой',
                'На работу',
                'Константинопольская набережная, 82',
            ],
            'eats_place': ['Якитория'],
            'grocery_category': ['Завтрак'],
        },
    )

    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)
    assert resp.layout == [
        ['Домой', 2],
        ['На работу', 2],
        ['Якитория', 2],
        ['Константинопольская набережная, 82', 4],
        ['Завтрак', 2],
    ]


@pytest.mark.experiments3(filename='experiments3.json')
async def test_unsupported_input(taxi_blender, load_json):
    req_body = load_json('empty_request.json')

    def spoil_grid_width():
        res = copy.deepcopy(req_body)
        res['grid_restriction']['grid_width'] = 5
        return res, 400

    def spoil_cell_widths():
        res = copy.deepcopy(req_body)
        res['grid_restriction']['cell_widths'] = [2, 4]
        return res, 500

    for spoil_f in spoil_grid_width, spoil_cell_widths:
        request_json, expected_code = spoil_f()
        response = await taxi_blender.post(
            'blender/v1/shortcuts-grid',
            json=request_json,
            headers=helpers.MEANINGLESS_HEADERS,
        )

        assert response.status_code == expected_code


@pytest.mark.experiments3(filename='experiments3_assignment.json')
@pytest.mark.parametrize(
    'expected_scenarios',
    [
        pytest.param(
            {
                'eats_place',
                'promo_stories',
                'grocery_category',
                'taxi_expected_destination',
            },
            id='normal mode',
        ),
        pytest.param(
            {'taxi_expected_destination'},
            marks=pytest.mark.experiments3(
                filename='experiments3_organic_allowed_scenarios.json',
            ),
            id='ultima mode',
        ),
    ],
)
async def test_all_scenarios_existed(response_fetcher, expected_scenarios):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': ['Домой', 'На работу'],
            'eats_place': ['Якитория'],
            'grocery_category': ['Завтрак'],
            'promo_stories': ['Доставка лекарств'],
            'media_stories': ['Музей Гараж'],
        },
    )

    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)
    helpers.check_layout_scenarios(resp.layout, expected_scenarios)


@pytest.mark.experiments3(filename='experiments3.json')
async def test_organic_block(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': ['taxi 0'],
            'eats_place': [f'eda {i}' for i in range(10)],
        },
    )

    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)
    assert (
        len(
            helpers.split_to_lines(
                resp.layout, width_function=lambda cell: cell.width,
            ),
        )
        == 4
    )
    assert len(resp.blocks) == 2
    assert len(resp.blocks[0].shortcut_ids) == 5


@pytest.mark.experiments3(filename='experiments3_assignment.json')
async def test_organic_block_via_assignment(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': ['taxi 0'],
            'eats_place': [f'eda {i}' for i in range(10)],
        },
    )

    helpers.check_layout_without_gaps(resp.layout)
    assert (
        len(
            helpers.split_to_lines(
                resp.layout, width_function=lambda cell: cell.width,
            ),
        )
        == 4
    )
    assert len(resp.blocks) == 2
    assert len(resp.blocks[0].shortcut_ids) == 5


@pytest.mark.experiments3(filename='experiments3_organic_sizes.json')
async def test_baseline_organic_sizes_shortcuts_grid(response_fetcher):
    tops = {
        'taxi_expected_destination': ['taxi 0', 'taxi 1'],
        'eats_place': [f'eda {i}' for i in range(10)],
        'grocery_category': [f'lavka {i}' for i in range(10)],
    }

    resp = await response_fetcher.response(
        tops, title_to_tags={'eda 3': ['personal'], 'taxi 0': ['personal']},
    )
    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)
    assert resp.layout == [
        ['taxi 0', 2],
        ['taxi 1', 2],
        ['eda 0', 2],
        ['lavka 0', 2],
        ['eda 1', 4],
        ['lavka 1', 3],
        ['eda 3', 3],
    ]

    resp = await response_fetcher.response(
        tops,
        title_to_tags={
            'eda 1': ['personal'],
            'eda 3': ['personal'],
            'lavka 2': ['personal'],
        },
    )
    helpers.check_layout_without_gaps(resp.layout)
    helpers.check_layout_diversity(resp.layout)
    assert resp.layout == [['taxi 0', 2], ['eda 1', 2], ['lavka 2', 2]]


@pytest.mark.experiments3(filename='experiments3_media.json')
async def test_media_stories_simple(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [f'taxi {i}' for i in range(5)],
            'media_stories': [f'med {i}' for i in range(4)],
        },
    )
    assert resp.layout == [
        ['taxi 0', 2],
        ['taxi 1', 2],
        ['taxi 2', 2],
        ['taxi 3', 4],
        ['taxi 4', 2],
        ['med 0', 2, 4],
        ['med 1', 4, 2],
        ['med 2', 4, 2],
    ]


@pytest.mark.experiments3(filename='experiments3_media.json')
async def test_media_stories_in_the_end(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [f'taxi {i}' for i in range(3)],
            'media_stories': [f'med {i}' for i in range(4)],
        },
    )
    assert resp.layout == [
        ['taxi 0', 2],
        ['taxi 1', 2],
        ['taxi 2', 2],
        ['med 0', 2, 4],
        ['med 1', 4, 2],
        ['med 2', 4, 2],
    ]


@pytest.mark.experiments3(filename='experiments3.json')
async def test_promo(response_fetcher):
    resp = await response_fetcher.response(
        {
            'taxi_expected_destination': [f'taxi {i}' for i in range(10)],
            'eats_place': [f'eda {i}' for i in range(10)],
            'grocery_category': [f'lavka {i}' for i in range(10)],
            'promo_stories': [f'promo'],
        },
    )
    helpers.check_layout_diversity(resp.layout)
    helpers.check_layout_without_gaps(resp.layout)
    lines = helpers.split_to_lines(
        resp.layout, width_function=lambda cell: cell.width,
    )
    assert 'promo' in [cell.title for cell in lines[0]]
    assert 'promo' not in [cell.title for cell in lines[1]]
    assert 'promo' not in [cell.title for cell in lines[2]]
    assert 'promo' not in [cell.title for cell in lines[3]]


@pytest.mark.skip(reason='UB')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_intent_modifier(response_fetcher):
    resp = await response_fetcher.response(
        scenario_to_top={
            'taxi_expected_destination': [f'taxi {i}' for i in range(10)],
            'eats_place': [f'eda {i}' for i in range(10)],
            'grocery_category': [f'lavka {i}' for i in range(10)],
        },
        scenario_to_prediction={'eats_place': 0.01},
    )
    helpers.check_layout_diversity(resp.layout)
    helpers.check_layout_without_gaps(resp.layout)

    organic_sh_ids = [
        id
        for block in resp.blocks
        for id in block.shortcut_ids
        if block.slug == 'organic'
    ]
    assert 'eats_place' not in [
        cell.scenario
        for cell in resp.layout
        if cell.shortcut_id in organic_sh_ids
    ]


@pytest.mark.skip(reason='UB')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_block_eraser(response_fetcher):
    resp = await response_fetcher.response(
        scenario_to_top={
            'taxi_expected_destination': [f'taxi {i}' for i in range(10)],
            'eats_place': [f'eda {i}' for i in range(10)],
            'grocery_category': [f'lavka {i}' for i in range(10)],
        },
        scenario_to_prediction={'grocery_category': 0.01},
    )
    helpers.check_layout_diversity(resp.layout)
    helpers.check_layout_without_gaps(resp.layout)
    assert 'grocery_category' not in [block.slug for block in resp.blocks]


@pytest.mark.experiments3(filename='experiments3.json')
async def test_known_orders(response_fetcher):
    resp = await response_fetcher.response(
        scenario_to_top={
            'taxi_expected_destination': [f'taxi {i}' for i in range(10)],
            'eats_place': [f'eda {i}' for i in range(10)],
            'grocery_category': [f'lavka {i}' for i in range(10)],
        },
        known_orders=['eats'],
    )
    helpers.check_layout_diversity(resp.layout)
    helpers.check_layout_without_gaps(resp.layout)
    organic_sh_ids = [
        id
        for block in resp.blocks
        for id in block.shortcut_ids
        if block.slug == 'organic'
    ]
    assert 'eats_place' not in [
        cell.scenario
        for cell in resp.layout
        if cell.shortcut_id in organic_sh_ids
    ]


@pytest.mark.experiments3(filename='experiments3_transform_taxi_to_eats.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_preprocessing(response_fetcher):
    resp = await response_fetcher.response(
        scenario_to_top={
            'taxi_expected_destination': [f'taxi {i}' for i in range(5)],
            'eats_place': [f'eda {i}' for i in range(5)],
        },
        check_params=False,
    )

    # eda before taxi
    max_eda_index = max(
        index for index, cell in enumerate(resp.layout) if 'eda' in cell.title
    )
    min_taxi_index = min(
        index for index, cell in enumerate(resp.layout) if 'taxi' in cell.title
    )
    assert max_eda_index < min_taxi_index
    assert {cell.scenario for cell in resp.layout} == {'eats_place'}
    assert len(resp.layout) <= 5 + 5


@pytest.mark.experiments3(filename='experiments3.json')
async def test_building_shortcuts(taxi_blender, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response.json')

    req_body = load_json('request_with_shortcuts_to_build_enabled.json')
    response = await taxi_blender.post(
        'blender/v1/shortcuts-grid',
        json=req_body,
        headers=helpers.MEANINGLESS_HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()

    expected = load_json('building_shortcuts_response.json')
    _check_equals(resp_body, expected)


async def test_add_shop(load_json, experiments3, response_fetcher):
    exp3_json = load_json('experiments3_grid_rules.json')
    exp3_json['experiments'][0]['clauses'][0]['value'].update(
        {'add_shops': True},
    )
    experiments3.add_experiments_json(exp3_json)
    request = {
        'taxi_expected_destination': [f'taxi {i}' for i in range(3)],
        'eats_place': [f'eats {i}' for i in range(3)],
        'grocery_category': [f'grocery {i}' for i in range(3)],
        'eats_shop': [f'eats_shop {i}' for i in range(3)],
    }
    resp = await response_fetcher.response(request)
    assert len(resp.shop_shortcuts) == 3
