import datetime
from typing import Optional

import pytest

from rida import consts
from test_rida import experiments_utils
from test_rida import helpers


_NOW = datetime.datetime(2022, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)


def get_user_offer_popup_exp(
        min_time_from_offer_created: Optional[int] = None,
        min_time_from_offer_updated: Optional[int] = None,
        min_seen_by_drivers: Optional[int] = None,
        max_total_bids: Optional[int] = None,
        max_suggested_price_ratio: Optional[float] = None,
        new_popup_on_price_change: bool = False,
        popup_type: int = 1,
):
    translations = {
        'rida': {
            'user_popup.title': {'en': 'Title'},
            'user_popup.body': {'en': 'Body'},
            'user_popup.button': {
                'en': 'Button {suggested_price}' + (
                    ' {currency}' if popup_type == 2 else ''
                ),
            },
        },
    }
    translations_mark = pytest.mark.translations(**translations)

    popup_rules = {
        'min_time_from_offer_created': min_time_from_offer_created,
        'min_time_from_offer_updated': min_time_from_offer_updated,
        'min_seen_by_drivers': min_seen_by_drivers,
        'max_total_bids': max_total_bids,
        'max_offer_to_suggested_price_ratio': max_suggested_price_ratio,
        'new_popup_on_price_change': new_popup_on_price_change,
    }
    popup_rules = {k: v for k, v in popup_rules.items() if v is not None}

    exp_value = {
        'rules': popup_rules,
        'popup': {
            'title_tk': 'user_popup.title',
            'body_tk': 'user_popup.body',
            'button_tk': 'user_popup.button',
            'type': popup_type,
        },
    }
    exp3_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_user_offer_popup',
        args=experiments_utils.get_default_user_args(),
        value=exp_value,
    )
    return [translations_mark, exp3_mark]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'is_popup_expected',
    [
        pytest.param(True, marks=get_user_offer_popup_exp(), id='no_rules'),
        pytest.param(
            False,
            marks=get_user_offer_popup_exp(min_time_from_offer_created=1900),
            id='min_time_created_not_passed',
        ),
        pytest.param(
            True,
            marks=get_user_offer_popup_exp(min_time_from_offer_created=1700),
            id='min_time_created_passed',
        ),
        pytest.param(
            False,
            marks=get_user_offer_popup_exp(min_time_from_offer_updated=1900),
            id='min_time_updated_not_passed',
        ),
        pytest.param(
            True,
            marks=get_user_offer_popup_exp(min_time_from_offer_updated=1700),
            id='min_time_updated_passed',
        ),
        pytest.param(
            False,
            marks=get_user_offer_popup_exp(min_seen_by_drivers=3),
            id='min_seen_by_drivers_not_passed',
        ),
        pytest.param(
            True,
            marks=get_user_offer_popup_exp(min_seen_by_drivers=2),
            id='min_seen_by_drivers_passed',
        ),
        pytest.param(
            False,
            marks=get_user_offer_popup_exp(max_total_bids=0),
            id='max_total_bids_exceeded',
        ),
        pytest.param(
            True,
            marks=get_user_offer_popup_exp(max_total_bids=1),
            id='max_total_bids_not_exceeded',
        ),
        pytest.param(
            False,
            marks=get_user_offer_popup_exp(max_suggested_price_ratio=0.5),
            id='max_suggested_price_ratio_exceeded',
        ),
        pytest.param(
            True,
            marks=get_user_offer_popup_exp(max_suggested_price_ratio=1),
            id='max_suggested_price_ratio_not_exceeded',
        ),
    ],
)
async def test_popup_rules(web_app_client, is_popup_expected: bool):
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    if is_popup_expected:
        assert popup == {
            'id': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D_1',
            'title': 'Title',
            'body': 'Body',
            'button': 'Button {suggested_price}',
            'type': 1,
            'data': {},
        }
    else:
        assert popup is None


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['has_active_bid', 'is_popup_expected'],
    [
        pytest.param(
            False, True, marks=get_user_offer_popup_exp(), id='no_active_bids',
        ),
        pytest.param(
            True, False, marks=get_user_offer_popup_exp(), id='has_active_bid',
        ),
    ],
)
async def test_no_popup_on_active_bids(
        web_app_client, mongodb, has_active_bid: bool, is_popup_expected: bool,
):
    if has_active_bid:
        mongodb.rida_bids.insert_one(
            {
                'accepted_bid': '0',
                'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
                'bid_status': 'PENDING',
                'created_at': _NOW,
                'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
                'expired_at': _NOW + datetime.timedelta(minutes=5),
                'is_shown': False,
                'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
                'price_sequence': 1,
                'proposed_price': 100,
                'updated_at': 39549394,
                'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
            },
        )

    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    if is_popup_expected:
        assert popup is not None
    else:
        assert popup is None


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['has_changed_price', 'expected_popup_id'],
    [
        pytest.param(
            False,
            '1',
            marks=get_user_offer_popup_exp(
                min_time_from_offer_updated=1, new_popup_on_price_change=False,
            ),
            id='no_price_change',
        ),
        pytest.param(
            True,
            '1',
            marks=get_user_offer_popup_exp(
                min_time_from_offer_updated=1, new_popup_on_price_change=False,
            ),
            id='no_update_on_price_change',
        ),
        pytest.param(
            False,
            '1_1',
            marks=get_user_offer_popup_exp(
                min_time_from_offer_updated=1, new_popup_on_price_change=True,
            ),
            id='no_price_change_with_enabled_updates',
        ),
        pytest.param(
            True,
            '1_2',
            marks=get_user_offer_popup_exp(
                min_time_from_offer_updated=1, new_popup_on_price_change=True,
            ),
            id='update_on_price_change',
        ),
    ],
)
async def test_update_on_price_changed(
        taxi_rida_web,
        mocked_time,
        has_changed_price: bool,
        expected_popup_id: str,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'

    if has_changed_price:
        await taxi_rida_web.post(
            '/v1/offer/priceChange',
            headers=helpers.get_auth_headers(user_id=1234),
            json={'offer_guid': offer_guid, 'initial_price': 35900},
        )
    mocked_time.sleep(2)
    await taxi_rida_web.invalidate_caches()

    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    assert popup is not None
    assert popup['id'] == '_'.join([offer_guid, expected_popup_id])


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'popup_type',
    [
        pytest.param(
            1,
            marks=get_user_offer_popup_exp(popup_type=1),
            id='default_popup',
        ),
        pytest.param(
            2,
            marks=get_user_offer_popup_exp(popup_type=2),
            id='suggested_price_popup',
        ),
    ],
)
async def test_popup_types(web_app_client, popup_type: int):
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    if popup_type == 1:
        assert popup == {
            'id': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D_1',
            'title': 'Title',
            'body': 'Body',
            'button': 'Button {suggested_price}',
            'type': 1,
            'data': {},
        }
    elif popup_type == 2:
        assert popup == {
            'id': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D_2',
            'title': 'Title',
            'body': 'Body',
            'button': 'Button 1,500 NGN',
            'type': 2,
            'data': {'suggested_price': 1500.0},
        }
    else:
        assert False, 'unexpected popup type'


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    [
        'current_price',
        'country_id',
        'expected_suggested_price',
        'expected_formatted_price',
    ],
    [
        pytest.param(
            1366,
            2,
            1500,
            '1,500 NGN',
            marks=get_user_offer_popup_exp(popup_type=2),
            id='next_step_price_is_below_suggested_price',
        ),
        pytest.param(
            1566,
            2,
            1600,
            '1,600 NGN',
            marks=get_user_offer_popup_exp(popup_type=2),
            id='next_step_price_is_above_suggested_price',
        ),
        pytest.param(
            1566,
            13,
            1600,
            '1,600 SLL',
            marks=get_user_offer_popup_exp(popup_type=2),
            id='sierra_leone_popup',
        ),
    ],
)
@pytest.mark.parametrize('zone_id', [0, 1])
async def test_popup_suggested_price(
        web_app_client,
        mongodb,
        current_price: float,
        country_id: int,
        expected_suggested_price: float,
        expected_formatted_price: str,
        zone_id: int,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    mongodb.rida_offers.update_one(
        {'offer_guid': offer_guid},
        {
            '$set': {
                'initial_price': current_price,
                'zone_id': zone_id,
                'country_id': country_id,
            },
        },
    )
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    assert popup == {
        'id': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D_2',
        'title': 'Title',
        'body': 'Body',
        'button': f'Button {expected_formatted_price}',
        'type': 2,
        'data': {'suggested_price': expected_suggested_price},
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['offer_status', 'is_popup_expected'],
    [
        pytest.param(
            consts.OfferStatus.PENDING,
            True,
            marks=get_user_offer_popup_exp(),
            id='offer_is_pending',
        ),
        pytest.param(
            consts.OfferStatus.WAITING,
            False,
            marks=get_user_offer_popup_exp(),
            id='offer_is_waiting',
        ),
        pytest.param(
            consts.OfferStatus.DRIVING,
            False,
            marks=get_user_offer_popup_exp(),
            id='offer_is_driving',
        ),
        pytest.param(
            consts.OfferStatus.EXPIRED,
            False,
            marks=get_user_offer_popup_exp(),
            id='offer_is_expired',
        ),
    ],
)
async def test_popup_on_pending(
        web_app_client,
        mongodb,
        offer_status: consts.OfferStatus,
        is_popup_expected: bool,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    mongodb.rida_offers.update_one(
        {'offer_guid': offer_guid},
        {'$set': {'offer_status': offer_status.value}},
    )
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    if is_popup_expected:
        assert popup is not None
    else:
        assert popup is None


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'is_price_change_popup_expected',
    [
        pytest.param(
            True,
            marks=get_user_offer_popup_exp(
                new_popup_on_price_change=True, min_time_from_offer_updated=0,
            ),
            id='no_min_time_since_offer_updated',
        ),
        pytest.param(
            False,
            marks=get_user_offer_popup_exp(
                new_popup_on_price_change=True, min_time_from_offer_updated=30,
            ),
            id='set_min_time_since_offer_updated',
        ),
    ],
)
async def test_popup_on_price_changed(
        web_app_client, is_price_change_popup_expected: bool,
):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'

    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    assert popup is not None

    response = await web_app_client.post(
        '/v1/offer/priceChange',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid, 'initial_price': 1200},
    )
    assert response.status == 200
    response_json = await response.json()
    popup = response_json['data']['offer'].get('popup')
    if is_price_change_popup_expected:
        assert popup is not None
    else:
        assert popup is None
