# flake8: noqa
# pylint: disable=redefined-outer-name, import-only-modules
import pytest

from .conftest import exp3_config_multi_places

EATS_CORE_RESPONSE = [
    {
        'id': 1,
        'name': 'Нунануна',
        'available': True,
        'currency': {'code': 'JPY', 'sign': '¥', 'decimal_places': 2},
        'country_code': 'JP',
        'show_shipping_time': False,
        'integration_type': 'native',
        'slug': 'nunanuna',
    },
    {
        'id': 2,
        'name': 'Нунануна',
        'available': True,
        'currency': {'code': 'JPY', 'sign': '¥', 'decimal_places': 2},
        'country_code': 'JP',
        'show_shipping_time': False,
        'integration_type': 'native',
        'slug': 'nunanuna',
    },
    {
        'id': 5,
        'name': 'Нунануна',
        'available': True,
        'currency': {'code': 'JPY', 'sign': '¥', 'decimal_places': 2},
        'country_code': 'JP',
        'show_shipping_time': False,
        'integration_type': 'native',
        'slug': 'nunanuna',
    },
]


def make_create_config_suggest(slug, arg_name, arg_type, value, pred_type):
    return {
        'suggest_slug': slug,
        'icon_slug': 'icon_slug_{}'.format(slug),
        'section_slug': 'section_slug_sel_{}'.format(slug),
        'suggest_text': {'text': '{}_text'.format(slug), 'params': []},
        'title': 'Title {}'.format(slug),
        'button_title': '{}_btn'.format(slug),
        'predicates': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'value': value,
                            'arg_name': arg_name,
                            'arg_type': arg_type,
                        },
                        'type': pred_type,
                    },
                ],
            },
            'type': 'any_of',
        },
    }


def make_create_config_suggest_icon(
        slug,
        arg_name,
        arg_type,
        value,
        pred_type,
        value_type='absolute',
        target=None,
):
    return {
        'suggest_slug': slug,
        'icon_slug': 'icon_slug_{}'.format(slug),
        'dynamic_icon': {
            'max_value': value,
            'value_unit_sign': '₽',
            'local_value_unit': 'currency',
            'symbols_after_comma': 2,
            'arg_name': arg_name,
            'value_type': value_type,
            'target': target,
        },
        'section_slug': 'section_slug_sel_{}'.format(slug),
        'suggest_text': {'text': '{}_text'.format(slug), 'params': []},
        'title': 'Title {}'.format(slug),
        'button_title': '{}_btn'.format(slug),
        'predicates': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'value': value,
                            'arg_name': arg_name,
                            'arg_type': arg_type,
                        },
                        'type': pred_type,
                    },
                ],
            },
            'type': 'any_of',
        },
    }


def make_config_suggest_template(slug, arg_name, arg_type, value, pred_type):
    return {
        'suggest_slug': slug,
        'icon_slug': 'icon_slug_{}'.format(slug),
        'section_slug': 'section_slug_sel_{}'.format(slug),
        'suggest_text': {'text': '{}_text'.format(slug), 'params': []},
        'suggest_template_slug': 'template:template_{}_slug'.format(slug),
        'title': 'Title {}'.format(slug),
        'button_title': '{}_btn'.format(slug),
        'predicates': {
            'init': {
                'predicates': [
                    {
                        'init': {
                            'value': value,
                            'arg_name': arg_name,
                            'arg_type': arg_type,
                        },
                        'type': pred_type,
                    },
                ],
            },
            'type': 'any_of',
        },
    }


def make_create_suggest(slug, place_id):
    return {
        'button': {
            'slug': 'section_slug_sel_{}'.format(slug),
            'text': '{}_btn'.format(slug),
        },
        'description': '{}_text'.format(slug),
        'icon_slug': 'icon_slug_{}'.format(slug),
        'place_id': place_id,
        'title': 'Title {}'.format(slug),
    }


def make_suggest_icon_percent(slug, place_id, value, max_value, percents):
    return {
        'button': {
            'slug': 'section_slug_sel_{}'.format(slug),
            'text': '{}_btn'.format(slug),
        },
        'dynamic_icon': {
            'value': value,
            'display': '{:.0f} %'.format(percents),
            'limit': max_value,
        },
        'description': '{}_text'.format(slug),
        'icon_slug': 'icon_slug_{}'.format(slug),
        'place_id': place_id,
        'title': 'Title {}'.format(slug),
    }


def make_create_suggest_icon(slug, place_id, value, max_value, target=None):
    data = {
        'button': {
            'slug': 'section_slug_sel_{}'.format(slug),
            'text': '{}_btn'.format(slug),
        },
        'dynamic_icon': {
            'value': value,
            'display': '{:.2f} ¥'.format(value),
            'limit': max_value,
        },
        'description': '{}_text'.format(slug),
        'icon_slug': 'icon_slug_{}'.format(slug),
        'place_id': place_id,
        'title': 'Title {}'.format(slug),
    }
    if target is not None:
        data['dynamic_icon']['target'] = target
    return data


def make_create_suggest_template(slug, place_id):
    return {
        'button': {
            'slug': 'section_slug_sel_{}'.format(slug),
            'text': '{}_btn'.format(slug),
        },
        'description': 'template_{}_text'.format(slug),
        'icon_slug': 'icon_slug_{}'.format(slug),
        'place_id': place_id,
        'title': 'Title {}'.format(slug),
    }


def make_create_template(slug):
    return {
        'slug': 'template_{}_slug'.format(slug),
        'template': 'template_{}_text'.format(slug),
    }


def make_group(slug, number_of_displays_in_group, suggests):
    return {
        'group_slug': slug,
        'number_of_displays_in_group': number_of_displays_in_group,
        'suggests': suggests,
    }


@pytest.mark.pgsql('eats_report_storage', files=['insert_data_suggest.sql'])
@pytest.mark.parametrize(
    'place_ids,result',
    [
        pytest.param(
            [1],
            [],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_1_empty',
        ),
        pytest.param(
            [1],
            [],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_1_empty_conf',
        ),
        pytest.param(
            [1],
            [make_create_suggest('more_photos', 1)],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_1_more_photos',
        ),
        pytest.param(
            [1],
            [make_create_suggest('more_photos', 1)],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_1_more_photos',
        ),
        pytest.param(
            [2],
            [
                make_create_suggest('low_rating', 2),
                make_create_suggest('more_photos', 2),
            ],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_2_low_rating_and_more_photos',
        ),
        pytest.param(
            [3],
            [
                make_create_suggest('more_photos', 3),
                make_create_suggest('low_rating', 3),
            ],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_3_low_rating_and_more_photos_priority',
        ),
        pytest.param(
            [4],
            [],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_4_all_suggest_false',
        ),
        pytest.param(
            [1, 2, 3, 4],
            [
                make_create_suggest('more_photos', 1),
                make_create_suggest('low_rating', 2),
                make_create_suggest('more_photos', 2),
                make_create_suggest('more_photos', 3),
                make_create_suggest('low_rating', 3),
            ],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='place_id_4_some_suggests_are_not_false',
        ),
        pytest.param(
            [1, 2],
            [
                make_create_suggest('discount_flg', 1),
                make_create_suggest('more_photos', 1),
                make_create_suggest('low_rating', 2),
                make_create_suggest('more_photos', 2),
                make_create_suggest('discount_flg', 2),
            ],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        4.0,
                                        'lt',
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                            make_group(
                                'create_promo',
                                1,
                                [
                                    make_create_config_suggest(
                                        'dish_as_gift_flg',
                                        'dish_as_gift_flg',
                                        'bool',
                                        False,
                                        'eq',
                                    ),
                                    make_create_config_suggest(
                                        'discount_flg',
                                        'discount_flg',
                                        'bool',
                                        False,
                                        'eq',
                                    ),
                                    make_create_config_suggest(
                                        'second_for_free_flg',
                                        'second_for_free_flg',
                                        'bool',
                                        False,
                                        'eq',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='limit_group_suggests',
        ),
        pytest.param(
            [1, 2],
            [
                make_create_suggest('more_photos', 1),
                make_create_suggest_icon('low_rating', 2, 3.4, 5.0, 4.3),
                make_create_suggest('more_photos', 2),
            ],
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest_icon(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        5.0,
                                        'lt',
                                        'absolute',
                                        4.3,
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='group_suggests_dynamic_icons',
        ),
        pytest.param(
            [1, 2],
            [
                make_create_suggest('more_photos', 1),
                make_create_suggest_icon('low_rating', 2, 3.4, 5.0, 4.3),
                make_create_suggest('more_photos', 2),
            ],
            marks=[
                exp3_config_multi_places(),
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest_icon(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        5.0,
                                        'lt',
                                        'absolute',
                                        4.3,
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='group_suggests_disable_multi_suggests_false',
        ),
        pytest.param(
            [1, 2],
            [],
            marks=[
                exp3_config_multi_places(disable_in_suggests=True),
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest_icon(
                                        'low_rating',
                                        'rating',
                                        'double',
                                        5.0,
                                        'lt',
                                        'absolute',
                                        4.3,
                                    ),
                                    make_create_config_suggest(
                                        'more_photos',
                                        'pict_share',
                                        'double',
                                        6.2,
                                        'gt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='group_suggests_disable_multi_suggests_true',
        ),
        pytest.param(
            [5],
            [make_create_suggest('low_cancel_rating', 5)],
            marks=[
                exp3_config_multi_places(),
                pytest.mark.config(
                    EATS_REPORT_STORAGE_DASHBOARD_GROUPED_SUGGESTS={
                        'groups': [
                            make_group(
                                'common_group',
                                None,
                                [
                                    make_create_config_suggest(
                                        'low_cancel_rating',
                                        'cancel_rating',
                                        'double',
                                        2.5,
                                        'lt',
                                    ),
                                ],
                            ),
                        ],
                        'permissions': ['permission.dashboard.suggests'],
                    },
                ),
            ],
            id='group_suggests_cancel_rating',
        ),
    ],
)
async def test_requests_grouped_suggest(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mockserver,
        place_ids,
        result,
):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_core(request):
        return mockserver.make_response(
            status=200, json={'payload': EATS_CORE_RESPONSE},
        )

    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-suggests?place_ids={}'.format(
            ','.join(str(x) for x in place_ids),
        ),
        headers={'X-YaEda-PartnerId': str(1)},
    )
    assert response.json()['suggests'] == result
