from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from test_rida import experiments_utils
from test_rida import helpers


@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_extra.sql'])
@pytest.mark.parametrize(
    ['user_id', 'expected_response_json_path'],
    [
        pytest.param(1234, 'user_wo_driver.json', id='user_without_driver'),
        pytest.param(1449, 'user_with_driver.json', id='user_with_driver'),
        pytest.param(
            1448,
            'user_with_driver_and_permit.json',
            id='user_with_driver_and_permit',
        ),
    ],
)
async def test_get_profile_data(
        web_app_client,
        load_json,
        user_id: int,
        expected_response_json_path: str,
):
    response = await web_app_client.post(
        '/v1/getProfileData',
        headers=helpers.get_auth_headers(user_id=user_id),
    )
    assert response.status == 200
    response_json = await response.json()
    expected_response_json = load_json(expected_response_json_path)
    assert response_json == expected_response_json


def get_profile_info_mark(
        user_id: int,
        passenger_unit_templates: List[Dict[str, Any]],
        driver_unit_templates: List[Dict[str, Any]],
):
    if user_id == 1234:
        args = experiments_utils.get_default_user_args()
    elif user_id == 1448:
        args = experiments_utils.get_default_user_args(
            user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
        )
    elif user_id == 1449:
        args = experiments_utils.get_default_user_args(
            user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
        )
    else:
        raise ValueError('Unknown user')

    exp3_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_profile_info_templates',
        args=args,
        value={
            'recent_window_size_days': 7,
            'passenger_unit_templates': passenger_unit_templates,
            'driver_unit_templates': driver_unit_templates,
        },
    )
    return exp3_mark


@pytest.mark.now('2022-02-22T12:22:22')
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_extra.sql'])
@pytest.mark.translations(
    rida={
        'rating': {'en': 'Rating {rating}'},
        'number_of_trips': {'en': 'Trips {number_of_trips}'},
        'permit_number': {'en': 'Permit {permit_number}'},
        'total_offers': {'en': 'Total offers: {total_offers_count}'},
        'succ_offers': {'en': 'Succ offers: {successful_offers_count}'},
        'succ_offers_perc': {'en': 'Succ perc: {successful_offer_percent}'},
        'fail_offers': {'en': 'Fail offers: {failed_offers_count}'},
        'fail_offers_perc': {'en': 'Fail perc: {failed_offers_percent}'},
        'rating_adjustment': {'en': '{value} rating adjustment'},
    },
)
@pytest.mark.parametrize(
    ['user_id', 'expected_passenger_info', 'expected_driver_info'],
    [
        pytest.param(
            1234,
            [
                {
                    'type': 1,
                    'data': {'text': 'Rating 5.00', 'color': '#000000'},
                },
                {'type': 1, 'data': {'text': 'Trips 0', 'color': '#000000'}},
            ],
            None,
            marks=get_profile_info_mark(
                user_id=1234,
                passenger_unit_templates=[
                    {'tanker_key': 'rating'},
                    {'tanker_key': 'number_of_trips'},
                ],
                driver_unit_templates=[
                    {'tanker_key': 'rating'},
                    {'tanker_key': 'number_of_trips'},
                    {'tanker_key': 'permit_number'},
                ],
            ),
            id='user_without_driver',
        ),
        pytest.param(
            1449,
            [
                {
                    'type': 1,
                    'data': {'text': 'Rating 5.00', 'color': '#000000'},
                },
                {'type': 1, 'data': {'text': 'Trips 0', 'color': '#000000'}},
            ],
            [
                {
                    'type': 1,
                    'data': {'text': 'Rating 0.00', 'color': '#000000'},
                },
                {'type': 1, 'data': {'text': 'Trips 0', 'color': '#000000'}},
                {
                    'type': 1,
                    'data': {'text': 'Permit № ------', 'color': '#000000'},
                },
            ],
            marks=get_profile_info_mark(
                user_id=1449,
                passenger_unit_templates=[
                    {'tanker_key': 'rating'},
                    {'tanker_key': 'number_of_trips'},
                ],
                driver_unit_templates=[
                    {'tanker_key': 'rating'},
                    {'tanker_key': 'number_of_trips'},
                    {'tanker_key': 'permit_number'},
                ],
            ),
            id='user_with_driver_wo_permit',
        ),
        pytest.param(
            1448,
            [
                {
                    'type': 1,
                    'data': {'text': 'Rating 5.00', 'color': '#000000'},
                },
                {'type': 1, 'data': {'text': 'Trips 0', 'color': '#000000'}},
            ],
            [
                {
                    'type': 1,
                    'data': {'text': 'Rating 5.00', 'color': '#000000'},
                },
                {'type': 1, 'data': {'text': 'Trips 0', 'color': '#000000'}},
                {
                    'type': 1,
                    'data': {'text': 'Permit № AA018913', 'color': '#000000'},
                },
            ],
            marks=get_profile_info_mark(
                user_id=1448,
                passenger_unit_templates=[
                    {'tanker_key': 'rating'},
                    {'tanker_key': 'number_of_trips'},
                ],
                driver_unit_templates=[
                    {'tanker_key': 'rating'},
                    {'tanker_key': 'number_of_trips'},
                    {'tanker_key': 'permit_number'},
                ],
            ),
            id='user_with_driver_with_permit',
        ),
        pytest.param(
            1448,
            [
                {
                    'type': 1,
                    'data': {'text': 'Total offers: 3', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Succ offers: 1', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Succ perc: 33', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Fail offers: 2', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Fail perc: 66', 'color': '#000000'},
                },
            ],
            [
                {
                    'type': 1,
                    'data': {'text': 'Total offers: 2', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Succ offers: 1', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Succ perc: 50', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Fail offers: 1', 'color': '#000000'},
                },
                {
                    'type': 1,
                    'data': {'text': 'Fail perc: 50', 'color': '#000000'},
                },
            ],
            marks=get_profile_info_mark(
                user_id=1448,
                passenger_unit_templates=[
                    {'tanker_key': 'total_offers'},
                    {'tanker_key': 'succ_offers'},
                    {'tanker_key': 'succ_offers_perc'},
                    {'tanker_key': 'fail_offers'},
                    {'tanker_key': 'fail_offers_perc'},
                ],
                driver_unit_templates=[
                    {'tanker_key': 'total_offers'},
                    {'tanker_key': 'succ_offers'},
                    {'tanker_key': 'succ_offers_perc'},
                    {'tanker_key': 'fail_offers'},
                    {'tanker_key': 'fail_offers_perc'},
                ],
            ),
            id='offers_stats',
        ),
        pytest.param(
            1448,
            [
                {
                    'data': {
                        'bubbles': [
                            {
                                'background_color': '#FFFF00',
                                'text': '★ 4.00',
                                'text_color': '#000000',
                            },
                            {
                                'background_color': '#FF0000',
                                'text': '-1.00 rating adjustment',
                                'text_color': '#000000',
                            },
                        ],
                        'text': 'Rating',
                    },
                    'type': 4,
                },
            ],
            [
                {
                    'data': {
                        'bubbles': [
                            {
                                'background_color': '#FFFF00',
                                'text': '★ 5.00',
                                'text_color': '#000000',
                            },
                            {
                                'background_color': '#00FF00',
                                'text': '+2.00 rating adjustment',
                                'text_color': '#000000',
                            },
                        ],
                        'text': 'Rating',
                    },
                    'type': 4,
                },
            ],
            marks=[
                get_profile_info_mark(
                    user_id=1448,
                    passenger_unit_templates=[
                        {'unit_id': 'rating_with_adjustments'},
                    ],
                    driver_unit_templates=[
                        {'unit_id': 'rating_with_adjustments'},
                    ],
                ),
                experiments_utils.get_penalty_exp(
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
                    passenger_rules=[
                        experiments_utils.PenaltyRule(
                            profile_comment_tk='rating_adjustment',
                            penalty=1,
                            min_cancelled_orders=1,
                        ),
                    ],
                    driver_rules=[
                        experiments_utils.PenaltyRule(
                            profile_comment_tk='rating_adjustment',
                            penalty=-2,
                            min_cancelled_orders=1,
                        ),
                    ],
                ),
            ],
            id='penalty_adjustments',
        ),
        pytest.param(
            1448,
            [
                {
                    'data': {
                        'bubbles': [
                            {
                                'background_color': '#FFFF00',
                                'text': '★ 5.00',
                                'text_color': '#000000',
                            },
                        ],
                        'text': 'Rating',
                    },
                    'type': 4,
                },
            ],
            [
                {
                    'data': {
                        'bubbles': [
                            {
                                'background_color': '#FFFF00',
                                'text': '★ 5.00',
                                'text_color': '#000000',
                            },
                        ],
                        'text': 'Rating',
                    },
                    'type': 4,
                },
            ],
            marks=[
                get_profile_info_mark(
                    user_id=1448,
                    passenger_unit_templates=[
                        {'unit_id': 'rating_with_adjustments'},
                    ],
                    driver_unit_templates=[
                        {'unit_id': 'rating_with_adjustments'},
                    ],
                ),
                experiments_utils.get_penalty_exp(
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
                    passenger_rules=[
                        experiments_utils.PenaltyRule(
                            profile_comment_tk='rating_adjustment',
                            penalty=0,
                            min_cancelled_orders=1,
                        ),
                    ],
                    driver_rules=[
                        experiments_utils.PenaltyRule(
                            profile_comment_tk='rating_adjustment',
                            penalty=0,
                            min_cancelled_orders=1,
                        ),
                    ],
                ),
            ],
            id='zero_penalty_adjustments_skipped',
        ),
        pytest.param(
            1448,
            [
                {
                    'type': 1,
                    'data': {'text': 'Total offers: 3', 'color': '#000000'},
                },
            ],
            [],
            marks=[
                get_profile_info_mark(
                    user_id=1448,
                    passenger_unit_templates=[
                        {'tanker_key': 'total_offers'},
                        {'unit_id': 'rating_with_adjustments'},
                    ],
                    driver_unit_templates=[],
                ),
                experiments_utils.get_penalty_exp(
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
                    passenger_rules=[
                        experiments_utils.PenaltyRule(
                            profile_comment_tk='UNKNOWN_TANKER_KEY',
                            penalty=1,
                            min_cancelled_orders=1,
                        ),
                    ],
                    driver_rules=[],
                ),
            ],
            id='prebuilt_rating_unit_missing_tanker_key',
        ),
    ],
)
async def test_additional_info(
        web_app_client,
        user_id: int,
        expected_passenger_info: Optional[List[Dict[str, Any]]],
        expected_driver_info: Optional[List[Dict[str, Any]]],
):
    response = await web_app_client.post(
        '/v1/getProfileData',
        headers=helpers.get_auth_headers(user_id=user_id),
    )
    assert response.status == 200
    response_json = await response.json()
    user = response_json['data']['user']

    passenger_info = user.get('additional_info')
    assert passenger_info == expected_passenger_info

    driver_info = (user.get('driver') or {}).get('additional_info')
    assert driver_info == expected_driver_info
