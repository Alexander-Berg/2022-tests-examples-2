# pylint: disable=invalid-name
from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as test_http

from test_eats_tips_payments import conftest


def _format_request_param(
        *, qr=None, recipient_id=None, place_id=None, bill_amount=None,
):
    return dict(
        filter(
            lambda item: item[1] is not None,
            {
                'qr': qr,
                'recipient_id': recipient_id,
                'place_id': place_id,
                'bill_amount': bill_amount,
            }.items(),
        ),
    )


def _format_eats_tips_partners_response(*, place_id=None, partner_id=None):
    mysql_ids_by_partner_id = {
        conftest.PARTNER_ID_1: '1',
        conftest.PARTNER_ID_3: '3',
        conftest.PARTNER_ID_4: '4',
        conftest.PARTNER_ID_17: '17',
    }
    mysql_ids_by_place_id = {
        conftest.PLACE_ID_1: '3',
        conftest.PLACE_ID_2: '4',
        conftest.PLACE_ID_3: '21',
        conftest.PLACE_ID_4: '22',
    }
    result = {
        'info': {
            'id': partner_id or 'partner_id_1',
            'b2p_id': 'partner_b2p_id_1',
            'display_name': '',
            'full_name': '',
            'phone_id': 'phone_id_1',
            'saving_up_for': '',
            'best2pay_blocked': False,
            'registration_date': '1970-01-01T03:00:00+03:00',
            'is_vip': False,
            'blocked': False,
            'mysql_id': mysql_ids_by_partner_id.get(partner_id),
        },
        'places': [
            {
                'place_id': place_id or conftest.PLACE_ID_2,
                'title': '',
                'address': '',
                'confirmed': True,
                'show_in_menu': True,
                'roles': [],
                'mysql_id': (
                    mysql_ids_by_place_id.get(place_id)
                    if place_id
                    else mysql_ids_by_partner_id.get(partner_id)
                ),
            },
        ],
    }
    if place_id in [conftest.PLACE_ID_1, conftest.PLACE_ID_4]:
        result['places'][0]['brand_slug'] = 'shoko'
    return result


def _make_round_payment_experiment_answer(enabled: bool) -> dict:
    return {
        'enabled': enabled,
        'round_settings': [
            {'round_amount': 10, 'lower_threshold': 0, 'upper_threshold': 100},
            {
                'round_amount': 100,
                'lower_threshold': 1000,
                'upper_threshold': 10000,
            },
            {
                'round_amount': 20,
                'lower_threshold': 100,
                'upper_threshold': 500,
            },
            {
                'round_amount': 50,
                'lower_threshold': 500,
                'upper_threshold': 1000,
            },
        ],
    }


def _format_expected_response(
        *,
        trans_guest_block=False,
        trans_guest_checked=False,
        option='fixed_amounts',
        default_percent=10,
        default_amount=1000,
        fixed_amounts=conftest.SENTINEL,
        fixed_percents=conftest.SENTINEL,
        show_ya_pay=True,
        min_plus_threshold=100,
        show_plus_offer=True,
        rounded_amount=None,
):
    result = {
        'trans_guest_block': trans_guest_block,
        'trans_guest_checked': trans_guest_checked,
        'option': option,
        'default_percent': default_percent,
        'default_amount': default_amount,
        'fixed_amounts': conftest.value_or_default(
            fixed_amounts, [25, 100, 300, 500],
        ),
        'fixed_percents': conftest.value_or_default(
            fixed_percents, [5, 7, 10, 15],
        ),
        'show_ya_pay': show_ya_pay,
        'min_amount': {'commission_enabled': 1, 'commission_disabled': 2},
        'max_amount': 10000,
        'show_plus_offer': show_plus_offer,
    }
    if min_plus_threshold is not None:
        result['min_plus_threshold'] = min_plus_threshold
    if rounded_amount is not None:
        result['rounded_amount'] = rounded_amount
    return result


@pytest.mark.parametrize(
    'request_params, expected_status, expected_result, expected_stats_labels,'
    'antifraud_result',
    [
        pytest.param(
            _format_request_param(recipient_id=conftest.PARTNER_ID_1),
            200,
            _format_expected_response(
                option='fixed_percents',
                default_percent=0,
                default_amount=0,
                fixed_amounts=[50, 100, 300, 500],
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_percents',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            id='by recipient_id',
        ),
        pytest.param(
            _format_request_param(
                recipient_id=conftest.PARTNER_ID_1,
                place_id=conftest.PLACE_ID_1,
            ),
            200,
            _format_expected_response(),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_amounts',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            id='by place_id',
        ),
        pytest.param(
            _format_request_param(
                qr='0000040',
                bill_amount='900',
                recipient_id=conftest.PARTNER_ID_1,
                place_id=conftest.PLACE_ID_3,
            ),
            200,
            _format_expected_response(
                option='fixed_percents',
                default_percent=0,
                default_amount=0,
                fixed_amounts=[50, 100, 300, 500],
                rounded_amount=[50, 70, 90, 140],
                show_ya_pay=False,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_percents',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            id='round_payment',
        ),
        pytest.param(
            _format_request_param(
                bill_amount='900',
                recipient_id=conftest.PARTNER_ID_1,
                place_id=conftest.PLACE_ID_4,
            ),
            200,
            _format_expected_response(
                option='fixed_percents',
                default_percent=0,
                default_amount=0,
                fixed_amounts=[50, 100, 300, 500],
                show_ya_pay=False,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_percents',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            id='round_payment_disable_by_slug',
        ),
        (
            _format_request_param(recipient_id=conftest.PARTNER_ID_4),
            200,
            _format_expected_response(),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_amounts',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
        ),
        pytest.param(
            _format_request_param(recipient_id=conftest.PARTNER_ID_4),
            200,
            _format_expected_response(
                trans_guest_block=True, trans_guest_checked=True,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_amounts',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            marks=pytest.mark.config(
                EATS_TIPS_PAYMENTS_SHOW_COMMISSION_BLOCK=True,
                EATS_TIPS_PAYMENTS_ENABLE_COMMISSION_FOR_ALL=True,
            ),
        ),
        pytest.param(
            _format_request_param(recipient_id=conftest.PARTNER_ID_4),
            200,
            _format_expected_response(
                trans_guest_block=True, trans_guest_checked=True,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_amounts',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            marks=pytest.mark.config(
                EATS_TIPS_PAYMENTS_SHOW_COMMISSION_BLOCK=True,
                EATS_TIPS_PAYMENTS_ENABLE_COMMISSION_FOR_ALL=False,
            ),
        ),
        (
            _format_request_param(recipient_id=conftest.PARTNER_ID_3),
            200,
            _format_expected_response(),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_amounts',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
        ),
        (
            _format_request_param(recipient_id=conftest.PARTNER_ID_3),
            200,
            _format_expected_response(
                min_plus_threshold=None, show_plus_offer=False,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_amounts',
                },
                {
                    'sensor': 'antifraud_get_payment_settings',
                    'status': 'False',
                },
            ],
            'block',
        ),
        (
            _format_request_param(recipient_id=conftest.NOT_FOUND_ID),
            404,
            {'code': 'not_found', 'message': 'waiter is not found'},
            None,
            'allow',
        ),
        (
            _format_request_param(recipient_id=conftest.PARTNER_ID_17),
            200,
            _format_expected_response(
                option='fixed_percents',
                default_percent=5,
                default_amount=0,
                fixed_amounts=[50, 100, 300, 500],
                show_ya_pay=False,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_percents',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
        ),
        (
            _format_request_param(recipient_id=conftest.PARTNER_ID_1),
            200,
            _format_expected_response(
                option='fixed_percents',
                default_percent=0,
                default_amount=0,
                fixed_amounts=[50, 100, 300, 500],
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_percents',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
        ),
        pytest.param(
            _format_request_param(recipient_id=conftest.PARTNER_ID_1),
            200,
            _format_expected_response(
                trans_guest_block=True,
                trans_guest_checked=True,
                option='fixed_percents',
                default_percent=0,
                default_amount=0,
                fixed_amounts=[50, 100, 300, 500],
                show_plus_offer=True,
            ),
            [
                {
                    'sensor': 'success',
                    'handle': 'payment_settings',
                    'payment_option': 'fixed_percents',
                },
                {'sensor': 'antifraud_get_payment_settings', 'status': 'True'},
            ],
            'allow',
            marks=pytest.mark.config(
                EATS_TIPS_PAYMENTS_SHOW_COMMISSION_BLOCK=False,
                EATS_TIPS_PAYMENTS_ENABLE_COMMISSION_FOR_ALL=True,
            ),
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/new-payment-design',
    experiment_name='eda_tips_payments_new_payment_design',
    args=[{'name': 'place_id', 'type': 'string', 'value': '000030'}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/new-payment-design',
    experiment_name='eda_tips_payments_new_payment_design',
    args=[{'name': 'place_id', 'type': 'string', 'value': '000010'}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/new-payment-design',
    experiment_name='eda_tips_payments_new_payment_design',
    args=[{'name': 'place_id', 'type': 'string', 'value': '000160'}],
    value={'enabled': False},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/plus-calculation',
    experiment_name='eda_tips_payments_plus_calculation',
    args=[
        {'name': 'yandex_uid', 'type': 'string', 'value': conftest.TEST_UID},
    ],
    value={
        'settings': [
            {'plus_amount_percent': 0.05, 'plus_minimal_threshold': 100},
        ],
    },
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/round_payment',
    experiment_name='round_payment',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': conftest.PLACE_ID_3},
        {'name': 'yandex_uid', 'type': 'string', 'value': conftest.TEST_UID},
    ],
    value=_make_round_payment_experiment_answer(enabled=True),
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/round_payment',
    experiment_name='round_payment',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': conftest.PLACE_ID_4},
        {'name': 'brand_slug', 'type': 'string', 'value': 'shoko'},
        {'name': 'yandex_uid', 'type': 'string', 'value': conftest.TEST_UID},
    ],
    value=_make_round_payment_experiment_answer(enabled=False),
)
@pytest.mark.config(
    EATS_TIPS_PAYMENTS_PLUS_SETTINGS=conftest.DEFAULT_PLUS_SETTINGS_CFG,
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_payment_settings(
        web_app,
        web_app_client,
        mock_uantifraud,
        mock_eats_tips_partners,
        mock_eats_tips_partners_for_settings,
        # params:
        request_params,
        expected_status,
        expected_result,
        expected_stats_labels,
        get_stats_by_list_label_values,
        antifraud_result,
):
    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v1_partner(request):
        partner_id = request.query['partner_id']
        if partner_id == conftest.NOT_FOUND_ID:
            return web.json_response(
                {'code': 'not-found', 'message': 'settings are not found'},
                status=404,
            )
        return web.json_response(
            _format_eats_tips_partners_response(
                partner_id=partner_id, place_id=request_params.get('place_id'),
            ),
            status=200,
        )

    @mock_uantifraud('/v1/tips/check')
    async def _mock_tips_check(request: test_http.Request):
        assert request.json['user_agent'] == 'some user agent'
        assert request.json['client_login_id'] == '123'
        assert request.json['client_yandex_uid'] == conftest.TEST_UID
        return web.json_response({'status': antifraud_result}, status=200)

    response = await web_app_client.get(
        '/v1/payments/payment-settings',
        params=request_params,
        headers={
            'X-Yandex-Login': '123',
            'User-Agent': 'some user agent',
            'X-Remote-IP': '1.2.3.4',
            **conftest.VALID_TVM_HEADER,
        },
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
    stats = get_stats_by_list_label_values(
        web_app['context'],
        [
            {'handle': 'payment_settings'},
            {'sensor': 'antifraud_get_payment_settings'},
        ],
    )
    expected_stats = (
        [[conftest.make_stat(labels)] for labels in expected_stats_labels]
        if expected_stats_labels
        else [[], []]
    )
    assert stats == expected_stats
