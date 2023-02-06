import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from test_rida import experiments_utils
from test_rida import helpers


@dataclasses.dataclass()
class BidHighlightItem:
    ranking: Dict[str, Any]
    highlight_text_tk: str
    highlight_color: str
    min_bids_to_highlight: int


def _get_exp_marks(
        *,
        bid_price: float = 0,
        time_to_a: float = 0,
        driver_rating: float = 0,
        highlights: Optional[List[BidHighlightItem]] = None,
        max_bids: Optional[int] = None,
):
    exp_value = {
        'ranking': {
            'bid_price': bid_price,
            'time_to_a': time_to_a,
            'driver_rating': driver_rating,
        },
        'highlights': [
            {
                'ranking': highlight.ranking,
                'highlight_text_tk': highlight.highlight_text_tk,
                'highlight_color': highlight.highlight_color,
                'min_bids_to_highlight': highlight.min_bids_to_highlight,
            }
            for highlight in (highlights or [])
        ],
    }
    if max_bids is not None:
        exp_value['max_bids'] = max_bids
    client_exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_bid_ranks_highlights',
        args=[
            {'name': 'country_id', 'type': 'int', 'value': 2},
            {'name': 'zone_id', 'type': 'int', 'value': 0},
            *experiments_utils.get_default_user_args(),
        ],
        value=exp_value,
    )
    return [client_exp_mark]


@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers', 'rida_bids')
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['expected_bid_guid_order'],
    [
        pytest.param(
            [
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            ],
            marks=_get_exp_marks(),
            id='no params',
        ),
        pytest.param(
            [
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            ],
            marks=_get_exp_marks(bid_price=-10.0),
            id='bid_price',
        ),
        pytest.param(
            [
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            ],
            marks=_get_exp_marks(time_to_a=-10),
            id='time_to_a',
        ),
        pytest.param(
            [
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
            ],
            marks=_get_exp_marks(driver_rating=10),
            id='driver_rating',
        ),
        pytest.param(
            [
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
                '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            ],
            marks=_get_exp_marks(
                bid_price=-10, time_to_a=-0.01, driver_rating=10,
            ),
            id='multiple params',
        ),
    ],
)
async def test_bid_ranking(taxi_rida_web, expected_bid_guid_order: List[str]):
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    assert [
        bid['bid_guid'] for bid in offer['bids']
    ] == expected_bid_guid_order


@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers', 'rida_bids')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={'best price': {'en': 'best price'}, 'best ETA': {'en': 'best ETA'}},
)
@pytest.mark.parametrize(
    ['expected_bid_guids_and_highlights'],
    [
        pytest.param([], marks=_get_exp_marks(highlights=[]), id='no params'),
        pytest.param(
            [],
            marks=_get_exp_marks(
                highlights=[
                    BidHighlightItem(
                        highlight_color='#color',
                        highlight_text_tk='Best price!',
                        min_bids_to_highlight=5,
                        ranking={'bid_price': -1},
                    ),
                ],
            ),
            id='not enough bids',
        ),
        pytest.param(
            [('9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'best price')],
            marks=_get_exp_marks(
                highlights=[
                    BidHighlightItem(
                        highlight_color='#color',
                        highlight_text_tk='best price',
                        min_bids_to_highlight=2,
                        ranking={'bid_price': -1},
                    ),
                ],
            ),
            id='one parameter',
        ),
        pytest.param(
            [
                ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'best price'),
                ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', 'best ETA'),
            ],
            marks=_get_exp_marks(
                highlights=[
                    BidHighlightItem(
                        highlight_color='#color',
                        highlight_text_tk='best price',
                        min_bids_to_highlight=2,
                        ranking={'bid_price': -1},
                    ),
                    BidHighlightItem(
                        highlight_color='#color',
                        highlight_text_tk='best ETA',
                        min_bids_to_highlight=2,
                        ranking={'time_to_a': -1},
                    ),
                ],
            ),
            id='mutiple parameters',
        ),
        pytest.param(
            [('9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 'best price')],
            marks=_get_exp_marks(
                highlights=[
                    BidHighlightItem(
                        highlight_color='#color',
                        highlight_text_tk='best price',
                        min_bids_to_highlight=2,
                        ranking={'bid_price': -1},
                    ),
                    BidHighlightItem(
                        highlight_color='#color',
                        highlight_text_tk='best ETA',
                        min_bids_to_highlight=2,
                        ranking={'bid_price': -1},
                    ),
                ],
            ),
            id='one bid matches two highlights',
        ),
    ],
)
async def test_bid_highlighting(
        taxi_rida_web,
        expected_bid_guids_and_highlights: List[Tuple[str, str]],
):
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    bid_highlights = [
        (bid['bid_guid'], bid['additional_info'][-1]['data']['text'])
        for bid in offer['bids']
        if bid.get('additional_info')
        and bid['additional_info'][-1]['type'] == 1
    ]

    assert bid_highlights == expected_bid_guids_and_highlights


@pytest.mark.parametrize(
    ['expected_bids_count', 'is_max_bids_enabled'],
    [
        pytest.param(
            4, False, marks=_get_exp_marks(bid_price=-1), id='no_max_bids',
        ),
        pytest.param(
            3,
            False,
            marks=_get_exp_marks(bid_price=-1, max_bids=4),
            id='declined_bid_is_excluded',
        ),
        pytest.param(
            1,
            False,
            marks=_get_exp_marks(bid_price=-1, max_bids=1),
            id='best_pending_bid_is_returned',
        ),
    ],
)
async def test_max_bids(
        taxi_rida_web, expected_bids_count: int, is_max_bids_enabled: bool,
):
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    result = await response.json()
    bids = result['data']['offer']['bids']
    assert len(bids) == expected_bids_count
    if is_max_bids_enabled:
        for bid in bids:
            assert bid['bid_status'] == 'PENDING'
