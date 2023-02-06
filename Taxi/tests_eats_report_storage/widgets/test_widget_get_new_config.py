# pylint: disable=import-only-modules

import pytest

from tests_eats_report_storage.conftest import exp3_config_metrics
from tests_eats_report_storage.conftest import exp3_config_switch_flag
from tests_eats_report_storage.conftest import exp3_config_widgets
from tests_eats_report_storage.conftest import make_rating_response
from tests_eats_report_storage.widgets.utils import consts
from tests_eats_report_storage.widgets.utils import helpers


CONFIG_WIDGET_ADVERT_GMV = {
    'chart_type': 'no_data',
    'description': '',
    'html': 'Тест html',
    'layout': {
        'desktop': [
            [
                'advert_gmv_line_with_delta',
                'advert_first_gmv_line_with_delta',
                'quality_place_raiting_sum_with_delta',
            ],
        ],
        'mobile': [
            ['advert_gmv_line_with_delta'],
            [
                'advert_first_gmv_line_with_delta',
                'quality_place_raiting_sum_with_delta',
            ],
        ],
    },
    'metrics': [],
    'stretch_to_full_width': False,
    'title': '',
    'widget_id': 'advert_gmv',
    'widget_type': 'recursive',
}

CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET = {
    'chart_type': 'line_with_delta',
    'description': '',
    'metrics': ['advert_organic_returner_from_ad_gmv'],
    'title': 'Повторные',
    'widget_id': 'advert_gmv_line_with_delta',
}

CONFIG_WIDGET_ADVERT_FIRST_GMV = {
    'chart_type': 'line_with_delta',
    'description': '',
    'metrics': ['advert_ad_gmv'],
    'title': 'Заказы по рекламе',
    'widget_id': 'advert_first_gmv_line_with_delta',
}

CONFIG_WIDGET_QUALITY = {
    'chart_type': 'line_with_delta',
    'description': '',
    'metrics': ['rating_average'],
    'title': 'Рейтинг',
    'widget_id': 'quality_place_raiting_sum_with_delta',
}

CONFIG_METRIC_ADVERT_ORGANIC = {
    'data_key': 'advert_organic_returner_from_ad_gmv',
    'granularity': ['day', 'week', 'month'],
    'inverse': True,
    'metric_id': 'advert_organic_returner_from_ad_gmv',
    'name': 'Повторные заказы',
    'periods': ['week', 'month', 'year', 'custom'],
    'permissions': ['permission.stats.advert'],
    'simbols_after_comma': 2,
    'value_unit_sign': '₽',
}

CONFIG_METRIC_ADVERT_AD_GMV = {
    'data_key': 'advert_ad_gmv',
    'granularity': ['day', 'week', 'month'],
    'inverse': True,
    'metric_id': 'advert_ad_gmv',
    'name': 'Заказы по рекламе',
    'periods': ['week', 'month', 'year', 'custom'],
    'permissions': ['permission.stats.advert'],
    'simbols_after_comma': 2,
    'value_unit_sign': '₽',
}

CONFIG_METRIC_RATING_AVERAGE = {
    'data_key': 'rating_average',
    'granularity': ['hour', 'day', 'week', 'month'],
    'metric_id': 'rating_average',
    'name': 'Общий рейтинг',
    'periods': ['week', 'month', 'year', 'custom'],
    'permissions': ['other_permission'],
    'simbols_after_comma': 1,
}


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_advert_stats.sql',),
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_PLUS_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_PLUS_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
            ],
            id='metrics_and_widget_only_old_config',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_PLUS_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_PLUS_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_switch_flag('old'),
            ],
            id='metrics_and_widget_only_old_config_old',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_PLUS_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_PLUS_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_and_widget_only_old_config_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_ADVERT_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_first_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                    ],
                ),
            ],
            id='metrics_and_widget_everywhere_in_configs',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_ADVERT_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_first_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                    ],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_and_widget_everywhere_in_configs_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_ADVERT_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_first_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                    ],
                ),
                exp3_config_switch_flag('old'),
            ],
            id='metrics_and_widget_everywhere_in_configs_old',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={
                        'metrics': [CONFIG_METRIC_RATING_AVERAGE],
                    },
                    EATS_REPORT_STORAGE_ADVERT_METRICS={
                        'metrics': [
                            CONFIG_METRIC_ADVERT_AD_GMV,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_first_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                    ],
                ),
                exp3_config_switch_flag('new'),
            ],
            id='metrics_and_widget_everywhere_in_configs_new',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={
                        'widgets': [CONFIG_WIDGET_QUALITY],
                    },
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={
                        'widgets': [
                            CONFIG_WIDGET_ADVERT_GMV,
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ],
                    },
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='only_widgets_in_old_config',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_ADVERT_METRICS={
                        'metrics': [
                            CONFIG_METRIC_RATING_AVERAGE,
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ],
                    },
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={
                        'widgets': [CONFIG_WIDGET_ADVERT_FIRST_GMV],
                    },
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                    ],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='mix_old_and_new_metrics_and_configs',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={'metrics': []},
                    EATS_REPORT_STORAGE_ADVERT_METRICS={'metrics': []},
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={'widgets': []},
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={'widgets': []},
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_first_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                    ],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='only_new_configs_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_COMMON_METRICS={'metrics': []},
                    EATS_REPORT_STORAGE_ADVERT_METRICS={'metrics': []},
                    EATS_REPORT_STORAGE_COMMON_WIDGETS={'widgets': []},
                    EATS_REPORT_STORAGE_ADVERT_WIDGETS={'widgets': []},
                ),
                exp3_config_metrics(
                    [
                        ('rating_average', CONFIG_METRIC_RATING_AVERAGE),
                        ('advert_ad_gmv', CONFIG_METRIC_ADVERT_AD_GMV),
                        (
                            'advert_organic_returner_from_ad_gmv',
                            CONFIG_METRIC_ADVERT_ORGANIC,
                        ),
                    ],
                ),
                exp3_config_widgets(
                    [
                        (
                            'quality_place_raiting_sum_with_delta',
                            CONFIG_WIDGET_QUALITY,
                        ),
                        (
                            'advert_first_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_FIRST_GMV,
                        ),
                        ('advert_gmv', CONFIG_WIDGET_ADVERT_GMV),
                        (
                            'advert_gmv_line_with_delta',
                            CONFIG_WIDGET_ADVERT_GMV_LWD_WIDGET,
                        ),
                    ],
                ),
                exp3_config_switch_flag('new'),
            ],
            id='only_new_configs_merge_new',
        ),
    ],
)
async def test_recursive_widget_with_new_configs(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        mock_core_places_info_request,
        rating_response,
        pgsql,
):
    rating_response.set_data(make_rating_response(show_rating=True))
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'advert_gmv',
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    widget = response.json()['payload']
    assert not widget['charts']
    assert widget['widget_type'] == 'recursive'
    assert widget['chart_type'] == 'no_data'
    assert len(widget['subwidgets']) == 3
    for subwidget in widget['subwidgets']:
        if subwidget['widget_slug'] in [
                'advert_gmv_line_with_delta',
                'advert_first_gmv_line_with_delta',
        ]:
            helpers.check_data_count(subwidget, 1, 3)
            helpers.check_data(
                subwidget,
                None,
                ['6.60 ₽'],
                ['2.20 ₽'],
                [[3.3], [2.2], [1.1]],
                None,
                None,
                None,
                None,
            )
        elif (
            subwidget['widget_slug'] == 'quality_place_raiting_sum_with_delta'
        ):
            helpers.check_data_count(subwidget, 1, 0)
            helpers.check_data(
                subwidget, None, ['4.1'], ['1.6'], [], None, None, None, None,
            )
    assert widget['layout']['desktop'] == [
        [
            'advert_gmv_line_with_delta',
            'advert_first_gmv_line_with_delta',
            'quality_place_raiting_sum_with_delta',
        ],
    ]
    assert widget['layout']['mobile'] == [
        ['advert_gmv_line_with_delta'],
        [
            'advert_first_gmv_line_with_delta',
            'quality_place_raiting_sum_with_delta',
        ],
    ]
