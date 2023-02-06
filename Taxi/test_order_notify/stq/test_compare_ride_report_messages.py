import copy
import typing

import pytest

from order_notify import compare_report_settings
from order_notify.generated.stq3 import stq_context
from order_notify.repositories.email.message import Message
from order_notify.repositories.order_info import OrderData
from order_notify.stq import compare_ride_report_messages


NOT_FOUND_LOG = compare_report_settings.NOT_FOUND_LOG
ERROR_LOG = compare_report_settings.ERROR_LOG
DIFF_LOG = compare_report_settings.DIFF_LOG


PY2_MAP = (
    'https://tc.tst.mobile.yandex.net/get-map/1.x/?'
    'lang=ru&lg=0&scale=1&pt=37.58116,55.79221,'
    'comma_solid_red~37.56998,55.78875,comma_solid_blue'
    '&l=map&cr=0&pl=c:3C3C3CFF,w:5,37.5758552551,55.7919044495,'
    '37.5741767883,55.7916069031&bbox=37.62525,55.78943'
    '~37.58209,55.79250'
)

PY3_MAP = (
    'https://tc.tst.mobile.yandex.net/get-map/1.x/?'
    'l=map&cr=0&lg=0&scale=1&lang=ru&pt=37.58116,55.79221,'
    'comma_solid_red~37.56997,55.78876,comma_solid_blue&'
    'pl=c:3C3C3CFF,w:5,37.57585525512695,55.79190444946289,'
    '37.57417678833008,55.79160690307617&bbox=37.62582,55.78943'
    '~37.58208,55.79251'
)


DST_POINTS = ['point_1', 'point_2']


DEFAULT_VARS: dict = {
    'title': 'k',
    'logo_host': 'kslxas',
    'logo_url': 'kkndcns',
    'logo_title': 'dcaccad',
    'map_size': 'vat_perc',
    'route_title': 'g_gg',
    'src_pt': 'dsvfv',
    'start_transporting_time': 'dknca',
    'dst_pt': 'kjbcvq',
    'finish_transporting_time': 'ljbcalk',
    'destination_changed': False,
    'payment_title': 'hcgscvjav',
    'show_fare_with_vat_only': False,
    'tips_sign': 'qwgcdvblc',
    'payment_method_corp': 'qyjckvcjbkc',
    'payment_method_title': 'htqcvkljbc',
    'details_title': 'qjhvckjbc',
    'th_car': 'pipkn32n',
    'car_color': 'kjlknc5cx',
    'car_model': 'ljkblk;ds',
    'car_number': '2jblkfbe',
    'fare_type': 'ljvblkcc',
    'tariff': 'ncbdkjd',
    'date_title': 'jbdwoomc',
    'date': 'date',
    'duration': 'knlncx',
    'ride_time': 'jbcak',
    'ride_dist_round': 'jlwccx',
    'show_user_fullname': False,
    'show_order_id': False,
    'receipt_title': 'knnknna',
    'bill_title': 'bill',
    'support_url': 's_urll',
    'support_title': 'supp_titt',
    'is_corp_report': False,
    'carrier_title': 'c_tt',
    'th_driver': 'cf_dr',
    'driver_name': 'dr_name',
    'th_park': 'td_pa',
    'park_legal_name': 'p_l_n',
    'legal_address_title': 'l_a_n',
    'park_legal_address': 'p_l_a',
    'show_ogrn_and_unp': False,
    'unsubscribe_text': 'uns_text',
    'fare_title': 'fare_title',
    'ride_title': 'ride_title',
    'tips_title': 'tips_title',
    'tips_percent': 20.0,
    'vat_title': 'vat',
    'dst_changed': 'changed',
    'ogrn_title': 'ogr',
    'park_ogrn': 'ogr',
    'unp_title': 'unp',
    'park_inn': 'p_in',
}


DEFAULT_MESSAGE_ARGS: dict = {
    'campaign_slug': 'campaign_slug',
    'from_name': 'name',
    'from_email': 'f@email.com',
    'to_email': 'sf@email.ru',
    'template_vars': {
        'sizeless_maps_url': PY3_MAP,
        'dst_points': DST_POINTS[:-1],
        'payment_phrase': '••••&nbsp;1234',
        'payment_icon': 'card',
        'receipt_mode': 'receipt',
        'receipt_url': None,
        'unsubscribe_host': (
            'host/email/unsubscribe/?confirmation_code=conf_code&lang=lang'
        ),
        'taxi_host': 'host',
        'confirmation_code': 'conf_code',
        'lang_param': '&lang=lang',
        'cost_without_vat_sign': '123,5',
        'vat_perc': '20',
        'vat_value_sign': '24,7',
        'total_cost_sign': '98,8',
        **DEFAULT_VARS,
    },
}


@pytest.fixture(name='mock_functions')
def mock_functions_fixture(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.construct_user_message = Counter()
            self.construct_corp_message = Counter()
            self.get_order_info = Counter()

    counters = Counters()

    @patch('order_notify.repositories.order_info.get_order_info')
    async def _get_order_info(
            context: stq_context.Context, order_id: str,
    ) -> typing.Optional[OrderData]:
        counters.get_order_info.call()
        assert order_id in [str(i) for i in range(8)]
        if order_id == '0':
            return None

        payment_tech: dict = {'type': 'corp'}
        if order_id == '7':
            payment_tech['need_accept'] = True

        return OrderData(
            brand='',
            country='',
            order={'_id': order_id, 'payment_tech': payment_tech},
            order_proc={'order': {}},
        )

    @patch('order_notify.repositories.email.message.' 'construct_user_message')
    async def _construct_user_message(
            context: stq_context.Context,
            order_data: OrderData,
            locale: str,
            personal_email_id: typing.Optional[str] = None,
    ) -> typing.Optional[Message]:
        counters.construct_user_message.call()

        if order_data.order['_id'] == '1':
            raise Exception('user')

        if order_data.order['_id'] in ('2', '4'):
            return None

        message_args = copy.deepcopy(DEFAULT_MESSAGE_ARGS)
        if order_data.order['_id'] == '5':
            message_args['template_vars']['g'] = 'h'

        if order_data.order['_id'] == '7':
            message_args['template_vars']['cost_without_vat_sign'] = '123'
            message_args['template_vars']['vat_value_sign'] = '24'
            message_args['template_vars']['total_cost_sign'] = '98'

        return Message(**message_args)

    @patch('order_notify.repositories.email.message.' 'construct_corp_message')
    async def _construct_corp_message(
            context: stq_context.Context, order_data: OrderData, locale: str,
    ) -> typing.Optional[Message]:
        counters.construct_corp_message.call()

        if order_data.order['_id'] == '1':
            raise Exception('corp')

        if order_data.order['_id'] in ('2', '3', '5'):
            return None

        return Message(**DEFAULT_MESSAGE_ARGS)

    return counters


@pytest.mark.parametrize(
    'order_id, user_vars, corp_vars, expected_logs_cnt',
    [
        pytest.param('0', {}, {}, [1, 0, 0], id='no_order_data'),
        pytest.param('1', {}, {}, [0, 2, 0], id='raise_error'),
        pytest.param('2', {}, {}, [2, 0, 0], id='no_messages'),
        pytest.param('3', {}, {}, [1, 0, 0], id='no_corp_message'),
        pytest.param('4', {}, {}, [1, 0, 0], id='no_user_message'),
        pytest.param(
            '5',
            {},
            {},
            [1, 0, 1],
            id='no_corp_message_cant_find_in_user_message',
        ),
        pytest.param('6', {}, None, [0, 0, 0], id='ok'),
        pytest.param('7', {}, None, [0, 0, 0], id='corp_need_accept'),
    ],
)
async def test_compare_ride_report_messages(
        stq3_context: stq_context.Context,
        stq,
        mock_functions,
        caplog,
        order_id,
        expected_logs_cnt,
        user_vars,
        corp_vars,
):
    default_vars = {
        'user': 'vars',
        'from_name': 'name',
        'from_email': 'f@email.com',
        'to_email': 'sf@email.ru',
        'sizeless_maps_url': PY2_MAP,
        'dst_points': DST_POINTS,
        'compare_payment_phrase': '1234',
        'compare_payment_icon': 'card',
        'payment_method_card2': True,
        'receipt_mode': 'none',
        'ride_receipt_url': None,
        'taxi_host': 'host',
        'confirmation_code': 'conf_code',
        'lang_param': '&lang=lang',
        'without_vat_ride_sign': '123,5',
        'country_vat_perc': '20',
        'vat_sign': '24,7',
        'total_cost_sign': '98,8',
    }
    default_vars.update(DEFAULT_VARS)
    if user_vars is not None:
        user_vars.update(default_vars)
    if corp_vars is not None:
        corp_vars.update(default_vars)

    await compare_ride_report_messages.task(
        context=stq3_context,
        order_id=order_id,
        user_vars=user_vars,
        corp_vars=corp_vars,
    )
    not_found_log_cnt = 0
    error_log_cnt = 0
    diff_log_cnt = 0
    for record in caplog.records:
        not_found_log_cnt += int(NOT_FOUND_LOG in record.message)
        error_log_cnt += int(ERROR_LOG in record.message)
        diff_log_cnt += int(DIFF_LOG in record.message)

    logs_cnt = [not_found_log_cnt, error_log_cnt, diff_log_cnt]

    assert logs_cnt == expected_logs_cnt
