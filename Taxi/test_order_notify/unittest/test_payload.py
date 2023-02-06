import pytest

from order_notify.payloads import common as payload_logic
from test_order_notify.conftest import BASE_PAYLOAD
from test_order_notify.conftest import TRANSLATIONS_NOTIFY


@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY,
    tariff={
        'currency_sign.rub': {'ru': '₽'},
        'currency.rub': {'ru': 'руб.'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$ $CURRENCY$'},
    },
    color={'FAFBFB': {'ru': 'белый'}},
)
@pytest.mark.config(
    ROUTE_SHARING_URL_TEMPLATES={
        'yataxi': 'https://taxi.yandex.ru/route-enter/{key}',
    },
)
async def test_all_methods_exist(stq3_context, mock_tariff_zones, mock_yacc):
    raw_payload = payload_logic.RawPayload(**BASE_PAYLOAD)
    payload = payload_logic.CommonPayload(stq3_context, 'ru', raw_payload)

    result = {}
    # pylint: disable=protected-access
    for key, getter_func in payload_logic._PAYLOAD_FIELDS_MAP.items():
        assert getter_func, f'Getter for field "{key}" not exist'
        value = await getter_func(payload)
        result[key.name] = value

    # todo:
    assert result == {
        'AUTOREORDER_REASON': '',
        'CAR_INFO': 'Белый Kia Optima Е 001 КХ 777',
        'SHORT_CAR_INFO': 'Белый Kia Optima Е001КХ',
        'CAR_NUMBER': 'Е001КХ',
        'CASHBACK': '',
        'PERFORMER_PHONE': '+70001112233,0000',
        'PERFORMER_NAME': 'Evgeny',
        'DUE': '18:52',
        'ESTIMATE': '3–5',
        'SHORT_ESTIMATE': '5',
        'FORMATTED_COMPLEMENT_PRICE': '',
        'FORMATTED_COUPON': '',
        'FORMATTED_TOTAL_COST': '100 ₽',
        'FORMATTED_USER_COST': '100 ₽',
        'SHARE_ROUTE_URL': 'clck_url',
    }


@pytest.mark.parametrize(
    'plate, use_short, expected_plate',
    [
        pytest.param('E001KX777', False, 'E 001 KX 777', id='type 1'),
        pytest.param('E001KX777', True, 'E001KX', id='type 1, short'),
        pytest.param('AB001777', False, 'AB 001 777', id='type 2'),
        pytest.param('AB001777', True, 'AB001', id='type 2, short'),
        pytest.param('Е001КХ777', False, 'Е 001 КХ 777', id='type 1 RU'),
        pytest.param('АВ001777', False, 'АВ 001 777', id='type 2 RU'),
        pytest.param('incorrect', True, 'incorrect', id='incorrect'),
        pytest.param('01КG703АDQ', False, '01КG 703АDQ', id='KG'),
        pytest.param('01КG703АDQ', True, '703АDQ', id='KG, short'),
        pytest.param(None, True, '', id='empty'),
    ],
)
async def test_car_number(stq3_context, plate, use_short, expected_plate):
    payload = {**BASE_PAYLOAD, 'car_number': plate}
    raw_payload = payload_logic.RawPayload(**payload)
    payload = payload_logic.CommonPayload(stq3_context, 'ru', raw_payload)

    # pylint: disable=protected-access
    result = await payload._get_car_number(use_short)
    assert result == expected_plate


async def test_car_number_en(stq3_context):
    payload = {**BASE_PAYLOAD, 'car_number': 'У001УУ777'}  # ru
    raw_payload = payload_logic.RawPayload(**payload)
    payload = payload_logic.CommonPayload(stq3_context, 'en', raw_payload)

    # pylint: disable=protected-access
    result = await payload._get_car_number(use_short=False)
    assert result == 'Y 001 YY 777'
