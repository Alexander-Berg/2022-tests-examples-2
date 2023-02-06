import copy

# pylint: disable=import-error
from eats_bigb.eats_bigb import Profile
import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils

BRAND_ID = 1
TEST_PASSPORT_UID = '4003514354'
TEST_DEVICE_ID = 'device_id'


def settings():
    return {f'{BRAND_ID}': {'should_filter_categories_by_bigb': True}}


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_exp_not_matched(
        taxi_eats_nomenclature, experiments3, load_json,
):
    experiments3.add_experiment(
        **make_adverts_experiment(make_exp_categories(show=False)),
    )

    some_device_id = 'device_id2'
    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug',
        headers=make_auth_headers(TEST_PASSPORT_UID, some_device_id),
    )
    assert response.status == 200

    assert sort_by_id(load_json('response.json')) == sort_by_id(
        response.json(),
    )


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.parametrize(
    'show, removed_categories',
    [
        pytest.param(True, [], id='always_show'),
        pytest.param(False, [2, 3, 6], id='never_show'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_exp_without_targeting(
        taxi_eats_nomenclature,
        experiments3,
        load_json,
        bigb,
        # parametrize params
        show,
        removed_categories,
):
    experiments3.add_experiment(
        **make_adverts_experiment(make_exp_categories(show)),
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug', headers=make_auth_headers(),
    )
    assert response.status == 200

    assert not bigb.times_called

    assert sort_by_id(
        get_without_categories(load_json('response.json'), removed_categories),
    ) == sort_by_id(response.json())


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_exp_with_targeting_no_auth(
        taxi_eats_nomenclature, experiments3, load_json,
):
    targeting = {
        'heuristic_segments': [1, 2, 3],
        'audience_segments': [4, 5, 6],
        'longterm_interests_segments': [7, 8, 9],
        'shortterm_interests_segments': [10, 11],
    }
    experiments3.add_experiment(
        **make_adverts_experiment(
            make_exp_categories(show=True, targeting=targeting),
        ),
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug', headers={'X-Device-Id': TEST_DEVICE_ID},
    )
    assert response.status == 200

    removed_categories = [2, 3, 6]
    assert sort_by_id(
        get_without_categories(load_json('response.json'), removed_categories),
    ) == sort_by_id(response.json())


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.parametrize(
    'targeting, profile, removed_categories',
    [
        pytest.param(
            # few segments intersect
            {
                'heuristic_segments': [1, 2, 3],
                'audience_segments': [4, 5, 6],
                'longterm_interests_segments': [7, 8, 9],
                'shortterm_interests_segments': [10, 11],
            },
            {
                'heuristic_segments': [2, 3, 99],
                'audience_segments': [4, 801],
                'longterm_interests_segments': [25, 71],
                'shortterm_interests_segments': [113],
            },
            [],
            id='user_has_many_interests',
        ),
        pytest.param(
            # only one segment intersect
            {
                'heuristic_segments': [1, 2, 3],
                'audience_segments': [4, 5, 6],
                'longterm_interests_segments': [7, 8, 9],
                'shortterm_interests_segments': [10, 11],
            },
            {
                'heuristic_segments': [99],
                'audience_segments': [801],
                'longterm_interests_segments': [7, 25, 71],
                'shortterm_interests_segments': [113],
            },
            [],
            id='user_has_one_interest',
        ),
        pytest.param(
            # no segment intersect
            {
                'heuristic_segments': [1, 2, 3],
                'audience_segments': [4, 5, 6],
                'longterm_interests_segments': [7, 8, 9],
                'shortterm_interests_segments': [10, 11],
            },
            {
                'heuristic_segments': [99],
                'audience_segments': [801],
                'longterm_interests_segments': [25, 71],
                'shortterm_interests_segments': [113],
            },
            [2, 3, 6],
            id='user_has_no_interest',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_exp_with_targeting(
        taxi_eats_nomenclature,
        experiments3,
        load_json,
        bigb,
        # parametrize params
        targeting,
        profile,
        removed_categories,
):
    bigb.add_profile(
        TEST_PASSPORT_UID,
        Profile(
            heuristic_segments=profile['heuristic_segments'],
            audience_segments=profile['audience_segments'],
            longterm_interests_segments=profile['longterm_interests_segments'],
            shortterm_interests_segments=profile[
                'shortterm_interests_segments'
            ],
        ),
    )

    experiments3.add_experiment(
        **make_adverts_experiment(
            make_exp_categories(show=True, targeting=targeting),
        ),
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug', headers=make_auth_headers(),
    )
    assert response.status == 200

    assert bigb.times_called

    assert sort_by_id(
        get_without_categories(load_json('response.json'), removed_categories),
    ) == sort_by_id(response.json())


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.parametrize(
    'show, removed_categories',
    [
        pytest.param(True, [], id='always_show'),
        pytest.param(False, [2, 3], id='never_show'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_exp_with_requested_category(
        taxi_eats_nomenclature,
        experiments3,
        load_json,
        # parametrize params
        should_include_pennies_in_price,
        show,
        removed_categories,
):
    experiments3.add_experiment(
        **make_adverts_experiment(make_exp_categories(show)),
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_2_origin',
        headers=make_auth_headers(),
    )
    assert response.status == 200

    expected_response = get_without_categories(
        load_json('requested_category_response.json'), removed_categories,
    )

    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')

    assert sort_by_id(response.json()) == sort_by_id(expected_response)


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.parametrize(
    'show, removed_categories',
    [
        pytest.param(True, [], id='always_show'),
        pytest.param(False, [1, 2, 3, 6, 8], id='never_show'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_remove_parent_with_all_removed_children(
        taxi_eats_nomenclature,
        experiments3,
        load_json,
        # parametrize params
        show,
        removed_categories,
):
    experiments3.add_experiment(
        **make_adverts_experiment(
            [
                # remove one parent and two leaf categories
                {'category_id': '2', 'show': show, 'targeting': None},
                {'category_id': '6', 'show': show, 'targeting': None},
                {'category_id': '8', 'show': show, 'targeting': None},
            ],
        ),
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug', headers=make_auth_headers(),
    )
    assert response.status == 200

    assert sort_by_id(
        get_without_categories(load_json('response.json'), removed_categories),
    ) == sort_by_id(response.json())


def make_adverts_experiment(categories) -> dict:
    return {
        'name': 'eats_nomenclature_adverts',
        'consumers': ['eats_nomenclature/adverts'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {
                    'init': {
                        'arg_name': 'device_id',
                        'arg_type': 'string',
                        'value': TEST_DEVICE_ID,
                    },
                    'type': 'eq',
                },
                'value': {'categories': categories},
            },
        ],
        'default_value': {'categories': []},
    }


def make_auth_headers(
        passport_uid=TEST_PASSPORT_UID, device_id=TEST_DEVICE_ID,
):
    return {'X-Yandex-UID': passport_uid, 'X-Device-Id': device_id}


def make_exp_categories(show, targeting=None):
    return [
        # remove one parent and one leaf category
        {'category_id': '2', 'show': show, 'targeting': targeting},
        {'category_id': '6', 'show': show, 'targeting': targeting},
    ]


def get_without_categories(data, category_public_ids):
    src_categories = copy.deepcopy(data['categories'])
    data['categories'] = [
        category
        for category in src_categories
        if category['public_id'] not in category_public_ids
    ]
    return data


def sort_by_id(data):
    for category in data['categories']:
        category['items'] = sorted(category['items'], key=lambda k: k['id'])
    data['categories'] = sorted(data['categories'], key=lambda k: k['id'])
    return data
