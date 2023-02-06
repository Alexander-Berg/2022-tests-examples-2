# pylint: disable=too-many-arguments,too-many-lines,protected-access
import datetime

import pytest


@pytest.mark.parametrize(
    ['data', 'order_proc_data', 'order_data', 'expected_data'],
    [
        (
            {
                'metadata': {
                    'ticket_subject': 'Я не вижу новые заказы',
                    'block_reasons': ['DriverPointsRateBlockTemp'],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'aze',
                },
            },
            {},
            {},
            {'autoreply': {'status': 'not_satisfy'}},
        ),
        (
            {
                'metadata': {
                    'ticket_subject': 'Я не вижу новые заказы',
                    'block_reasons': ['DriverPointsRateBlockTemp'],
                    'locale': 'ru',
                    'tariff': 'vip',
                    'country': 'rus',
                },
            },
            {},
            {},
            {'autoreply': {'status': 'ok', 'macro_id': 1}},
        ),
        (
            {
                'metadata': {
                    'ticket_subject': 'Я не вижу новые заказы',
                    'block_reasons': ['DriverPointsRateBlockTemp'],
                    'locale': 'en',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {},
            {'autoreply': {'status': 'not_satisfy'}},
        ),
        (
            {
                'metadata': {
                    'ticket_subject': 'Я не вижу новые заказы',
                    'block_reasons': ['DriverPointsRateBlockTemp'],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {},
            {'autoreply': {'macro_id': 1, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Почему меня заблокировали?',
                    'block_reasons': [
                        'DriverGradeBlock',
                        'DriverTiredByHoursExceed',
                    ],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {},
            {'autoreply': {'macro_id': 2, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Почему меня не заблокировали?',
                    'block_reasons': ['DriverTiredByHoursExceed'],
                },
            },
            {},
            {},
            {'autoreply': {'status': 'not_satisfy'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {'_id': 'order_id', 'payment_tech': {'type': 'cash'}},
            {'autoreply': {'macro_id': 4, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {'type': 'card'},
                'billing_tech': {
                    'transactions': [{'status': 'clear_success'}],
                },
            },
            {'autoreply': {'macro_id': 6, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {'type': 'card'},
                'billing_tech': {
                    'transactions': [
                        {
                            'status': 'clear_success',
                            'refunds': [{'status': 'refund_success'}],
                        },
                    ],
                },
            },
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {'type': 'card'},
                'billing_tech': {
                    'transactions': [
                        {'status': 'clear_success'},
                        {'status': 'hold_initiated'},
                    ],
                },
            },
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не постdупила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {'type': 'card'},
                'billing_tech': {
                    'transactions': [
                        {'status': 'clear_success'},
                        {'status': 'clear_success'},
                    ],
                },
            },
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {
                    'type': 'card',
                    'history': [
                        {
                            'decision': 'refund',
                            'reason_code': 'DOUBLE_PAY_CARD',
                        },
                    ],
                },
                'billing_tech': {
                    'transactions': [
                        {'status': 'clear_success'},
                        {'status': 'clear_success'},
                    ],
                },
            },
            {'autoreply': {'macro_id': 5, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {
                    'type': 'card',
                    'history': [
                        {'decision': 'refund', 'reason': 'DOUBLE_PAY_CARD'},
                        {'decision': 'compensate_park'},
                    ],
                },
                'billing_tech': {
                    'transactions': [
                        {'status': 'clear_success'},
                        {'status': 'clear_success'},
                    ],
                },
            },
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id_1',
                'payment_tech': {
                    'type': 'card',
                    'history': [{'decision': 'refund', 'reason': 'OTHER'}],
                },
                'billing_tech': {
                    'transactions': [
                        {'status': 'clear_success'},
                        {'status': 'clear_success'},
                    ],
                },
            },
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_2',
                    'ticket_subject': 'Таксометр: Вопрос про бонус',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {'_id': 'order_id_2'},
            {},
            {'autoreply': {'macro_id': 8, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_3',
                    'ticket_subject': 'Таксометр: Вопрос про бонус',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {
                '_id': 'order_id_3',
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                't': 'driving',
                                'c': datetime.datetime(2019, 1, 1, 15, 10),
                            },
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 15),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2019, 1, 1, 15, 12, 12),
                            },
                        ],
                    },
                },
            },
            {},
            {'autoreply': {'macro_id': 7, 'status': 'ok'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_3',
                    'ticket_subject': 'Таксометр: Вопрос про бонус',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {
                '_id': 'order_id_3',
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                't': 'driving',
                                'c': datetime.datetime(2019, 1, 1, 15, 10),
                            },
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 15),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2019, 1, 1, 15, 14, 12),
                            },
                        ],
                    },
                },
            },
            {},
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_3',
                    'ticket_subject': 'Таксометр: Вопрос про бонус',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {
                '_id': 'order_id_3',
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'q': 'create',
                                'c': datetime.datetime(2019, 1, 1, 15, 10),
                            },
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 15),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 19),
                            },
                            {
                                'q': 'reorder',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 20),
                            },
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 25),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2019, 1, 1, 15, 14, 12),
                            },
                        ],
                    },
                },
            },
            {},
            {'autoreply': {'status': 'no_answer'}},
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_3',
                    'ticket_subject': 'Таксометр: Вопрос про бонус',
                    'block_reasons': [],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {
                '_id': 'order_id_3',
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'q': 'create',
                                'c': datetime.datetime(2019, 1, 1, 15, 10),
                            },
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 15),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 19),
                            },
                            {
                                'q': 'reorder',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 20),
                            },
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2019, 1, 1, 15, 11, 25),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2019, 1, 1, 15, 12, 12),
                            },
                        ],
                    },
                },
            },
            {},
            {'autoreply': {'macro_id': 7, 'status': 'ok'}},
        ),
    ],
)
async def test_driver_autoreply(
        support_info_client,
        support_info_app,
        patch_aiohttp_session,
        response_mock,
        data,
        order_proc_data,
        order_data,
        expected_data,
        order_archive_mock,
):
    if order_proc_data:
        order_archive_mock.set_order_proc(order_proc_data)

    archive_api_url = support_info_app.settings.ARCHIVE_API_URL

    @patch_aiohttp_session(archive_api_url, 'POST')
    def _dummy_archive_api_request(method, url, **kwargs):
        assert url == archive_api_url + '/archive/order'
        if order_data:
            return response_mock(json={'doc': order_data})
        return response_mock(status=404)

    response = await support_info_client.post(
        '/v1/autoreply/driver',
        json=data,
        headers={'YaTaxi-Api-Key': 'api-key'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == expected_data


@pytest.mark.parametrize(
    ['data', 'order_proc_data', 'order_data', 'expected_data'],
    [
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': ['DriverNoPermit'],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {'type': 'card'},
                'billing_tech': {
                    'transactions': [{'status': 'clear_success'}],
                },
            },
            {
                'status': 'ok',
                'metadata': {
                    'compensation_success': False,
                    'ya_plus': False,
                    'order_events_autocancel': False,
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': ['DriverNoPermit'],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                    'no_permit': True,
                    'source_block': False,
                },
            },
        ),
        (
            {
                'metadata': {
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': ['DriverCarBlacklisted'],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                },
            },
            {},
            {
                '_id': 'order_id',
                'payment_tech': {
                    'type': 'card',
                    'history': [
                        {
                            'decision': 'refund',
                            'reason_code': 'DOUBLE_PAY_CARD',
                        },
                    ],
                },
                'billing_tech': {
                    'transactions': [
                        {'status': 'clear_success'},
                        {'status': 'clear_success'},
                    ],
                },
            },
            {
                'status': 'ok',
                'metadata': {
                    'refund_reason': ['DOUBLE_PAY_CARD'],
                    'compensation_success': False,
                    'payment_decisions': ['refund'],
                    'ya_plus': False,
                    'order_events_autocancel': False,
                    'order_id': 'order_id_1',
                    'ticket_subject': 'Таксометр: Не поступила оплата',
                    'block_reasons': ['DriverCarBlacklisted'],
                    'locale': 'ru',
                    'tariff': 'econom',
                    'country': 'rus',
                    'no_permit': False,
                    'source_block': True,
                },
            },
        ),
    ],
)
async def test_driver_meta(
        support_info_client,
        support_info_app,
        patch_aiohttp_session,
        order_archive_mock,
        response_mock,
        data,
        order_proc_data,
        order_data,
        expected_data,
):
    if order_proc_data:
        order_archive_mock.set_order_proc(order_proc_data)

    archive_api_url = support_info_app.settings.ARCHIVE_API_URL

    @patch_aiohttp_session(archive_api_url, 'POST')
    def _dummy_archive_api_request(method, url, **kwargs):
        assert url == archive_api_url + '/archive/order'
        if order_data:
            return response_mock(json={'doc': order_data})
        return response_mock(status=404)

    response = await support_info_client.post(
        '/v1/autoreply/driver_meta',
        json=data,
        headers={'YaTaxi-Api-Key': 'api-key'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == expected_data
