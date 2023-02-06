import typing

from aiohttp import web
import pytest

from eats_tips_payments.utils.plus import calculate as plus_calc
from test_eats_tips_payments import conftest


EXPERIMENT_UID_ARG = {
    'name': 'yandex_uid',
    'type': 'string',
    'value': conftest.TEST_UID,
}


def _format_eats_tips_partners_response(*, place_id=None):
    result = {
        'info': {
            'id': 'partner_id_1',
            'b2p_id': 'partner_b2p_id_1',
            'display_name': '',
            'full_name': '',
            'phone_id': 'phone_id_1',
            'saving_up_for': '',
            'best2pay_blocked': False,
            'registration_date': '1970-01-01T03:00:00+03:00',
            'is_vip': False,
            'blocked': False,
        },
        'places': [
            {
                'place_id': place_id or conftest.PLACE_ID_2,
                'title': '',
                'address': '',
                'confirmed': True,
                'show_in_menu': True,
                'roles': [],
            },
        ],
    }
    if place_id == conftest.PLACE_ID_1:
        result['places'][0]['brand_slug'] = 'shoko'
    return result


def make_pytest_param(
        amount,
        guest_percent,
        expected_commission,
        *,
        id=None,  # pylint: disable=redefined-builtin, invalid-name
        place_id: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        amount,
        guest_percent,
        expected_commission,
        conftest.value_or_default(place_id, None),
        id=id,
    )


@pytest.mark.config(
    EATS_TIPS_PAYMENTS_PLUS_SETTINGS=conftest.DEFAULT_PLUS_SETTINGS_CFG,
)
@pytest.mark.parametrize(
    'amount, guest_percent, expected_commission, place_id',
    [
        make_pytest_param(100, False, 0.0),
        make_pytest_param(100, True, 6.0),
        make_pytest_param(101, True, 7.0),
        make_pytest_param(99, True, 6.0),
        make_pytest_param(
            100, True, 5.0, place_id=conftest.PLACE_ID_1, id='brand is shoko',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[{'name': 'brand_slug', 'type': 'string', 'value': 'shoko'}],
    value={
        'commission_percent': 5,
        'commission_should_be_compensated': True,
        'theme_name': 'shoko',
        'promo_url': 'test_promo_url',
        'promo_image_url': 'test_promo_image_url',
    },
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[],
    value={'commission_percent': 6, 'commission_should_be_compensated': False},
)
async def test_get_on_amount_change_commissions(
        taxi_eats_tips_payments_web,
        mock_eats_tips_partners,
        # params:
        amount,
        guest_percent,
        expected_commission,
        place_id,
):
    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v1_partner(request):
        return web.json_response(
            _format_eats_tips_partners_response(place_id=place_id), status=200,
        )

    params = {
        'recipient_id': conftest.PARTNER_ID_1,
        'amount': amount,
        'guest_percent': guest_percent,
        'qr': '1000',
    }
    if place_id:
        params['place_id'] = place_id
    response = await taxi_eats_tips_payments_web.get(
        '/v1/payments/on-amount-change', params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert result.get('commission') == expected_commission
    # plus must be 0 cuz no authorized
    assert result.get('plus_amount') == 0


@pytest.mark.config(
    TVM_USER_TICKETS_ENABLED=True, TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.parametrize(
    (
        'amount',
        'guest_percent',
        'plus_cfg',
        'qr_param',
        'expected_place_id',
        'expected_plus',
    ),
    (
        (1, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 0),
        (50, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 0),
        (100, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 5),
        (109, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 5),
        (110, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 6),
        (100, True, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 5),
        # (105 + 0.05 * 105) * 0.05 = (105+5.25) * 0.05 = 5.5125 -> 6
        (105, True, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 6),
        # 250 * 0.05 = 12.5 -> 13
        (250, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 13),
        # check no enabled
        (100, False, {'enabled': False}, '40', '3', 0),
        (1000, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 100),
        (5000, False, conftest.DEFAULT_PLUS_SETTINGS_CFG, '40', '3', 500),
        # check max_amount_per_transaction
        (
            10000,
            False,
            {'enabled': True, 'max_amount_per_transaction': 100},
            '40',
            '3',
            100,
        ),
        (
            20000,
            False,
            conftest.DEFAULT_PLUS_SETTINGS_CFG,
            '40',
            '3',
            plus_calc.PLUS_MAX_AMOUNT_FALLBACK,
        ),
        # check max_amount_per_transaction fallback
        (
            20000,
            False,
            {'enabled': True},
            '40',
            '3',
            plus_calc.PLUS_MAX_AMOUNT_FALLBACK,
        ),
    ),
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[{'name': 'brand_slug', 'type': 'string', 'value': 'shoko'}],
    value={
        'commission_percent': 5,
        'commission_should_be_compensated': True,
        'theme_name': 'shoko',
        'promo_url': 'test_promo_url',
        'promo_image_url': 'test_promo_image_url',
    },
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[],
    value={'commission_percent': 6, 'commission_should_be_compensated': False},
)
async def test_get_on_amount_change_plus(
        taxi_eats_tips_payments_web,
        mock_eats_tips_partners,
        mocked_tvm,
        client_experiments3,
        taxi_config,
        amount,
        guest_percent,
        plus_cfg,
        qr_param,
        expected_place_id,
        expected_plus,
):
    taxi_config.set_values({'EATS_TIPS_PAYMENTS_PLUS_SETTINGS': plus_cfg})

    client_experiments3.add_record(
        consumer='eats-tips-payments/plus-calculation',
        experiment_name='eda_tips_payments_plus_calculation',
        args=[EXPERIMENT_UID_ARG],
        value={
            'settings': [
                {'plus_amount_percent': 0.05, 'plus_minimal_threshold': 100},
                {'plus_amount_percent': 0.10, 'plus_minimal_threshold': 1000},
            ],
        },
    )

    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v1_partner(request):
        return web.json_response(
            _format_eats_tips_partners_response(), status=200,
        )

    response = await taxi_eats_tips_payments_web.get(
        '/v1/payments/on-amount-change',
        params={
            'recipient_id': conftest.PARTNER_ID_1,
            'amount': amount,
            'guest_percent': guest_percent,
            'qr': qr_param,
        },
        headers=conftest.VALID_TVM_HEADER,
    )
    result = await response.json()
    assert result.get('plus_amount') == expected_plus


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.config(
    TVM_USER_TICKETS_ENABLED=True,
    TVM_API_URL='$mockserver/tvm',
    EATS_TIPS_PAYMENTS_PLUS_SETTINGS=conftest.DEFAULT_PLUS_SETTINGS_CFG,
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/plus-calculation',
    experiment_name='eda_tips_payments_plus_calculation',
    args=[EXPERIMENT_UID_ARG],
    value={
        'settings': [
            {'plus_amount_percent': 0.05, 'plus_minimal_threshold': 100},
        ],
    },
)
@pytest.mark.parametrize(
    'qr_param, expected_place_id, expected_plus',
    (
        # кафе официанта в эксперименте
        ('40', '3', 5),
        # админ кафе в эксперименте
        ('30', '3', 5),
        # официант без кафе, id официанта в эксперименте
        ('60', '6', 5),
    ),
)
async def test_get_on_amount_change_plus_uid(
        taxi_eats_tips_payments_web,
        mock_eats_tips_partners,
        mocked_tvm,
        qr_param,
        expected_place_id,
        expected_plus,
):
    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v1_partner(request):
        return web.json_response(
            _format_eats_tips_partners_response(), status=200,
        )

    params = {
        'recipient_id': conftest.PARTNER_ID_1,
        'amount': 100,
        'guest_percent': False,
        'qr': qr_param,
    }
    response = await taxi_eats_tips_payments_web.get(
        '/v1/payments/on-amount-change',
        params=params,
        headers=conftest.VALID_TVM_HEADER,
    )
    result = await response.json()
    assert result.get('plus_amount') == expected_plus
