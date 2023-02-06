from typing import Any
from typing import Dict
from typing import List

import pytest

from test_rida import experiments_utils
from test_rida import helpers


def _get_exp_marks():
    translations_mark = pytest.mark.translations(
        rida={
            'rida.bid_car_highlights.keke_taxi': {'en': '{brand} {model}'},
            'rida.bid_car_highlights.keke_general': {'en': 'TIS IS KEKE'},
        },
    )
    exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_highlight_bid_car_model',
        args=experiments_utils.get_default_user_args(),
        value={
            'Keke': {
                'Taxi': {
                    'text_tk': 'rida.bid_car_highlights.keke_taxi',
                    'text_color': '#FFFFFF',
                    'background_color': '#000000',
                },
                '__default__': {
                    'text_tk': 'rida.bid_car_highlights.keke_general',
                    'text_color': '#F0F0F0',
                    'background_color': '#0A0A0A',
                },
            },
        },
    )
    return [translations_mark, exp_mark]


@pytest.mark.parametrize(
    ['bid_car_brand', 'bid_car_model', 'expected_additional_info'],
    [
        pytest.param(
            'Keke',
            'Taxi',
            [
                {
                    'type': 3,
                    'data': {
                        'text': 'Keke Taxi',
                        'text_color': '#FFFFFF',
                        'background_color': '#000000',
                    },
                },
                {'type': 101, 'data': {}},
            ],
            marks=_get_exp_marks(),
            id='model_rule',
        ),
        pytest.param(
            'Keke',
            'Dachshund',
            [
                {
                    'type': 3,
                    'data': {
                        'text': 'TIS IS KEKE',
                        'text_color': '#F0F0F0',
                        'background_color': '#0A0A0A',
                    },
                },
                {'type': 101, 'data': {}},
            ],
            marks=_get_exp_marks(),
            id='default_brand_rule',
        ),
        pytest.param('Lol', 'Taxi', [], marks=_get_exp_marks(), id='no_match'),
    ],
)
async def test_bid_car_highlights(
        web_app,
        web_app_client,
        bid_car_brand: str,
        bid_car_model: str,
        expected_additional_info: List[Dict[str, Any]],
):
    async with web_app['context'].pg.rw_pool.acquire() as connection:
        query = f"""
        UPDATE vehicle_brands
        SET name = '{bid_car_brand}'
        WHERE id = 1;

        UPDATE vehicle_models
        SET name = '{bid_car_model}'
        WHERE id = 2;
        """
        await connection.execute(query)

    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    bids = (await response.json())['data']['offer']['bids']
    assert len(bids) == 1
    bid = bids[0]
    assert bid['driver']['vehicle']['vehicle_brand_name'] == bid_car_brand
    assert bid['driver']['vehicle']['vehicle_model_name'] == bid_car_model
    bid_additional_info = bid['additional_info']
    assert len(bid_additional_info) >= 3
    bid_additional_info = bid_additional_info[3:]  # discard default info
    assert bid_additional_info == expected_additional_info
