# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest


CONSTRUCTOR = {
    'blocks': [
        {
            'items': [
                {
                    'type': 'header',
                    'title_default': 'main_title',
                    'subtitle_field': 'dates_range',
                },
                {
                    'type': 'default',
                    'title_default': 'min_orders_title',
                    'fields': {'orders': 'min_orders'},
                    'title_optional': 'percent_title',
                    'fields_optional': {'orders': 'percent'},
                    'title_type_field': 'not_enuogh_orders_flag',
                },
                {
                    'type': 'default',
                    'title_default': 'orders_info',
                    'fields': {
                        'orders': 'success_orders',
                        'delta': 'success_orders_delta',
                    },
                    'image': {
                        'type': 'taxi_car',
                        'color_field': 'color_theme',
                    },
                },
                {
                    'type': 'default',
                    'title_default': 'orders_tag',
                    'fields': {
                        'tag': 'good_order_tag',
                        'tips': 'good_order_tips',
                    },
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                },
                {
                    'type': 'default',
                    'title_default': 'reports_info',
                    'fields': {'report': 'bad_order_report'},
                    'image': {
                        'type': 'dislike',
                        'color_field': 'color_negative',
                    },
                    'tooltip_field': 'alert_value',
                },
                {
                    'type': 'default',
                    'title_default': 'reports_info_miss',
                    'fields': {'report': 'bad_order_report'},
                },
                {
                    'type': 'default',
                    'title_default': 'reports_info',
                    'fields': {'report': 'bad_order_report_miss'},
                },
            ],
        },
        {
            'items': [
                {'type': 'separator'},
                {'type': 'image', 'image_url': 'title_image'},
                {'type': 'title', 'title_default': 'tag_title'},
                {
                    'type': 'text',
                    'title_field': 'comment_date',
                    'subtitle_field': 'comment_value',
                },
                {
                    'type': 'text',
                    'title_field': 'comment_date_miss',
                    'subtitle_field': 'comment_value_miss',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_clean',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                    'subdetail_field': 'tag_clean',
                    'sort_tag': 'ok',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_polite',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                    'subdetail_field': 'tag_polite',
                    'sort_tag': 'ok',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_music',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                    'subdetail_field': 'tag_music',
                    'sort_tag': 'ok',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_chat',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                    'subdetail_field': 'tag_chat',
                    'sort_tag': 'ok',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_smellycar',
                    'image': {
                        'type': 'dislike',
                        'color_field': 'color_negative',
                    },
                    'subdetail_field': 'tag_smellycar',
                    'sort_tag': 'bad',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_baddriving',
                    'image': {
                        'type': 'dislike',
                        'color_field': 'color_negative',
                    },
                    'subdetail_field': 'tag_baddriving',
                    'sort_tag': 'bad',
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_rudedriver',
                    'image': {
                        'type': 'dislike',
                        'color_field': 'color_negative',
                    },
                    'subdetail_field': 'tag_rudedriver',
                    'sort_tag': 'bad',
                },
                {
                    'type': 'icon_text',
                    'title_default': 'tag_percent',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                    'subdetail_field': 'tag_percent',
                },
                {'type': 'text', 'subtitle_field': 'message_feedback'},
            ],
        },
        {
            'items': [
                {'type': 'separator'},
                {'type': 'title', 'title_default': 'report_title'},
                {
                    'type': 'icon',
                    'title_default': 'tag_highspeed_good_2',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_cancel_good_2',
                    'image': {'type': 'like', 'color_field': 'color_theme'},
                },
                {
                    'type': 'icon',
                    'title_default': 'tag_cancel_bad_2',
                    'image': {
                        'type': 'dislike',
                        'color_field': 'color_negative',
                    },
                },
                {'type': 'text', 'subtitle_field': 'message_service'},
            ],
        },
    ],
}


@pytest.mark.config(
    QUALITY_CARD_MOCK_ALLOWED=False,
    QUALITY_CARD_YT_PATH='/mph_recs',
    QUALITY_CARD_YT_CLUSTERS=['yt-repl'],
)
@pytest.mark.parametrize(
    'unique_driver_id,constructor,expected_response',
    [
        ('543eac8978f3c2a8d798362d', CONSTRUCTOR, 'expected_response1.json'),
        ('543eac8978f3c2a8d7983111', CONSTRUCTOR, 'expected_response2.json'),
        (
            '543eac8978f3c2a8d798362d',
            {'blocks': [{'items': []}]},
            'expected_response3.json',
        ),
    ],
)
def test_quality_card(
        taxi_driver_protocol,
        config,
        load_json,
        yt_client,
        unique_driver_id,
        constructor,
        expected_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1369', 'session_1', 'Sasha')

    config.set_values(dict(QUALITY_CONSTRUCTOR=constructor))

    query = (
        '* FROM [//home/taxi/unstable/mph_recs] '
        'WHERE unique_driver_id = "' + unique_driver_id + '"'
    )
    yt_client.add_select_rows_response(query, 'yt_response.json')

    response = taxi_driver_protocol.get(
        '/driver/quality-card',
        params={'db': '1369', 'session': 'session_1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == load_json(expected_response)


@pytest.mark.config(QUALITY_CONSTRUCTOR=CONSTRUCTOR)
@pytest.mark.parametrize(
    'mock_json,expected_response',
    [
        (
            {
                'unique_driver_id': '543eac8978f3c2a8d798362d',
                'dates_range': '3 - 12 ??????????????',
                'not_enuogh_orders_flag': True,
                'min_orders': 25,
                'percent': 10,
                'success_orders': 138,
                'success_orders_delta': 20,
                'good_order_tag': 10,
                'good_order_tips': 2,
                'bad_order_report': 2,
                'alert_value': '???????????????? ???????????????? ???? ?????????? ?? ????????????',
                'comment_date': '6 ??????????????',
                'comment_value': '???????????????? ???????????? ?? ???????????? ????????????',
                'comment_date_miss': None,
                'comment_value_miss': None,
                'title_image': 'http://somelink.com',
                'tag_clean': 1,
                'tag_polite': 2,
                'tag_music': 7,
                'tag_chat': None,
                'tag_baddriving': 6,
                'tag_smellycar': 2,
                'tag_rudedriver': None,
                'tag_percent': '???? 7%',
                'message_feedback': '???????????????????????? ?????????????????? ??????????????????',
                'tag_highspeed_good_2': True,
                'tag_cancel_good_2': None,
                'tag_cancel_bad_2': True,
                'message_service': '???????????????????????? ?????????????????? ??????????????????',
                'color_theme': '#AABBCC',
                'color_negative': '#AABBDD',
                'bad_order_report_miss': None,
                'min_orders_title': 'min_orders_title',
                'orders_info': 'orders_info',
                'orders_tag': 'orders_tag',
                'reports_info': 'reports_info',
                'reports_info_miss': None,
            },
            'expected_response1.json',
        ),
        ({}, 'expected_response2.json'),
    ],
)
def test_quality_card_mock(
        taxi_driver_protocol,
        load_json,
        config,
        mock_json,
        expected_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1369', 'session_1', 'Sasha')

    config.set_values(dict(QUALITY_CARD_MOCK_JSON=mock_json))

    response = taxi_driver_protocol.get(
        '/driver/quality-card',
        params={'db': '1369', 'session': 'session_1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == load_json(expected_response)


@pytest.mark.config(
    QUALITY_CARD_MOCK_ALLOWED=False,
    QUALITY_CARD_YT_PATH='/mph_recs',
    QUALITY_CARD_YT_CLUSTERS=['yt-repl'],
)
@pytest.mark.parametrize(
    'yt_prefix,constructor,expected_response,mode, unique_driver_id',
    [
        (
            'natasha2',
            CONSTRUCTOR,
            'expected_response5.json',
            'new_way',
            '543eac8978f3c2a8d798362a',
        ),
    ],
)
def test_unique_driver_from_license_pd_id(
        taxi_driver_protocol,
        config,
        load_json,
        yt_client,
        yt_prefix,
        constructor,
        expected_response,
        driver_authorizer_service,
        mode,
        unique_driver_id,
):
    session = 'session_natasha'
    db = '1369'
    driver_authorizer_service.set_session(db, session, 'Natasha')

    config.set_values(
        dict(
            FEATURE_GET_DRIVER_BY_LICENSE_PD_ID={'mode': mode},
            QUALITY_CONSTRUCTOR=constructor,
        ),
    )

    query = (
        '* FROM [//home/taxi/unstable/mph_recs] '
        'WHERE unique_driver_id = "' + unique_driver_id + '"'
    )
    yt_client.add_select_rows_response(query, yt_prefix + '_yt_response.json')

    response = taxi_driver_protocol.get(
        '/driver/quality-card',
        params={'db': db, 'session': session},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == load_json(expected_response)
