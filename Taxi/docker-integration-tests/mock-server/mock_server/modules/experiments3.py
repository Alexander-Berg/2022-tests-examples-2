"""
Mock for experiments3.taxi.yandex.net
This module is required for eats-core service ONLY
userver/py3 services use taxi-exp.taxi.yandex.net
"""

from aiohttp import web


EATS_CONFIGS_EXPERIMENTS = {
    'dispatch_weight_threshold_experiment': {
        'values': {
            'bicycle': 15,
            'vehicle': 50,
            'motorcycle': 15,
            'pedestrian': 15,
            'electric_bicycle': 15,
        },
    },
    'dispatch_supply_experiment': {'type': 'external'},
    'delayed_dispatch_settings_config': {
        'retry_delay': 60,
        'late_cancel_ttl': 300,
        'max_surge_level': 160,
        'late_cancel_delay': 30,
        'min_time_to_start_assign': 180,
        'max_arrival_to_source_delay': 1500,
        'time_until_region_work_finished': 1800,
        'fastest_suppliers_to_check_count': 5,
        'min_assign_threshold_before_order_prepared': 3,
    },
    'delivery_dispatch_duration_experiment': {
        'min_delivery_claim_lifetime': 1,
        'min_dispatch_time_for_claim': 10,
        'dispatch_attempts_end_time_threshold': 30,
    },
    'pull_dispatch_usage_experiment': {'enabled': False},
    'eda_core_order_send_strategy': {'value': 'legacy'},
    'eda_core_eats_order_send_schema': {'value': 'differences'},
    'batch_weight_threshold_experiment': {
        'values': {
            'bicycle': 15,
            'vehicle': 50,
            'motorcycle': 15,
            'pedestrian': 15,
            'electric_bicycle': 15,
        },
    },
    'eats_claim_tariff_classes': {'tariff_classes': []},
    'eats_claim_client_requirements': {'taxi_class': 'express'},
    'split_claim_request_comment_experiment': {
        'comments': {
            'default': (
                'Это заказ из ресторана или кафе. '
                'В комментарии к точке А есть адрес и номер телефона. '
                'Для заказа обязательно иметь термоемкость. '
                'Скажите менеджеру или официанту номер и сумму заказа. '
                'Положите горячее и холодное в разные пакеты и '
                'доставьте их до двери получателя.'
            ),
            'courier_eda': '',
            'courier_lavka': '',
        },
    },
    'claim_request_point_comment_experiment': {
        'points': {
            'return': {
                'default': (
                    'Ресторан {{place_name}}, номер заказа: '
                    '{{order_nr}}\n{{source_comment}}'
                ),
            },
            'source': {
                'default': (
                    'Ресторан {{place_name}}, номер заказа: '
                    '{{order_nr}}, сумма заказа: '
                    '{{sum}}{{currency}}.\n{{source_comment}}'
                ),
            },
            'pullback': {'default': ''},
            'destination': {
                'default': (
                    'Клиент: {{client_name}}\n' '{{destination_comment}}'
                ),
            },
        },
    },
    'delivery_batch_experiment': {'availability': True},
    'eda_payment_method_promo_discount': {
        'is_experiment_source_enabled': False,
        'is_eats_discounts_source_enabled': False,
    },
    'claim_request_processing_experiment': {
        'queues': {
            'cancel': [
                'stq',
            ],
            'create': [
                'stq',
            ],
            'approve': [
                'stq',
            ],
            'process': [
                'stq',
            ],
        },
    },
    'eats-new-cart-enabled': {
        'dry_run': False,
        'enabled': True,
        'should_log_dry_run': True,
    },
}

EATS_CONSUMERS = {
    'eda_core/logistics/order_from_source': [
        'dispatch_weight_threshold_experiment',
        'batch_weight_threshold_experiment',
        'claim_request_point_comment_experiment',
    ],
    'eda_core/logistics/delivery_from_source': [
        'dispatch_supply_experiment',
        'delayed_dispatch_settings_config',
        'pull_dispatch_usage_experiment',
    ],
    'eda_core/logistics/sent_order_with_assembly_data': [
        'delivery_dispatch_duration_experiment',
    ],
    'eda_core_order_send_strategy': ['eda_core_order_send_strategy'],
    'eda_core_eats_order_send_schema': ['eda_core_eats_order_send_schema'],
    'eda_core': [
        'eda_core_eats_order_send_schema',
        'eats-new-cart-enabled',
    ],
    'eda_core/logistics/branded_source': ['batch_weight_threshold_experiment'],
    'eda_core/logistics/claim_based': [
        'eats_claim_tariff_classes',
        'eats_claim_client_requirements',
    ],
    'eda_core/logistics/comments_from_source': [
        'split_claim_request_comment_experiment',
    ],
    'eda_core/logistics/multidelivery': ['delivery_batch_experiment'],
    'eda_payment_method_promo_discount': ['eda_payment_method_promo_discount'],
    'eda_core/logistics/corp_client': ['claim_request_processing_experiment'],
}


def _create_response(consumer_name: str) -> web.Response:
    return web.json_response(
        {
            'items': [
                {'name': exp, 'value': EATS_CONFIGS_EXPERIMENTS[exp]}
                for exp in EATS_CONSUMERS[consumer_name]
            ],
            'version': 1,
        },
    )


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/experiments', self.match_experiment)
        self.router.add_post('/v1/configs', self.match_experiment)

    @staticmethod
    async def match_experiment(request):
        data = await request.json()
        consumer = data['consumer']
        if consumer not in EATS_CONSUMERS:
            return web.HTTPNotFound

        return _create_response(consumer)
