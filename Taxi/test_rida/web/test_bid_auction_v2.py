import dataclasses
import datetime
import decimal
from typing import Dict
from typing import List
from typing import Optional

import pytest

from rida import consts
from rida.generated.service.swagger.models import api as api_models
from rida.logic import bid_auction
from test_rida import experiments_utils
from test_rida import helpers


@dataclasses.dataclass
class Bid:
    proposed_price: float
    status: consts.BidStatus = consts.BidStatus.PENDING
    driver_guid: Optional[str] = None

    def to_dict(self):
        return {
            'proposed_price': self.proposed_price,
            'bid_status': self.status.value,
        }


@dataclasses.dataclass
class AuctionStatusSettings:
    id: str  # pylint: disable=invalid-name
    can_make_bid: bool = True
    default_value_best_price_offset: Optional[int] = None
    limit_default_price_to_initial_price: Optional[bool] = None

    def to_api_model(self) -> api_models.AuctionStatusSettings:
        api_model = api_models.AuctionStatusSettings(
            additional_info=[api_models.TextUnit(tanker_key=self.id)],
            can_make_bid=self.can_make_bid,
            default_value_best_price_offset=(
                self.default_value_best_price_offset
            ),
            limit_default_price_to_initial_price=(
                self.limit_default_price_to_initial_price
            ),
        )
        return api_model


@dataclasses.dataclass
class AuctionActiveBidClause:
    settings: AuctionStatusSettings
    max_bid_position: Optional[int] = None
    min_bid_position: Optional[int] = None
    min_matching_bids: Optional[int] = None
    max_matching_bids: Optional[int] = None

    def to_api_model(self) -> api_models.AuctionActiveBidClause:
        api_model = api_models.AuctionActiveBidClause(
            settings=self.settings.to_api_model(),
            max_bid_position=self.max_bid_position,
            min_bid_position=self.min_bid_position,
            min_matching_bids=self.min_matching_bids,
            max_matching_bids=self.max_matching_bids,
        )
        return api_model


def _get_experiment(
        no_bids: Optional[AuctionStatusSettings] = None,
        no_driver_bid: Optional[AuctionStatusSettings] = None,
        active_bid: List[AuctionActiveBidClause] = None,
        bid_status_logs: Dict[str, api_models.BidStatusLog] = None,
) -> api_models.Exp3BidAuctionV2:
    active_bid = active_bid or list()
    bid_status_logs = bid_status_logs or dict()
    exp = api_models.Exp3BidAuctionV2(
        auction_settings=api_models.AuctionInterfaceSettings(
            default=AuctionStatusSettings(id='default').to_api_model(),
            no_bids=no_bids.to_api_model() if no_bids else None,
            no_driver_bid=(
                no_driver_bid.to_api_model() if no_driver_bid else None
            ),
            active_bid=[clause.to_api_model() for clause in active_bid],
        ),
        bid_status_logs=api_models.BidStatusLogs(extra=bid_status_logs),
    )
    return exp


def _get_experiment_mark(
        no_bids: Optional[AuctionStatusSettings] = None,
        no_driver_bid: Optional[AuctionStatusSettings] = None,
        active_bid: List[AuctionActiveBidClause] = None,
        bid_status_logs: Dict[str, api_models.BidStatusLog] = None,
):
    value = _get_experiment(
        no_bids=no_bids,
        no_driver_bid=no_driver_bid,
        active_bid=active_bid,
        bid_status_logs=bid_status_logs,
    )
    exp3_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_bid_auction_v2',
        args=[
            {'name': 'country_id', 'type': 'int', 'value': 2},
            {'name': 'zone_id', 'type': 'int', 'value': 0},
            *experiments_utils.get_default_user_args(),
        ],
        value=value.serialize(),
    )
    return exp3_mark


@pytest.mark.translations(
    rida={'log_status_pending': {'en': 'nice offer, bruh!'}},
)
@_get_experiment_mark(
    bid_status_logs={
        'new_status.PENDING': api_models.BidStatusLog(
            text_tk='log_status_pending',
            color='#000000',
            image_url='https://stonks',
        ),
        'new_status.ACCEPTED': api_models.BidStatusLog(
            text_tk='unknown_tanker_key', color='#000000',
        ),
    },
)
async def test_bid_status_log_response(web_app_client):
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    driver_bid = offer.get('driver_bid')
    assert driver_bid is not None
    bid_status_log = offer.get('bid_status_log')
    assert bid_status_log == [
        {
            'color': '#000000',
            'image_url': 'https://stonks',
            'text': 'nice offer, bruh!',
        },
    ]


@pytest.mark.parametrize(
    [
        'driver_bid',
        'other_bids',
        'expected_best_price',
        'expected_best_other_price',
        'expected_bid_position',
        'expected_matching_bids',
    ],
    [
        pytest.param(Bid(500), [], 500, None, 1, 0, id='no_other_bids'),
        pytest.param(
            Bid(500), [Bid(600), Bid(400)], 400, 400, 2, 0, id='multiple_bids',
        ),
        pytest.param(
            Bid(500),
            [Bid(600), Bid(700)],
            500,
            600,
            1,
            0,
            id='driver_bid_is_best',
        ),
        pytest.param(
            Bid(500),
            [Bid(500), Bid(500), Bid(600)],
            500,
            500,
            3,
            2,
            id='matching_bids',
        ),
    ],
)
def test_get_auction_stats(
        driver_bid: Bid,
        other_bids: List[Bid],
        expected_best_price: float,
        expected_best_other_price: Optional[float],
        expected_bid_position: int,
        expected_matching_bids: int,
):
    auction_stats = bid_auction._get_auction_stats(  # pylint: disable=W0212
        driver_bid.to_dict(), [bid.to_dict() for bid in other_bids],
    )
    assert auction_stats.best_price == expected_best_price
    assert auction_stats.best_other_price == expected_best_other_price
    assert auction_stats.bid_position == expected_bid_position
    assert auction_stats.matching_bids == expected_matching_bids


@pytest.mark.parametrize(
    ['driver_bid', 'other_bids', 'expected_clause_id'],
    [
        pytest.param(None, [], 'no_bids'),
        pytest.param(None, [Bid(500)], 'no_driver_bid'),
        pytest.param(Bid(500), [Bid(600), Bid(700)], 'best_bid'),
        pytest.param(Bid(500), [Bid(500), Bid(700)], 'matched_best_bid'),
        pytest.param(Bid(500), [Bid(500), Bid(500)], 'matched_twice'),
        pytest.param(Bid(500), [Bid(400), Bid(700)], 'second_bid'),
        pytest.param(Bid(500), [Bid(400), Bid(500)], 'matched_second_bid'),
        pytest.param(Bid(500), [Bid(400), Bid(450)], 'default'),
    ],
)
def test_get_auction_status_settings(
        driver_bid: Optional[Bid],
        other_bids: List[Bid],
        expected_clause_id: str,
):
    bid_auction_exp = _get_experiment(
        no_bids=AuctionStatusSettings('no_bids'),
        no_driver_bid=AuctionStatusSettings('no_driver_bid'),
        active_bid=[
            AuctionActiveBidClause(
                settings=AuctionStatusSettings('best_bid'), max_bid_position=2,
            ),
            AuctionActiveBidClause(
                settings=AuctionStatusSettings('matched_best_bid'),
                min_bid_position=2,
                max_bid_position=3,
                min_matching_bids=1,
            ),
            AuctionActiveBidClause(
                settings=AuctionStatusSettings('matched_twice'),
                min_bid_position=3,
                max_bid_position=4,
                min_matching_bids=2,
            ),
            AuctionActiveBidClause(
                settings=AuctionStatusSettings('second_bid'),
                min_bid_position=2,
                max_bid_position=3,
            ),
            AuctionActiveBidClause(
                settings=AuctionStatusSettings('matched_second_bid'),
                min_bid_position=3,
                max_bid_position=4,
                min_matching_bids=1,
                max_matching_bids=2,
            ),
        ],
    )
    auction_status_settings = (
        bid_auction._get_auction_status_settings(  # pylint: disable=W0212
            bid_auction_exp=bid_auction_exp,
            driver_bid=driver_bid.to_dict() if driver_bid else None,
            other_bids=[bid.to_dict() for bid in other_bids],
        )
    )
    assert len(auction_status_settings.additional_info) == 1
    unit = auction_status_settings.additional_info[0]
    assert isinstance(unit, api_models.TextUnit)
    clause_id = unit.tanker_key
    assert clause_id == expected_clause_id


@pytest.mark.translations(
    rida={
        'default': {'en': 'default'},
        'best_bid': {'en': 'best_bid'},
        'second_best_bid': {'en': 'second_best_bid'},
    },
)
@pytest.mark.parametrize(
    ['other_bids', 'expected_clause_id', 'expected_can_make_bid'],
    [
        pytest.param(
            [],
            'default',
            True,
            marks=_get_experiment_mark(),
            id='no_other_bids',
        ),
        pytest.param(
            [Bid(400, status=consts.BidStatus.EXPIRED)],
            'best_bid',
            False,
            marks=_get_experiment_mark(
                active_bid=[
                    AuctionActiveBidClause(
                        settings=AuctionStatusSettings(
                            'best_bid', can_make_bid=False,
                        ),
                        max_bid_position=2,
                    ),
                ],
            ),
            id='other_bid_is_expired',
        ),
        pytest.param(
            [Bid(400, driver_guid='dupe'), Bid(400, driver_guid='dupe')],
            'second_best_bid',
            True,
            marks=_get_experiment_mark(
                active_bid=[
                    AuctionActiveBidClause(
                        settings=AuctionStatusSettings('second_best_bid'),
                        min_bid_position=2,
                        max_bid_position=3,
                    ),
                ],
            ),
            id='duplicate_bids_ignored',
        ),
    ],
)
async def test_bid_settings(
        web_app_client,
        mongodb,
        other_bids: List[Bid],
        expected_clause_id: str,
        expected_can_make_bid: bool,
):
    for i, bid in enumerate(other_bids):
        mongodb.rida_bids.insert_one(
            {
                'accepted_bid': '0',
                'bid_guid': str(i),
                'bid_status': bid.status.value,
                'created_at': datetime.datetime(2025, 1, 1),
                'driver_guid': bid.driver_guid or str(i),
                'expired_at': datetime.datetime(2025, 1, 1),
                'is_shown': False,
                'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
                'price_sequence': 1,
                'proposed_price': 100,
                'updated_at': 39549394,
                'user_guid': str(i),
            },
        )

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']

    additional_info = offer['bid_settings'].get('additional_info')
    assert additional_info is not None
    assert len(additional_info) == 1
    assert additional_info[0]['data']['text'] == expected_clause_id

    can_make_bid = offer['can_make_bid']
    assert can_make_bid == expected_can_make_bid


async def test_bid_place_notifications(web_app_client, mongodb, stq):
    mongodb.rida_bids.remove(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=helpers.get_auth_headers(user_id=1234),
        json={
            'bid_guid': 'driver_bid_250',
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
            'proposed_price': 250.0,
        },
    )
    assert response.status == 200
    assert stq.rida_send_notifications.times_called == 3
    stq_calls_kwargs = []
    for _ in range(3):
        stq_call_kwargs = stq.rida_send_notifications.next_call()['kwargs']
        stq_calls_kwargs.append(stq_call_kwargs)
    stq_calls_kwargs.sort(key=lambda stq_call: stq_call['intent'])
    assert stq_calls_kwargs[0] == {
        'currency': 'NGN',
        'intent': 'add_bid',
        'price': 250.0,
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
    }
    assert stq_calls_kwargs[1] == {
        'intent': 'bid_auction_price_matched',
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
        'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        'price_sequence': 1,
        'proposed_price': 250.0,
    }
    assert stq_calls_kwargs[2] == {
        'intent': 'bid_auction_price_outbidden',
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
        'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        'price_sequence': 1,
        'proposed_price': 250.0,
    }


@pytest.mark.parametrize(
    [
        'bid_auction_exp',
        'initial_price',
        'bid_step',
        'driver_bid',
        'other_bids',
        'expected_default_price',
    ],
    [
        pytest.param(
            _get_experiment(),
            500,
            100,
            None,
            [],
            500,
            id='no_price_adjustments',
        ),
        pytest.param(
            _get_experiment(
                no_bids=AuctionStatusSettings(
                    id='no_bids', default_value_best_price_offset=1,
                ),
            ),
            500,
            100,
            None,
            [],
            600,
            id='default_price_offset',
        ),
        pytest.param(
            _get_experiment(
                no_driver_bid=AuctionStatusSettings(
                    id='no_driver_bid', default_value_best_price_offset=None,
                ),
            ),
            500,
            100,
            None,
            [Bid(600), Bid(700)],
            500,
            id='bid_prices_ignored',
        ),
        pytest.param(
            _get_experiment(
                no_driver_bid=AuctionStatusSettings(
                    id='no_driver_bid', default_value_best_price_offset=0,
                ),
            ),
            500,
            100,
            None,
            [Bid(600), Bid(700)],
            600,
            id='bid_prices_accounted_for',
        ),
        pytest.param(
            _get_experiment(
                no_driver_bid=AuctionStatusSettings(
                    id='no_driver_bid',
                    default_value_best_price_offset=0,
                    limit_default_price_to_initial_price=True,
                ),
            ),
            500,
            100,
            None,
            [Bid(600), Bid(700)],
            500,
            id='bid_prices_accounted_and_limited',
        ),
        pytest.param(
            _get_experiment(
                active_bid=[
                    AuctionActiveBidClause(
                        settings=AuctionStatusSettings(
                            id='active_bid',
                            default_value_best_price_offset=-1,
                        ),
                    ),
                ],
            ),
            500,
            100,
            Bid(500),
            [],
            400,
            id='driver_bid_accounted_for',
        ),
    ],
)
async def test_get_default_bid_price(
        bid_auction_exp: api_models.Exp3BidAuctionV2,
        initial_price: float,
        bid_step: Optional[float],
        driver_bid: Optional[Bid],
        other_bids: List[Bid],
        expected_default_price: float,
):
    default_price = bid_auction.get_default_bid_price(
        bid_auction_exp=bid_auction_exp,
        initial_price=initial_price,
        bid_step=decimal.Decimal(bid_step) if bid_step else None,
        driver_bid=driver_bid.to_dict() if driver_bid else None,
        other_bids=[bid.to_dict() for bid in other_bids],
    )
    assert default_price == expected_default_price


@_get_experiment_mark(
    active_bid=[
        AuctionActiveBidClause(
            settings=AuctionStatusSettings(
                id='active_bid', default_value_best_price_offset=-1,
            ),
        ),
    ],
)
async def test_default_price(web_app_client):
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    # 50 lower than best bid - one bid step down
    assert offer['bid_settings']['default_price'] == 450
