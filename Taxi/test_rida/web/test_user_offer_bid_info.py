from typing import Any
from typing import Dict
from typing import List

import pytest

from test_rida import experiments_utils
from test_rida import helpers


def _get_exp_mark(unit_templates: List[Dict[str, Any]]):
    exp3_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_bid_info_templates',
        args=experiments_utils.get_default_user_args(),
        value={'unit_templates': unit_templates},
    )
    return exp3_mark


def get_bid_info_marks(unit_templates: List[Dict[str, Any]]):
    translations = pytest.mark.translations(
        rida={'test_key_1': {'en': 'test_1'}, 'test_key_2': {'en': 'test_2'}},
    )
    return [translations, _get_exp_mark(unit_templates)]


@pytest.mark.translations(
    rida={
        'bid.price.key': {'en': 'Price'},
        'bid.price.value': {'en': '{proposed_price} {currency}'},
        'bid.estimated_time.key': {'en': 'Estimated pickup time'},
        'bid.estimated_time.value': {'en': '{estimated_time_min} min'},
    },
)
@pytest.mark.parametrize(
    'expected_bid_info',
    [
        pytest.param(
            [
                {'type': 101, 'data': {}},
                {
                    'type': 2,
                    'data': {
                        'key': {'text': 'Price', 'color': '#000000'},
                        'value': {'text': '100 NGN', 'color': '#000000'},
                    },
                },
                {'type': 100, 'data': {'color': '#000000'}},
                {'type': 101, 'data': {}},
                {
                    'type': 2,
                    'data': {
                        'key': {
                            'text': 'Estimated pickup time',
                            'color': '#000000',
                        },
                        'value': {'text': '1199 min', 'color': '#000000'},
                    },
                },
            ],
            id='default_additional_info',
        ),
        pytest.param(
            [
                {'type': 101, 'data': {}},
                {'type': 100, 'data': {'color': '#000000'}},
                {'type': 1, 'data': {'text': 'test_1', 'color': '#000000'}},
            ],
            marks=get_bid_info_marks(
                [
                    {'type': 101},
                    {'type': 100, 'color': '#000000'},
                    {'tanker_key': 'test_key_1'},
                ],
            ),
            id='multiple_units',
        ),
    ],
)
async def test_bid_additional_info(
        web_app_client, expected_bid_info: List[Dict[str, Any]],
):
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    response_json = await response.json()
    bid_info = response_json['data']['offer']['bids'][0]['additional_info']
    assert bid_info == expected_bid_info


@_get_exp_mark([{'tanker_key': 'bid.price.value'}])
@pytest.mark.translations(
    rida={
        'bid.price.key': {'en': 'Price'},
        'bid.price.value': {'en': '{proposed_price} {currency}'},
        'bid.estimated_time.key': {'en': 'Estimated pickup time'},
        'bid.estimated_time.value': {'en': '{estimated_time_min} min'},
    },
)
async def test_bid_additional_info_currency(web_app_client, mongodb):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    mongodb.rida_offers.update_one(
        {'offer_guid': offer_guid}, {'$set': {'country_id': 13}},
    )
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    response_json = await response.json()
    bid_info = response_json['data']['offer']['bids'][0]['additional_info']
    assert bid_info == [
        {'type': 1, 'data': {'text': '100 SLL', 'color': '#000000'}},
    ]
