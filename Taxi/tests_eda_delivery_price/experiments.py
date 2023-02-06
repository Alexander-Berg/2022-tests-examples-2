import pytest


def calc_delivery_price(prod_pipeline_2: str):
    return pytest.mark.experiments3(
        is_config=True,
        name='calc_delivery_price',
        consumers=['eda-delivery-price/calc-delivery-price'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            '-1': {
                'coef_distance': 25,
                'delivery_fee_basic': 400,
                'experiment_pipelines': ['missing_pipeline'],
                'experiment_pipelines_2.0': ['missing_pipeline'],
                'is_exceptional': False,
                'max_base_value': 99,
                'max_revenue': 250,
                'min_base_value': 29,
                'min_revenue': 150,
                'prod_pipeline_2.0': prod_pipeline_2,
                'thresholds': [
                    {'addition': 100, 'max': 550, 'min': 50, 'value': 0},
                    {'addition': 50, 'max': -1, 'min': 0, 'value': 1000},
                    {'addition': 0, 'max': -1, 'min': 0, 'value': 3000},
                ],
            },
            '2': {
                'coef_distance': 25,
                'delivery_fee_basic': 400,
                'experiment_pipelines': ['missing_pipeline'],
                'experiment_pipelines_2.0': ['missing_pipeline'],
                'is_exceptional': False,
                'max_base_value': 99,
                'max_revenue': 250,
                'min_base_value': 29,
                'min_revenue': 150,
                'prod_pipeline_2.0': prod_pipeline_2,
                'thresholds': [
                    {'addition': 100, 'max': 550, 'min': 50, 'value': 0},
                    {'addition': 50, 'max': -1, 'min': 0, 'value': 500},
                    {'addition': 0, 'max': -1, 'min': 0, 'value': 2000},
                ],
            },
        },
    )


def calc_if_delivery_is_free(is_free_delivery_fee: bool = False):
    return pytest.mark.experiments3(
        is_config=True,
        name='calc_if_delivery_is_free',
        consumers=['eda-delivery-price/calc-delivery-price'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'is_free_delivery_fee': is_free_delivery_fee,
            'number_of_orders_to_set_free_delivery_fee': 555,
            'thresholds_free_delivery': [
                {'addition': 444, 'max': 111, 'min': 222, 'value': 333},
            ],
        },
    )


def thresholds_templates(
        message_tmpl: str = 'Цена ниже за каждые 100 {currency_sign} в заказе',
        low_threshold_tmpl: str = 'Заказ от 0 {currency_sign}',
        high_threshold_tmpl: str = (
            'Заказ от {last_order_price} {currency_sign}'
        ),
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eda_delivery_price_thresholds_templates',
        consumers=['eda-delivery-price/calc-delivery-price'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'message_tmpl': message_tmpl,
            'low_threshold_tmpl': low_threshold_tmpl,
            'high_threshold_tmpl': high_threshold_tmpl,
        },
    )


def cart_service_fee(holding_amount: str):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cart_service_fee',
        consumers=['eda-delivery-price/calc-delivery-price'],
        clauses=[],
        default_value={'holding_amount': holding_amount},
    )


def surge_planned(time_interval_minutes: int):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_surge_planned',
        consumers=['eda-delivery-price/is-new-user'],
        clauses=[],
        is_config=True,
        default_value={'time_interval_minutes': time_interval_minutes},
    )


def redis_experiment(enabled: bool = True, ttl_minutes: int = 30):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_redis',
        consumers=['eda-delivery-price/calc-delivery-price'],
        clauses=[],
        default_value={'enabled': enabled, 'ttl_minutes': ttl_minutes},
    )


def continuous_carrot(step: int):
    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_continuous_carrot',
        consumers=['eda-delivery-price/calc-delivery-price'],
        default_value={'step': str(step)},
    )


def continuous_round(mode: str):
    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_continuous_round',
        consumers=['eda-delivery-price/calc-delivery-price'],
        default_value={'mode': str(mode)},
    )


def cart_weight_thresholds(thresholds=None):
    if thresholds is None:
        thresholds = {}
    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_cart_weight_thresholds',
        consumers=['eda-delivery-price/calc-delivery-price'],
        clauses=[],
        default_value={'-1': {'thresholds': thresholds}},
    )


def regional_limits_config(
        native_max_delivery_fee=None, taxi_max_delivery_fee=None,
):
    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_regional_limits',
        consumers=['eda-delivery-price/calc-delivery-price'],
        clauses=[],
        default_value={
            'native_max_delivery_fee': native_max_delivery_fee,
            'taxi_max_delivery_fee': taxi_max_delivery_fee,
        },
    )
