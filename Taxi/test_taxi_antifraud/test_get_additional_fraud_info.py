from typing import Dict
from typing import List

import pytest


def get_necessary_fields(response: Dict[str, str]) -> Dict[str, str]:
    return {'fraud_info': response['fraud_info']}


async def check_response_code(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
):
    response = await web_app_client.get(
        '/v1/get_additional_fraud_info', params=request_params,
    )

    assert response.status == expected_response_code


async def check_response_code_and_content(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
        expected_response_content: List[Dict[str, str]],
):
    response = await web_app_client.get(
        '/v1/get_additional_fraud_info', params=request_params,
    )
    assert response.status == expected_response_code

    subventions = get_necessary_fields(await response.json())

    assert subventions == expected_response_content


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'driver_license': '1111111111'},
            200,
            {
                'fraud_info': [
                    {
                        'info': {
                            'window_orders_cnt': 78,
                            'today_orders_cnt': 0,
                            'window_users_cnt': 69,
                            'window_algo_probab': 0.000004236908141651326,
                            'today_geozone_ratio': 0.9870340356564019,
                            'window_geozone_ratio': 0.9841767110922317,
                            'cnt_orders_with_users': (
                                '+79170449734: 2, +79659320795: 2, '
                                '+79677425588: 2, +79869714313: 3, '
                                '+79870554647: 2, +79874866215: 4'
                            ),
                            'today_users_cnt': 0,
                            'today_algo_probab': 1,
                            'tariff_zone': 'neftekamsk',
                            'geozone_drivers_cnt': 524,
                        },
                        'date': '2019-04-08',
                        'rule_id': 'window_unique_phones_rule',
                        'autoreject': True,
                        'rules_type': 'self_driver',
                    },
                ],
            },
        ),
        (
            {'driver_license': ' 1111111111\t'},
            200,
            {
                'fraud_info': [
                    {
                        'info': {
                            'window_orders_cnt': 78,
                            'today_orders_cnt': 0,
                            'window_users_cnt': 69,
                            'window_algo_probab': 0.000004236908141651326,
                            'today_geozone_ratio': 0.9870340356564019,
                            'window_geozone_ratio': 0.9841767110922317,
                            'cnt_orders_with_users': (
                                '+79170449734: 2, +79659320795: 2, '
                                '+79677425588: 2, +79869714313: 3, '
                                '+79870554647: 2, +79874866215: 4'
                            ),
                            'today_users_cnt': 0,
                            'today_algo_probab': 1,
                            'tariff_zone': 'neftekamsk',
                            'geozone_drivers_cnt': 524,
                        },
                        'date': '2019-04-08',
                        'rule_id': 'window_unique_phones_rule',
                        'autoreject': True,
                        'rules_type': 'self_driver',
                    },
                ],
            },
        ),
        (
            {'driver_license': '4444444444'},
            200,
            {
                'fraud_info': [
                    {
                        'autoreject': False,
                        'date': '2019-04-23',
                        'info': {
                            'orders': (
                                'fa0e2e90d9d1280e973c5d8ff6c0ade4, '
                                '4f0ad417f74d2882a58f8ba36337f27c'
                            ),
                            'total': 2,
                        },
                        'rule_id': 'sgovor',
                        'rules_type': 'rejected',
                    },
                    {
                        'autoreject': False,
                        'date': '2019-04-10',
                        'info': {
                            'city': 'Стерлитамак',
                            'cnt_drivers_users': 1,
                            'driver_phones': '+79273282224',
                            'drivers_orders': 1,
                            'self_orders': 1,
                            'user_phones': '+79273282224',
                        },
                        'rule_id': 'opg',
                        'rules_type': 'unknown',
                    },
                ],
            },
        ),
        (
            {'driver_license': '5555555555'},
            200,
            {
                'fraud_info': [
                    {
                        'autoreject': False,
                        'date': '2019-04-10',
                        'info': {
                            'city': 'Стерлитамак',
                            'cnt_drivers_users': 1,
                            'driver_phones': '+79273282224',
                            'drivers_orders': 1,
                            'self_orders': 1,
                            'user_phones': '+79273282224',
                        },
                        'rule_id': 'opg',
                        'rules_type': 'unknown',
                    },
                ],
            },
        ),
        (
            {'driver_license': 'АА9999999'},
            200,
            {
                'fraud_info': [
                    {
                        'autoreject': False,
                        'date': '2019-04-10',
                        'info': {
                            'city': 'Стерлитамак',
                            'cnt_drivers_users': 1,
                            'driver_phones': '+79273282224',
                            'drivers_orders': 1,
                            'self_orders': 1,
                            'user_phones': '+79273282224',
                        },
                        'rule_id': 'opg',
                        'rules_type': 'unknown',
                    },
                ],
            },
        ),
    ],
)
async def test_get_info_by_license(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
):
    await check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )


@pytest.mark.parametrize('request_params,expected_response_code', [({}, 400)])
async def test_get_info_without_license(
        web_app_client, request_params, expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )
