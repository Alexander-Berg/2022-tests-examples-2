import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest


def get_default_user_args(
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        device_uuid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        application: str = 'rida_android',
        version: str = '2.6.0',
        is_dev_team: bool = False,
) -> List[Dict[str, Any]]:
    return [
        {'name': 'user_guid', 'type': 'string', 'value': user_guid},
        {'name': 'device_uuid', 'type': 'string', 'value': device_uuid},
        {'name': 'application', 'type': 'application', 'value': application},
        {'name': 'version', 'type': 'application_version', 'value': version},
        {'name': 'is_dev_team', 'type': 'bool', 'value': is_dev_team},
    ]


def get_distance_info_config(
        strategy: str,
        request_source: str,
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
):
    return pytest.mark.client_experiments3(
        consumer='rida',
        config_name='rida_distance_info_calculation_settings',
        args=[
            {'name': 'user_guid', 'type': 'string', 'value': user_guid},
            {
                'name': 'request_source',
                'type': 'string',
                'value': request_source,
            },
        ],
        value={'strategy': strategy},
    )


def get_driver_dispatch_exp(
        max_search_distance_meters=7000,
        driver_position_last_updated_ttl_seconds=1800,
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
):
    value = {
        'max_search_distance_meters': max_search_distance_meters,
        'driver_position_last_updated_ttl_seconds': (
            driver_position_last_updated_ttl_seconds
        ),
    }

    client_exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_driver_dispatch_settings',
        args=[{'name': 'user_guid', 'type': 'string', 'value': user_guid}],
        value=value,
    )
    return client_exp_mark


def get_dispatch_exp(
        nearest_drivers_limit=50,
        max_search_distance_meters=7000,
        driver_position_last_updated_ttl_seconds=1800,
        nearest_visible_drivers_limit: Optional[int] = None,
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        application: str = 'rida_android',
):
    value = {
        'nearest_drivers_limit': nearest_drivers_limit,
        'max_search_distance_meters': max_search_distance_meters,
        'driver_position_last_updated_ttl_seconds': (
            driver_position_last_updated_ttl_seconds
        ),
    }
    if nearest_visible_drivers_limit:
        value['nearest_visible_drivers_limit'] = nearest_visible_drivers_limit
    client_exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        config_name='rida_dispatch_settings',
        args=get_default_user_args(user_guid, application=application),
        value=value,
    )
    return client_exp_mark


def get_route_info_config(
        strategy: str,
        request_source: str,
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
):
    return pytest.mark.client_experiments3(
        consumer='rida',
        config_name='rida_route_info_calculation_settings',
        args=[
            {'name': 'user_guid', 'type': 'string', 'value': user_guid},
            {
                'name': 'request_source',
                'type': 'string',
                'value': request_source,
            },
        ],
        value={'strategy': strategy},
    )


@dataclasses.dataclass
class PriceValidationSettingsExpArgs:
    country_id: int
    zone_id: int
    is_driver: bool
    user_guid: str
    device_uuid: str
    application: str = 'rida_android'
    version: str = '2.6.0'


def get_price_validation_marks(
        exp_args: PriceValidationSettingsExpArgs,
        *,
        offer_min_value: Optional[float] = None,
        offer_max_value: Optional[float] = None,
        offer_min_percent: Optional[float] = None,
        offer_max_percent: Optional[float] = None,
        bid_min_value: Optional[float] = None,
        bid_max_value: Optional[float] = None,
        bid_min_percent: Optional[float] = None,
        bid_max_percent: Optional[float] = None,
):
    offer_config = {
        'min_value': offer_min_value,
        'max_value': offer_max_value,
        'min_percent': offer_min_percent,
        'max_percent': offer_max_percent,
    }
    offer_config = {k: v for k, v in offer_config.items() if v is not None}
    bid_config = {
        'min_value': bid_min_value,
        'max_value': bid_max_value,
        'min_percent': bid_min_percent,
        'max_percent': bid_max_percent,
    }
    bid_config = {k: v for k, v in bid_config.items() if v is not None}
    client_exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        config_name='rida_price_validation_settings',
        args=[
            {
                'name': 'country_id',
                'type': 'int',
                'value': exp_args.country_id,
            },
            {'name': 'zone_id', 'type': 'int', 'value': exp_args.zone_id},
            {'name': 'is_driver', 'type': 'bool', 'value': exp_args.is_driver},
            *get_default_user_args(
                user_guid=exp_args.user_guid,
                device_uuid=exp_args.device_uuid,
                application=exp_args.application,
                version=exp_args.version,
            ),
        ],
        value={'offer': offer_config, 'bid': bid_config},
    )
    return [client_exp_mark]


def get_price_overrides_marks(
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        time_coefficient: float = 0.0,
        distance_coefficient: float = 0.0,
        suggest_price_constant: float = 0.0,
        min_offer_amount: float = 0.0,
):
    client_exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_suggested_price_overrides',
        args=[
            {'name': 'country_id', 'type': 'int', 'value': 12},
            {'name': 'zone_id', 'type': 'int', 'value': 1},
            *get_default_user_args(user_guid=user_guid),
        ],
        value={
            'time_coefficient': time_coefficient,
            'distance_coefficient': distance_coefficient,
            'suggest_price_constant': suggest_price_constant,
            'min_offer_amount': min_offer_amount,
        },
    )
    return [client_exp_mark]


def get_offer_info_units(
        templates: List[Dict[str, Any]],
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        consumer: str = 'driver',
):
    return pytest.mark.client_experiments3(
        consumer='rida',
        config_name=f'rida_{consumer}_offer_info_templates',
        args=get_default_user_args(user_guid=user_guid),
        value={'unit_templates': templates},
    )


# pylint: disable=W0102
def get_sequential_offers_exp(user_guid: str, value: Optional[Dict] = None):
    value = value or {'enabled': True}
    return pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_sequential_sending_offers',
        args=get_default_user_args(user_guid=user_guid),
        value=value,
    )


def get_driver_block_exp(
        user_guid: str,
        min_failed_offers_ratio: float,
        min_orders_count: float,
):
    return pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_driver_block_by_cancellations',
        args=[{'name': 'user_guid', 'type': 'string', 'value': user_guid}],
        value={
            'rule': {
                'min_failed_offers_ratio': min_failed_offers_ratio,
                'min_orders_count': min_orders_count,
            },
        },
    )


def get_referral_settings_exp(
        title_tk: str,
        description: List[Dict],
        app_link: str,
        sharing_message_tk: str,
        code_length: int,
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        country_id: int = 2,
        target_driver_rides: int = 1,
        target_rider_rides: int = 1,
):
    return pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_referral_backend_settings',
        args=[
            *get_default_user_args(user_guid),
            {'name': 'country_id', 'type': 'int', 'value': country_id},
        ],
        value={
            'title_tk': title_tk,
            'description': description,
            'app_link': app_link,
            'sharing_message_tk': sharing_message_tk,
            'code_length': code_length,
            'target_actions': {
                'rider': {'completed_rides': target_rider_rides},
                'driver': {'completed_rides': target_driver_rides},
            },
            'rewards': {
                'money_for_rider_with_currency': '1000$',
                'money_for_driver_with_currency': '2000$',
            },
        },
    )


@dataclasses.dataclass
class PenaltyRule:
    penalty: float
    min_cancelled_orders: int = 0
    min_cancelled_ratio: float = 0
    profile_comment_tk: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        raw = dataclasses.asdict(self)
        return {k: v for k, v in raw.items() if v is not None}


def get_penalty_exp(
        *,
        recent_window_size_days: int = 14,
        passenger_rules: List[PenaltyRule] = None,
        driver_rules: List[PenaltyRule] = None,
        user_guid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
):
    passenger_rules = passenger_rules or list()
    driver_rules = driver_rules or list()
    value = {
        'recent_window_size_days': recent_window_size_days,
        'passenger_rules': [rule.to_dict() for rule in passenger_rules],
        'driver_rules': [rule.to_dict() for rule in driver_rules],
    }
    return pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_rating_cancellation_penalty',
        args=[{'name': 'user_guid', 'type': 'string', 'value': user_guid}],
        value=value,
    )


def get_geocoding_exp(strategy: str, request_source: str):
    return pytest.mark.client_experiments3(
        consumer='rida',
        config_name='rida_geocoding_settings',
        args=[
            {
                'name': 'user_guid',
                'type': 'string',
                'value': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
            },
            {'name': 'country_code', 'type': 'string', 'value': 'ng'},
            {
                'name': 'request_source',
                'type': 'string',
                'value': request_source,
            },
        ],
        value={'strategy': strategy},
    )
