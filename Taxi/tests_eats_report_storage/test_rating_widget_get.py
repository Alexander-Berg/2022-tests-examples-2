# flake8: noqa
# pylint: disable=redefined-outer-name, import-only-modules

from typing import Text
import pytest
import dataclasses

from .conftest import (
    make_rating_response,
    make_ratings_response,
    make_place_rating,
)

PARTNER_ID = 1
PLACE_ID = 1

UNAVAILABLE_TEMPLATER_CONFIG = {
    'templates': [
        {'slug': 'unavailable_widget_rating', 'template': 'Не хватает оценок'},
        {
            'slug': 'unavailable_widget_cancel_rating',
            'template': 'Не хватает оценок отмен',
        },
    ],
}

COMMON_WIDGETS_TEMPLATER_CONFIG = {
    'widgets': [
        {
            'chart_type': 'sum_with_delta',
            'description': '',
            'metrics': ['rating_average'],
            'title': 'Общий рейтинг',
            'unvailable_widget_text': 'template:unavailable_widget_rating',
            'widget_id': 'quality_place_raiting_sum_with_delta',
            'widget_type': 'widget_basic_chart',
        },
        {
            'chart_type': 'sum_with_delta',
            'description': '',
            'metrics': ['rating_cancel'],
            'title': 'Рейтинг отмен',
            'unvailable_widget_text': (
                'template:unavailable_widget_cancel_rating'
            ),
            'widget_id': 'quality_cancel_raiting_sum_with_delta',
            'widget_type': 'widget_basic_chart',
        },
    ],
}


@dataclasses.dataclass
class Threshold:
    value: float
    title_template: str
    text_template: str


def make_threshold(value, title_template='', text_template=''):
    return Threshold(value, title_template, text_template)


def get_rating_thresholds_configs(
        m_value_a: float, l_value_a: float, m_value_c: float, l_value_c: float,
):
    return pytest.mark.experiments3(
        name='eats_report_storage_rating_thresholds',
        consumers=['eats_report_storage/partner_id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'rating_average': {
                        'high': {
                            'data': {
                                'title_template': 'Выше',
                                'text_template': 'Превосходно',
                                'slug_link': 'link_1',
                            },
                        },
                        'middle': {
                            'value': m_value_a,
                            'data': {
                                'title_template': 'Ниже',
                                'text_template': 'Можно лучше',
                                'slug_link': 'link_2',
                            },
                        },
                        'low': {
                            'value': l_value_a,
                            'data': {
                                'title_template': 'ниже',
                                'text_template': 'Все плохо',
                                'slug_link': 'link_3',
                            },
                        },
                    },
                    'rating_cancel': {
                        'high': {
                            'data': {
                                'title_template': 'Выше о',
                                'text_template': 'Превосходно о',
                                'slug_link': 'link_cancel_1',
                            },
                        },
                        'middle': {
                            'value': m_value_c,
                            'data': {
                                'title_template': 'Ниже о',
                                'text_template': 'Можно лучше о',
                                'slug_link': 'link_cancel_2',
                            },
                        },
                        'low': {
                            'value': l_value_c,
                            'data': {
                                'title_template': 'ниже о',
                                'text_template': 'Все плохо о',
                                'slug_link': 'link_cancel_3',
                            },
                        },
                    },
                },
            },
        ],
        is_config=True,
    )


@pytest.mark.parametrize(
    'widget_slug, places_rating_info, text, total_value, delta_value',
    [
        (
            'quality_place_raiting_sum_with_delta',
            make_rating_response(show_rating=True),
            None,
            {'title': '4.1', 'value': 4.1},
            {'title': '1.6', 'value': -1.6},
        ),
        (
            'quality_cancel_raiting_sum_with_delta',
            make_rating_response(show_rating=True),
            None,
            {'title': '5', 'value': 5},
            {'title': '0', 'value': 0},
        ),
        (
            'quality_place_raiting_sum_with_delta',
            make_rating_response(show_rating=False),
            'мало оценок',
            None,
            None,
        ),
        (
            'quality_cancel_raiting_sum_with_delta',
            make_rating_response(show_rating=False),
            '—',
            None,
            None,
        ),
        (
            'quality_place_raiting_sum_with_delta',
            {'places_rating_info': []},
            'мало оценок',
            None,
            None,
        ),
        (
            'quality_cancel_raiting_sum_with_delta',
            {'places_rating_info': []},
            '—',
            None,
            None,
        ),
    ],
)
async def test_service_return_rating_metrics_or_unavailable_text(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
        widget_slug,
        places_rating_info,
        text,
        total_value,
        delta_value,
):
    rating_response.set_data(places_rating_info)
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [PLACE_ID],
            'preset_period_type': 'week',
        },
    )
    assert response.status_code == 200
    charts = response.json()['payload']['charts']
    if not text:
        assert len(charts) == 1
        assert charts[0]['total_value'] == total_value
        assert charts[0]['delta_value'] == delta_value
    else:
        assert charts == text


@pytest.mark.config(
    EATS_REPORT_STORAGE_TEXT_TEMPLATER=UNAVAILABLE_TEMPLATER_CONFIG,
    EATS_REPORT_STORAGE_COMMON_WIDGETS=COMMON_WIDGETS_TEMPLATER_CONFIG,
)
@pytest.mark.parametrize(
    'widget_slug, text, period',
    [
        ('quality_place_raiting_sum_with_delta', 'Не хватает оценок', 'week'),
        (
            'quality_cancel_raiting_sum_with_delta',
            'Не хватает оценок отмен',
            'week',
        ),
    ],
)
async def test_service_return_rating_unavailable_text_with_templater(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
        widget_slug,
        text,
        period,
):
    rating_response.set_data({'places_rating_info': []})
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [PLACE_ID],
            'preset_period_type': period,
        },
    )
    assert response.status_code == 200
    charts = response.json()['payload']['charts']
    assert charts == text


@get_rating_thresholds_configs(4.2, 2.2, 3.3, 1.2)
@pytest.mark.parametrize(
    'widget_slug, places_rating_info, text, title_value,'
    'total_value, delta_value, text_ref, link, places',
    [
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 4.4, 5.0),
                    make_place_rating(2, 4.3, 5.0),
                    make_place_rating(3, 4.5, 5.0),
                    make_place_rating(4, 4.6, 5.0),
                    make_place_rating(5, 4.7, 5.0),
                    make_place_rating(6, 4.8, 5.0),
                ],
            ),
            None,
            'Выше',
            {'title': '6', 'value': 6.0},
            {'title': '', 'value': 1.0},
            {'title': 'Превосходно', 'value': 0},
            {'text': '', 'slug': 'link_1'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_more_max_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 3.4, 5.0),
                    make_place_rating(2, 3.5, 5.0),
                    make_place_rating(3, 3.8, 5.0),
                    make_place_rating(4, 3.6, 5.0),
                    make_place_rating(5, 3.9, 5.0),
                    make_place_rating(6, 3.2, 5.0),
                ],
            ),
            None,
            'Ниже',
            {'title': '6', 'value': 6.0},
            {'title': '', 'value': 1.0},
            {'title': 'Можно лучше', 'value': 0},
            {'text': '', 'slug': 'link_2'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_more_all_middle_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 1.4, 5.0),
                    make_place_rating(2, 1.5, 5.0),
                    make_place_rating(3, 1.8, 5.0),
                    make_place_rating(4, 1.6, 5.0),
                    make_place_rating(5, 1.9, 5.0),
                    make_place_rating(6, 1.2, 5.0),
                ],
            ),
            None,
            'ниже',
            {'title': '6', 'value': 6.0},
            {'title': '', 'value': -1.0},
            {'title': 'Все плохо', 'value': 0},
            {'text': '', 'slug': 'link_3'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_more_all_min_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 3.4, 5.0),
                    make_place_rating(2, 4.5, 5.0),
                    make_place_rating(3, 4.8, 5.0),
                    make_place_rating(4, 3.6, 5.0),
                    make_place_rating(5, 1.9, 5.0),
                    make_place_rating(6, 1.2, 5.0),
                ],
            ),
            None,
            'ниже',
            {'title': '2', 'value': 2.0},
            {'title': '', 'value': -1.0},
            {'title': 'Все плохо', 'value': 0},
            {'text': '', 'slug': 'link_3'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_more_2_min_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 4.4, 5.0),
                    make_place_rating(2, 4.5, 5.0),
                    make_place_rating(3, 4.8, 5.0),
                    make_place_rating(4, 3.1, 5.0),
                    make_place_rating(5, 2.9, 5.0),
                    make_place_rating(6, 4.3, 5.0),
                ],
            ),
            None,
            'Ниже',
            {'title': '2', 'value': 2.0},
            {'title': '', 'value': 1.0},
            {'title': 'Можно лучше', 'value': 0},
            {'text': '', 'slug': 'link_2'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_more_2_middle_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 4.4, 5.0),
                    make_place_rating(2, 4.5, 5.0, False),
                    make_place_rating(3, 4.8, 5.0, False),
                    make_place_rating(4, 3.6, 5.0, False),
                    make_place_rating(5, 2.9, 5.0, False),
                    make_place_rating(6, 2.3, 5.0, False),
                ],
            ),
            None,
            'Выше',
            {'title': '1', 'value': 1.0},
            {'title': '', 'value': 1.0},
            {'title': 'Превосходно', 'value': 0},
            {'text': '', 'slug': 'link_1'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_only_1_show_rating_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 4.4, 5.0),
                    make_place_rating(2, 4.5, 5.0),
                    make_place_rating(3, 4.8, 5.0, False),
                    make_place_rating(4, 3.6, 5.0, False),
                    make_place_rating(5, 2.9, 5.0, False),
                    make_place_rating(6, 2.3, 5.0, False),
                ],
            ),
            None,
            'Выше',
            {'title': '2', 'value': 2.0},
            {'title': '', 'value': 1.0},
            {'title': 'Превосходно', 'value': 0},
            {'text': '', 'slug': 'link_1'},
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_only_2_show_rating_thresholds',
        ),
        pytest.param(
            'quality_place_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 4.4, 5.0, False),
                    make_place_rating(2, 4.5, 5.0, False),
                    make_place_rating(3, 4.8, 5.0, False),
                    make_place_rating(4, 3.6, 5.0, False),
                    make_place_rating(5, 2.9, 5.0, False),
                    make_place_rating(6, 2.3, 5.0, False),
                ],
            ),
            'мало оценок',
            None,
            None,
            None,
            None,
            None,
            [1, 2, 3, 4, 5, 6],
            id='all_ratings_show_false',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 5.0),
                    make_place_rating(2, 5.0, 4.8),
                    make_place_rating(3, 5.0, 4.5),
                    make_place_rating(4, 5.0, 4.2),
                    make_place_rating(5, 5.0, 3.8),
                    make_place_rating(6, 5.0, 3.5),
                ],
            ),
            None,
            'Выше о',
            {'title': '6', 'value': 6.0},
            {'title': '', 'value': 1.0},
            {'title': 'Превосходно о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_1'},
            [1, 2, 3, 4, 5, 6],
            id='all_canel_ratings_more_max_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 3.2),
                    make_place_rating(2, 5.0, 3.1),
                    make_place_rating(3, 5.0, 2.0),
                    make_place_rating(4, 5.0, 1.8),
                    make_place_rating(5, 5.0, 1.5),
                    make_place_rating(6, 5.0, 1.3),
                ],
            ),
            None,
            'Ниже о',
            {'title': '6', 'value': 6.0},
            {'title': '', 'value': 1.0},
            {'title': 'Можно лучше о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_2'},
            [1, 2, 3, 4, 5, 6],
            id='all_cancel_ratings_more_all_middle_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 1.19),
                    make_place_rating(2, 5.0, 1.1),
                    make_place_rating(3, 5.0, 1.0),
                    make_place_rating(4, 5.0, 0.8),
                    make_place_rating(5, 5.0, 0.5),
                    make_place_rating(6, 5.0, 0.3),
                ],
            ),
            None,
            'ниже о',
            {'title': '6', 'value': 6.0},
            {'title': '', 'value': -1.0},
            {'title': 'Все плохо о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_3'},
            [1, 2, 3, 4, 5, 6],
            id='cancel_ratings_more_all_min_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 1.2),
                    make_place_rating(2, 5.0, 1.1),
                    make_place_rating(3, 5.0, 0.7),
                    make_place_rating(4, 5.0, 3.5),
                    make_place_rating(5, 5.0, 4.5),
                    make_place_rating(6, 5.0, 4.3),
                ],
            ),
            None,
            'ниже о',
            {'title': '2', 'value': 2.0},
            {'title': '', 'value': -1.0},
            {'title': 'Все плохо о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_3'},
            [1, 2, 3, 4, 5, 6],
            id='cancel_ratings_more_2_min_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 3.2),
                    make_place_rating(2, 5.0, 2.1),
                    make_place_rating(3, 5.0, 3.0),
                    make_place_rating(4, 5.0, 3.5),
                    make_place_rating(5, 5.0, 4.5),
                    make_place_rating(6, 5.0, 4.3),
                ],
            ),
            None,
            'Ниже о',
            {'title': '3', 'value': 3.0},
            {'title': '', 'value': 1.0},
            {'title': 'Можно лучше о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_2'},
            [1, 2, 3, 4, 5, 6],
            id='cancel_ratings_more_3_middle_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 3.2),
                    make_place_rating(2, 5.0, 2.1, False),
                    make_place_rating(3, 5.0, 3.0, False),
                    make_place_rating(4, 5.0, 3.5, False),
                    make_place_rating(5, 5.0, 4.5, False),
                    make_place_rating(6, 5.0, 4.3, False),
                ],
            ),
            None,
            'Ниже о',
            {'title': '1', 'value': 1.0},
            {'title': '', 'value': 1.0},
            {'title': 'Можно лучше о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_2'},
            [1, 2, 3, 4, 5, 6],
            id='cancel_ratings_only_1_show_rating_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 5.0, 4.2),
                    make_place_rating(2, 5.0, 3.8),
                    make_place_rating(3, 5.0, 3.0, False),
                    make_place_rating(4, 5.0, 3.5, False),
                    make_place_rating(5, 5.0, 4.5, False),
                    make_place_rating(6, 5.0, 4.3, False),
                ],
            ),
            None,
            'Выше о',
            {'title': '2', 'value': 2.0},
            {'title': '', 'value': 1.0},
            {'title': 'Превосходно о', 'value': 0},
            {'text': '', 'slug': 'link_cancel_1'},
            [1, 2, 3, 4, 5, 6],
            id='cancel_ratings_only_2_show_rating_thresholds',
        ),
        pytest.param(
            'quality_cancel_raiting_sum_with_delta',
            make_ratings_response(
                [
                    make_place_rating(1, 4.4, 5.0, False),
                    make_place_rating(2, 4.5, 5.0, False),
                    make_place_rating(3, 4.8, 5.0, False),
                    make_place_rating(4, 3.6, 5.0, False),
                    make_place_rating(5, 2.9, 5.0, False),
                    make_place_rating(6, 2.3, 5.0, False),
                ],
            ),
            '—',
            None,
            None,
            None,
            None,
            None,
            [1, 2, 3, 4, 5, 6],
            id='cancel_ratings_all_show_false',
        ),
    ],
)
async def test_service_return_rating_multi_places(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        rating_response,
        widget_slug,
        places_rating_info,
        text,
        title_value,
        total_value,
        delta_value,
        text_ref,
        link,
        places,
):
    rating_response.set_data(places_rating_info)
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': places,
            'preset_period_type': 'week',
        },
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    charts = payload['charts']
    if 'restapp_link' in payload:
        assert payload['restapp_link'] == link
    if not text:
        assert len(charts) == 1
        assert payload['title'] == title_value
        assert charts[0]['name'] == title_value
        assert charts[0]['total_value'] == total_value
        assert charts[0]['delta_value'] == delta_value
        if 'reference_value' in charts[0]:
            assert charts[0]['reference_value'] == text_ref
    else:
        assert charts == text
