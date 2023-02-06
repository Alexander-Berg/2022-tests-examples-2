# pylint: disable=import-error
from eats_bigb.eats_bigb import Profile
import pytest


BRAND_ID = 1
PLACE_SLUG = 'slug'
TEST_PASSPORT_UID = '4003514354'
TEST_DEVICE_ID = 'device_id'
METRICS_NAME = 'adverts-category-shows-data'


def settings():
    return {f'{BRAND_ID}': {'should_filter_categories_by_bigb': True}}


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.parametrize('targeting_present', [True, False])
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
        bigb,
        taxi_eats_nomenclature_monitor,
        targeting_present,
):
    profile = {
        'heuristic_segments': [2, 3, 99],
        'audience_segments': [4, 801],
        'longterm_interests_segments': [25, 71],
        'shortterm_interests_segments': [113],
    }
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

    targeting = (
        {
            'heuristic_segments': [1, 2, 3],
            'audience_segments': [4, 5, 6],
            'longterm_interests_segments': [7, 8, 9],
            'shortterm_interests_segments': [10, 11],
        }
        if targeting_present
        else None
    )
    experiments3.add_experiment(
        **make_adverts_experiment(
            make_exp_categories(show=True, targeting=targeting),
        ),
    )

    await taxi_eats_nomenclature.tests_control(reset_metrics=True)
    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}', headers=make_auth_headers(),
    )
    assert response.status == 200

    if targeting_present:
        assert bigb.times_called

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    if targeting_present:
        assert metrics[METRICS_NAME] == {
            '$meta': {'solomon_children_labels': 'category_id'},
            '2': {
                'shows_in_target_group': 1,
                'shows_in_unconditional_group': 0,
            },
            '6': {
                'shows_in_target_group': 1,
                'shows_in_unconditional_group': 0,
            },
        }
    else:
        assert metrics[METRICS_NAME] == {
            '$meta': {'solomon_children_labels': 'category_id'},
            '2': {
                'shows_in_target_group': 0,
                'shows_in_unconditional_group': 1,
            },
            '6': {
                'shows_in_target_group': 0,
                'shows_in_unconditional_group': 1,
            },
        }


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
        taxi_eats_nomenclature, experiments3, taxi_eats_nomenclature_monitor,
):
    await taxi_eats_nomenclature.tests_control(reset_metrics=True)
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

    await taxi_eats_nomenclature.tests_control(reset_metrics=True)
    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}',
        headers={'X-Device-Id': TEST_DEVICE_ID},
    )
    assert response.status == 200

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert metrics[METRICS_NAME] == {
        '$meta': {'solomon_children_labels': 'category_id'},
    }


@pytest.mark.config(EATS_NOMENCLATURE_ADVERTS=settings())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_more_categories.sql',
    ],
)
async def test_exp_with_requested_category(
        taxi_eats_nomenclature, experiments3, taxi_eats_nomenclature_monitor,
):
    await taxi_eats_nomenclature.tests_control(reset_metrics=True)
    experiments3.add_experiment(
        **make_adverts_experiment(make_exp_categories(True)),
    )

    await taxi_eats_nomenclature.tests_control(reset_metrics=True)
    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id=category_2_origin',
        headers=make_auth_headers(),
    )
    assert response.status == 200

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert metrics[METRICS_NAME] == {
        '$meta': {'solomon_children_labels': 'category_id'},
    }


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
