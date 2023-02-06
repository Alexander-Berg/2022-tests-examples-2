# encoding: utf-8

import datetime
import json

import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import experiments3
from taxi.internal import dbh
from taxi.internal.order_kit import const
from taxi.internal.order_kit import exceptions
from taxi.internal.order_kit import invoice_handler
from taxi.internal.order_kit.plg import order_fsm
from taxi.internal.order_kit.plg import status_handling, ordersync
from taxi.util import decimal

from cardstorage_mock import mock_cardstorage


@pytest.mark.filldb()
@pytest.mark.asyncenv('async')
@pytest.mark.parametrize('prev_status,stat_upd_kwargs,expected_status', [
    (
        (dbh.orders.STATUS_PENDING, None),
        dict(status=dbh.orders.STATUS_ASSIGNED),
        (dbh.orders.STATUS_ASSIGNED, None),
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, None),
        dict(taxi_status=dbh.orders.TAXI_STATUS_DRIVING),
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_DRIVING),
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_DRIVING),
        dict(status=dbh.orders.STATUS_PENDING, taxi_status=None),
        (dbh.orders.STATUS_PENDING, None),
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_TRANSPORTING),
        dict(status=dbh.orders.STATUS_FINISHED,
             taxi_status=dbh.orders.TAXI_STATUS_TRANSPORTING),
        (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_TRANSPORTING),
    ),
])
@pytest.inline_callbacks
def test_build_new_status(prev_status, stat_upd_kwargs, expected_status):
    stat_upd = _build_status_updates_obj(**stat_upd_kwargs)
    f = status_handling.order_fsm.OrderFsm(dbh.order_proc.Doc({}))
    f.status = prev_status[0]
    f.taxi_status = prev_status[1]
    yield f.handle_event(stat_upd)
    assert f.status, f.taxi_status == expected_status


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.mark.parametrize('driving_off', [True, False])
@pytest.mark.parametrize('prev_status,new_status,reason_code,expected', [
    (
        (dbh.orders.STATUS_PENDING, None),
        (dbh.orders.STATUS_PENDING, None),
        dbh.order_proc.STATUS_UPDATE_CREATE,
        [status_handling._HANDLE_CREATION],
    ),
    (
        (dbh.orders.STATUS_PENDING, None),
        (dbh.orders.STATUS_ASSIGNED, None),
        None,
        [status_handling._HANDLE_ASSIGNING],
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_DRIVING),
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_WAITING),
        None,
        [status_handling._HANDLE_WAITING],
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_WAITING),
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_TRANSPORTING),
        None,
        [status_handling._HANDLE_TRANSPORTING],
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_TRANSPORTING),
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_TRANSPORTING),
        None,
        [],
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_TRANSPORTING),
        (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_COMPLETE),
        None,
        [
            status_handling._HANDLE_FINISH,
            status_handling._HANDLE_COMPLETE,
            status_handling._HANDLE_POST_FINISH,
        ],
    ),
    (
        (dbh.orders.STATUS_ASSIGNED, dbh.orders.TAXI_STATUS_WAITING),
        (dbh.orders.STATUS_CANCELLED, dbh.orders.TAXI_STATUS_WAITING),
        None,
        [
            status_handling._HANDLE_FINISH,
            status_handling._HANDLE_CANCEL_BY_USER,
            status_handling._HANDLE_POST_FINISH,
        ],
    ),
    (
        (dbh.orders.STATUS_PENDING, None),
        (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_EXPIRED),
        None,
        [
            status_handling._HANDLE_FINISH,
            status_handling._HANDLE_SEARCH_FAILED,
            status_handling._HANDLE_POST_FINISH,
        ],
    ),
    (
        (dbh.orders.STATUS_PENDING, None),
        (dbh.orders.STATUS_PENDING, None),
        dbh.order_proc.STATUS_UPDATE_REJECT,
        [
            status_handling._HANDLE_OFFER_REJECT,
        ],
    ),
    (
        (dbh.orders.STATUS_PENDING, None),
        (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_FAILED),
        dbh.order_proc.FAILED_REASON_AUTOCANCEL,
        [
            status_handling._HANDLE_FINISH,
            status_handling._HANDLE_FAIL_BY_PARK,
            status_handling._HANDLE_POST_FINISH,
        ],
    ),
    (
        (dbh.orders.STATUS_PENDING, None),
        (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_FAILED),
        None,
        [
            status_handling._HANDLE_FINISH,
            status_handling._HANDLE_FAIL_BY_PARK,
            status_handling._HANDLE_POST_FINISH,
        ],
    ),
])
def test_detect_handler_keys(driving_off, prev_status, new_status, reason_code, expected):
    keys = status_handling._detect_handler_keys(
        prev_status, new_status, reason_code, driving_off=driving_off
    )
    assert keys == expected


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_handle_new_status():
    # Check that only objects with `need_handling=True` are handled

    stat_upd_kwargs_list = [
        dict(status=dbh.orders.STATUS_PENDING,
             reason_code=dbh.order_proc.STATUS_UPDATE_CREATE),
        dict(status=dbh.orders.STATUS_ASSIGNED, need_handling=True),
        dict(taxi_status=dbh.orders.TAXI_STATUS_DRIVING, need_handling=True),
        dict(taxi_status=dbh.orders.TAXI_STATUS_WAITING, need_handling=True),
    ]
    Order = dbh.orders.Doc
    order = Order({Order._id: 'order_1'})
    Proc = dbh.order_proc.Doc
    proc = Proc({
        Proc._id: order._id,
        Proc.order_info: {
            Proc.order_info.statistics.key: {
                Proc.order_info.statistics.status_updates.key: [
                    _build_status_updates_obj(**kwargs)
                    for kwargs in stat_upd_kwargs_list
                ],
            },
        },
    })
    log_extra = {'_link': '123'}

    calls = []

    @async.inline_callbacks
    def _handle_assigning(order_state, log_extra):
        yield
        calls.append(status_handling._HANDLE_ASSIGNING)

    handlers_map = {
        status_handling._HANDLE_ASSIGNING: _handle_assigning,
        status_handling._HANDLE_WAITING: None,
    }

    yield status_handling._handle_new_status(
        proc, handlers_map, 3, log_extra=log_extra
    )
    calls_for_keys = [
        status_handling._HANDLE_ASSIGNING,
    ]
    assert calls == calls_for_keys


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_keeping_handled_keys(patch):
    # Test that we keep keys (put into `handled_keys`) for any
    # `status_updates` object with `need_handling in (True, False)`

    statuses = iter(['one', 'two', 'three'])
    keys = {
        'one': [11, 12],
        'two': [21],
        'three': [31, 32],
    }
    handlers_map = dict((k, None) for k in [11, 12, 21, 31, 32])
    proc = dbh.order_proc.Doc({'_id': 'order_id'})
    proc.order_info.statistics.status_updates = [
        _build_status_updates_obj(),
        _build_status_updates_obj(need_handling=False),
        _build_status_updates_obj(need_handling=True),
    ]

    @patch('taxi.internal.order_kit.plg.status_handling._next_status')
    def _build_new_status(_):
        return statuses.next()

    @patch('taxi.internal.order_kit.plg.status_handling._detect_handler_keys')
    def _detect_handler_keys(prev_status, new_status, reason_code, driving_off=False):
        return keys[new_status]

    handled_keys = yield status_handling._handle_new_status(
        proc, handlers_map, 2, log_extra=None
    )
    assert handled_keys == [21, 31, 32]


def _build_status_updates_obj(**kwargs):
    proc = dbh.order_proc.Doc()
    proc.order_info.statistics.status_updates = []
    obj = proc.order_info.statistics.status_updates.new()
    for attr in kwargs:
        setattr(obj, attr, kwargs[attr])
    return obj


@pytest.mark.filldb(
    orders='driver_totw_forwarding',
    order_proc='driver_totw_forwarding'
)
@pytest.mark.parametrize('update_proc_in_procaas', [False, True])
@pytest.inline_callbacks
def test_driver_forwarding_base(areq_request, update_proc_in_procaas):
    yield config.PY2_PROCESSING_UPDATE_PROC_IN_PROCAAS.save(update_proc_in_procaas)

    @areq_request
    def requests_request(method, url, **kwargs):
        assert url == ('http://taxi-protocol.taxi.tst.yandex.net/'
                       'voicegatewaysobtain')
        body = {
            'gateways': [{
                'gateway': {
                    'phone': '+749500000000',
                    'ext': '007'
                }
            }]
        }
        return areq_request.response(200, body=json.dumps(body))

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    proc._commit_by_procaas = True
    state = order_fsm.OrderFsm(proc)
    state._candidate_index = 2

    yield status_handling._add_driver_forwarding_if_need(state)

    new_proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')

    if update_proc_in_procaas:
        assert proc.preupdated_proc_data.candidate_vgw_phone == {
            'candidates.2.forwarding': {
                'phone': '+749500000000',
                'ext': '007'
            }
        }
        assert new_proc.candidates[2].forwarding == {}
    else:
        assert proc.preupdated_proc_data.candidate_vgw_phone is None
        assert new_proc.candidates[2].forwarding == {
            'phone': '+749500000000',
            'ext': '007'
        }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(
    orders='driver_totw_forwarding',
    order_proc='driver_totw_forwarding'
)
@pytest.inline_callbacks
def test_driver_forwarding_no_performer(areq_request):

    @areq_request
    def requests_request(method, url, **kwargs):
        body = {
            'gateways': [{
                'gateway': {
                    'phone': '+749500000000',
                    'ext': '007'
                }
            }]
        }
        return areq_request.response(200, body=json.dumps(body))

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id_1')

    # bug 17882
    state = order_fsm.OrderFsm(proc)
    for event in proc.order_info.statistics.status_updates:
        state.handle_event(event)
        if event.get('s') == 'assigned':
            assert state._candidate_index == 0
            assert state.performer
            assert not state.proc.performer.candidate_index
            yield status_handling._add_driver_forwarding_if_need(state)

    assert proc.candidates[0].forwarding == {
        'phone': u'+749500000000', 'ext': u'007'}


@pytest.mark.filldb(
    orders='driver_totw_forwarding',
    order_proc='driver_totw_forwarding_exists'
)
@pytest.inline_callbacks
def test_driver_forwarding_base_forwarding_exists(areq_request):

    @areq_request
    def requests_request(method, url, **kwargs):
        raise NotImplementedError  # must not be called

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)
    state._candidate_index = 2

    yield status_handling._add_driver_forwarding_if_need(state)

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')

    assert proc.candidates[2].forwarding == {
        'phone': '+71111111111',
        'ext': '111'
    }


@pytest.mark.filldb(
    orders='driver_totw_forwarding',
    order_proc='driver_totw_forwarding'
)
@pytest.mark.parametrize('code, response, forwarding', [
    (
        200,
        {
            'gateways': [{
                'gateway': {
                    'phone': '+749500000000',
                    'ext': '007',
                },
            }]
        },
        {
            'phone': '+749500000000',
            'ext': '007',
        }
    ),
    (500, None, {'phone': '', 'ext': ''}),
    (502, None, {'phone': '', 'ext': ''}),
    (400, None, {'phone': '', 'ext': ''}),
    (404, None, {'phone': '', 'ext': ''}),
    (
        200,
        {
            'gateways': [{
                'error': {
                    'code': 'test_code',
                    'message': 'test_message',
                },
            }]
        },
        {'phone': '', 'ext': ''}
    ),
    (
        200,
        {
            'bla-bla-bla': 'bla-bla-bla',
        },
        {'phone': '', 'ext': ''}
    ),
])
@pytest.inline_callbacks
def test_driver_forwarding_cant_obtain_voice_gateway(
        areq_request, code, response, forwarding):

    @areq_request
    def requests_request(method, url, **kwargs):
        assert url == ('http://taxi-protocol.taxi.tst.yandex.net/'
                       'voicegatewaysobtain')
        return areq_request.response(code, body=json.dumps(response))

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)
    state._candidate_index = 2

    yield status_handling._add_driver_forwarding_if_need(state)

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')

    assert proc.candidates[2].forwarding == forwarding


def _to_decimal_or_none(x):
    if x is not None:
        return decimal.Decimal(x)
    return x


def _make_contract_object(
        empty, currency, currency_rate, offer_currency, offer_currency_rate,
        acquiring_percent, donate_multiplier, donate_discounts_multiplier,
        subventions_hold_delay, rebate_percent, ind_bel_nds_percent,
        max_cost_for_commission):
    return dbh.orders.BillingContractInfo(
        empty=empty,
        currency=currency,
        currency_rate=_to_decimal_or_none(currency_rate),
        offer_currency=offer_currency,
        offer_currency_rate=_to_decimal_or_none(offer_currency_rate),
        acquiring_percent=_to_decimal_or_none(acquiring_percent),
        donate_multiplier=_to_decimal_or_none(donate_multiplier),
        donate_discounts_multiplier=_to_decimal_or_none(
            donate_discounts_multiplier),
        subventions_hold_delay=subventions_hold_delay,
        rebate_percent=_to_decimal_or_none(rebate_percent),
        ind_bel_nds_percent=_to_decimal_or_none(ind_bel_nds_percent),
        max_cost_for_commission=_to_decimal_or_none(max_cost_for_commission),
    )


@pytest.mark.filldb(
    cities='for_set_billing_contract_test',
    holded_subventions_config='for_set_billing_contract_test',
    orders='for_set_billing_contract_test',
    parks='for_set_billing_contract_test',
    currency_rates='for_set_billing_contract_test',
    commission_contracts='for_set_billing_contract_test',
)
@pytest.mark.now(datetime.datetime(2015, 4, 3).isoformat())
@pytest.mark.parametrize('order_id,expected_billing_contract_info', [
    # commission contract has no acquiring percent for all orders till
    # similar comment
    (
        'good_order_id',
        _make_contract_object(
            False, 'USD', '0.023', 'EUR', '0.034', '0.035', '1.06', '1.06',
            666, None, '0.2', None
        ),
    ),
    # old order that doesn't have contract field at all
    (
        'no_contract_at_all_good_order_id',
        _make_contract_object(
            False, 'USD', '0.023', 'EUR', '0.034', '0.035', '1.06', '1.06',
            666, None, '0.2', None
        ),
    ),
    (
        'unknown_park_id_order_id',
        _make_contract_object(
            False, None, None, None, None, None, None, None, None, None, None,
            None
        ),
    ),
    (
        'unknown_city_id_order_id',
        _make_contract_object(
            False, 'USD', None, None, None, '0.035', '1.06', '1.06',
            666, None, '0.2', None
        ),
    ),
    (
        'no_performer_order_id',
        _make_contract_object(
            True, None, None, None, None, None, None, None, None, None, None,
            None
        ),
    ),
    (
        'unknown_currency_rate_order_id',
        _make_contract_object(
            False, 'KZT', None, None, None, '0.045', '1.06', '1.06',
            666, None, None, None
        ),
    ),
    (
        'contract_already_set_order_id',
        _make_contract_object(
            False, 'EUR', '0.0138', None, None, '0.09', '1.00', None,
            None, None, None, None
        ),
    ),
    (
        'no_commission_contract_order_id',
        _make_contract_object(
            False, 'USD', '0.023', 'EUR', '0.034', None, '1.06', '1.06',
            0, None, '0.2', None
        ),
    ),
    (
        'contract_already_set_with_discounts_multiplier_order_id',
        _make_contract_object(
            False, 'EUR', '0.0138', None, None, '0.09', '1.00', '1.06',
            None, None, None, None
        ),
    ),
    (
        'custom_discounts_multiplier_order_id',
        _make_contract_object(
            False, 'ILS', '1.0', 'ILS', '1.0', '0.035', '1.00', '1.06',
            0, None, None, None
        ),
    ),

])
@pytest.inline_callbacks
def test_get_billing_contract_info(order_id, expected_billing_contract_info):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    billing_contract_info = yield status_handling._get_billing_contract_info(
        _make_proc_from_order(order), False, log_extra=None
    )
    assert billing_contract_info == expected_billing_contract_info


@pytest.mark.config(
    CORP_ZONE_CLASS_REBATES={
        'yerevan': {
            'econom': '0.01',
        }
    },
    CORP_COUNTRY_CLASS_FALLBACK_REBATES={
        'rus': {
            'econom': '0.02',
            'comfortplus': '0.03',
            'default_rebate': '0.04',
        }
    },
    BILLING_CORP_REBATE_COUNTRIES=['arm'],
    CUSTOM_REBATES_ENABLED=True,
    CORP_REBATE_FETCH_TARIFF_FROM_PERFORMER={
        'level': 'disabled',
        'since_due': '2099-01-01T00:00:00+00:00'
    }
)
@pytest.mark.filldb(
    cities='for_set_billing_contract_test',
    holded_subventions_config='for_set_billing_contract_test',
    orders='for_set_billing_contract_test',
    parks='for_set_billing_contract_test',
    currency_rates='for_set_billing_contract_test',
    tariff_settings='for_set_billing_contract_test',
    commission_contracts='for_unknown_set_billing_contract_test',
)
@pytest.mark.now(datetime.datetime(2015, 4, 3).isoformat())
@pytest.mark.parametrize(
    'order_id,expected_billing_contract_info, bc_response, rebate_fetch_mode',
    [
        # commission contract has acquiring percent for all orders below
        (
            'good_order_id',
            _make_contract_object(
                False, 'USD', '0.023', 'EUR', '0.034', '0.02', '1.06', '1.06',
                666, None, '0.2', None
            ),
            None,
            'config'
        ),
        (
            'good_order_id_corp',
            _make_contract_object(
                False, 'USD', '0.023', 'EUR', '0.034', '0.02', '1.06', '1.06',
                666, '0.01', '0.2', '6000'
            ),
            None,
            'config'
        ),
(
            'good_order_id_corp',
            _make_contract_object(
                False, 'USD', '0.023', 'EUR', '0.034', '0.02', '1.06', '1.06',
                666, '0.01', '0.2', '6000'
            ),
            'external/billing_commissions_good_order_id_corp.json',
            'fallback'
        ),
        (
            'good_order_id_corp',
            _make_contract_object(
                False, 'USD', '0.023', 'EUR', '0.034', '0.02', '1.06', '1.06',
                666, '0.02', '0.2', '6001'
            ),
            'external/billing_commissions_good_order_id_corp.json',
            'service'
        ),
        (
            'no_contract_at_all_good_order_id',
            _make_contract_object(
                False, 'USD', '0.023', 'EUR', '0.034', '0.02', '1.06', '1.06',
                666, None, '0.2', None
            ),
            None,
            'config'
        ),
        (
            'unknown_park_id_order_id',
            _make_contract_object(
                False, None, None, None, None, None, None, None, None,
                None, None, None
            ),
            None,
            'config'
        ),
        (
            'unknown_city_id_order_id',
            _make_contract_object(
                False, 'USD', None, None, None, '0.02', '1.06', '1.06',
                666, None, '0.2', None
            ),
            None,
            'config'
        ),
        (
            'no_performer_order_id',
            _make_contract_object(
                True, None, None, None, None, None, None, None, None, None,
                None, None
            ),
            None,
            'config'
        ),
        (
            'unknown_currency_rate_order_id',
            _make_contract_object(
                False, 'KZT', None, None, None, '0.02', '1.06', '1.06',
                666, None, None, None
            ),
            None,
            'config'
        ),
        (
            'contract_already_set_order_id',
            _make_contract_object(
                False, 'EUR', '0.0138', None, None, '0.09', '1.00', None,
                None, None, None, None
            ),
            None,
            'config'
        ),
    ]
)
@pytest.inline_callbacks
def test_get_billing_contract_info_unknown(
    order_id,
    expected_billing_contract_info,
    bc_response,
    rebate_fetch_mode,
    mock,
    areq_request,
    patch,
    load,
):
    @patch('taxi.config.BILLING_CORP_REBATE_FETCH_MODE.get')
    @async.inline_callbacks
    def get_rebate_fetch_mode_config():
        yield
        async.return_value(rebate_fetch_mode)

    @mock
    @areq_request
    def _dummy_request(method, url, **kwargs):
        return 200, load(bc_response)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    billing_contract_info = yield status_handling._get_billing_contract_info(
        _make_proc_from_order(order), False, log_extra=None
    )
    assert billing_contract_info == expected_billing_contract_info


@pytest.mark.config(
    CORP_ZONE_CLASS_REBATES={
        'moscow': {
            'econom': '0.01',
            'express': '0.23',
        }
    },
    CORP_COUNTRY_CLASS_FALLBACK_REBATES={
        'rus': {
            'econom': '0.02',
            'comfortplus': '0.03',
            'default_rebate': '0.04',
        }
    },
    CORP_REBATE_FETCH_TARIFF_FROM_PERFORMER={
        'level': 'disabled',
        'since_due': '2099-01-01T00:00:00+00:00'
    },
    BILLING_FUNCTIONS_REBATES_OVERRIDE=[
        {
            'due': '2050-01-01T00:00:00+00:00',
            'zones': {
                'moscow': {
                    'courier': '0.08',
                }
            }
        },
        {
            'due': '2025-01-01T00:00:00+00:00',
            'zones': {
                'moscow': {
                    'courier': '0.07',
                }
            }
        },
        {
            'due': '2026-01-01T00:00:00+00:00',
            'zones': {
                'moscow': {
                    'courier': '0.08',
                }
            }
        }
    ]
)
@pytest.mark.filldb(
    orders='for_get_custom_rebate_test',
    tariff_settings='for_get_custom_rebate_test',
)
@pytest.mark.parametrize('order_id,expected_rebate,tariff_config', [
    (
        'order_msk_econom', '0.01', None
    ),
    (
        'order_spb_econom', '0.02', None
    ),
    (
        'order_msk_comfortplus', '0.03', None
    ),
    (
        'order_msk_minivan', '0.04', None
    ),
    (
        'order_ufa_no_country', None, None
    ),
    (
        'order_almaty_econom', None, None
    ),
    (
        'order_msk_courier', '0.23', None
    ),
    (
        'order_msk_courier_future_2030', '0.23', None
    ),
    (
        'order_msk_courier_future_2050', '0.23', None
    ),
    (
        'order_msk_courier', '0.23', {
            'level': 'just_logging',
            'since_due': '2099-01-01T00:00:00+00:00'
        }
    ),
    (
        'order_msk_courier', '0.23', {
            'level': 'enabled',
            'since_due': '2099-01-01T00:00:00+00:00'
        }
    ),
    (
        'order_msk_courier', '0.04', {
            'level': 'enabled',
            'since_due': '2000-01-01T00:00:00+00:00'
        }
    ),
    (
        'order_msk_courier_future_2050', '0.08', {
            'level': 'enabled',
            'since_due': '2000-01-01T00:00:00+00:00'
        }
    ),
    (
        'order_msk_courier_future_2030', '0.08', {
            'level': 'enabled',
            'since_due': '2000-01-01T00:00:00+00:00'
        }
    )
])
@pytest.mark.now('2010-08-30T13:35:56')
@pytest.inline_callbacks
def test_get_custom_rebate(order_id, expected_rebate, tariff_config, patch):
    if tariff_config:
        @patch('taxi.config.CORP_REBATE_FETCH_TARIFF_FROM_PERFORMER.get')
        @async.inline_callbacks
        def get_cargo_config():
            yield
            async.return_value(tariff_config)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    custom_rebate = yield status_handling._get_custom_rebate(order_id, order)
    if expected_rebate is not None:
        assert custom_rebate == decimal.Decimal(expected_rebate)
    else:
        assert custom_rebate is None


@pytest.mark.filldb(orders='moneyflow', order_proc='moneyflow')
@pytest.inline_callbacks
def test_handle_preupdate_proc_moneyflow():
    expected = {
        "ride": 1234,
        "tips": 12,
    }

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)

    yield status_handling._handle_preupdate_proc_moneyflow(state)
    payment_method_info = state.proc._preupdate_order_data.payment_method_info
    assert payment_method_info[0]['tag'] == 'raw_payment_tech'
    assert payment_method_info[0]['data']['paid_amount'] == expected

    yield ordersync.sync_and_handle_order(
        proc, log_extra=None
    )
    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    assert proc.payment_tech.paid_amount == expected


PRICING_DATA = {
    'driver': {
        'additional_prices': {},
        'base_price': {
            'boarding': 100,
            'destination_waiting': 0,
            'distance': 94.22160968112945,
            'requirements': 0,
            'time': 164.83333333333331,
            'transit_waiting': 0,
            'waiting': 0,
        },
        'category_prices_id': 'c/8e94ac99f32148ef8a4512c95c76d605',
        'meta': {},
        'modifications': {
            'for_fixed': [358, 352, 482, 526, 534],
            'for_taximeter': [358, 352, 482, 526, 534],
        },
        'price': {
            'components': {
                'boarding': 200,
                'destination_waiting': 0,
                'distance': 188.4432193622589,
                'requirements': 0,
                'time': 329.66666666666663,
                'transit_waiting': 0,
                'waiting': 0,
            },
        },
    },
    'geoarea_ids': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
    'taximeter_metadata': {
        'max_distance_from_point_b': 501,
        'show_price_in_taximeter': False,
    },
    'trip_information': {
        'distance': 11469.067742347717,
        'jams': True,
        'time': 970,
    },
    'user': {
        'additional_prices': {},
        'base_price': {
            'boarding': 100,
            'destination_waiting': 0,
            'distance': 94.22160968112945,
            'requirements': 0,
            'time': 164.83333333333331,
            'transit_waiting': 0,
            'waiting': 0,
        },
        'category_prices_id': 'c/8e94ac99f32148ef8a4512c95c76d605',
        'data': {},
        'meta': {},
        'modifications': {
            'for_fixed': [358, 352, 482, 526, 498, 534, 540],
            'for_taximeter': [358, 352, 482, 526, 498, 534, 540],
        },
        'price': {
            'components': {
                'boarding': 140,
                'destination_waiting': 0,
                'distance': 131.9102535535812,
                'requirements': 0,
                'time': 230.76666666666662,
                'transit_waiting': 0,
                'waiting': 0,
            },
            'strikeout': 718.1098860289255,
        },
    },
}

DECOUPLING_SUCCESS_DATA = {
    "driver_price_info": {
        "fixed_price": 45.123,
        "tariff_id": "decoupling_driver_tariff_id",
        "category_id": "decoupling_driver_category_id",
        "sp": 1.1,
        "sp_surcharge": 0.5,
        "sp_alpha": 0.6,
        "sp_beta": 0.7
    },
    "user_price_info": {
        "fixed_price": 54.123,
        "tariff_id": "decoupling_user_tariff_id",
        "category_id": "decoupling_user_category_id",
        "sp": 2.2,
        "sp_surcharge": 0.8,
        "sp_alpha": 0.9,
        "sp_beta": 1.1
    },
}


CURRENT_PRICES_DATA = {
    'kind': 'fixed',
    'user_ride_display_price': 200.0,
    'user_total_display_price': 200.0,
    'user_total_price': 200.0,
    'cashback_price': 10.0,
}


@pytest.mark.filldb(orders='tips', order_proc='tips')
@pytest.inline_callbacks
def test_handle_preupdate_proc_tips():
    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)

    status_handling._handle_preupdate_proc_tips(state)
    assert state.proc.preupdated_order_data.tips_percent == 20


@pytest.mark.filldb(orders='tips', order_proc='tips')
@pytest.inline_callbacks
def test_handle_update_tips(patch):
    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_id, intent=None, log_extra=None):
        yield

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)

    yield status_handling._handle_update_tips(state)
    assert update_transactions_call.calls == [
        {
            'args': ('order_id',),
            'kwargs': {'intent': invoice_handler.INTENT_UPGRADE_TIPS_SUM, 'log_extra': None},
        }
    ]


@pytest.mark.now('2017-08-30T13:35:56')
@pytest.inline_callbacks
def test_handle_offer_reject(patch):
    @patch('taxi.core.scheduler.call_later')
    def call_later(delay, func, *args, **kwargs):
        return

    proc = dbh.order_proc.Doc()
    candidate = proc.candidates.new()
    candidate.driver_license = 'test_driver_license'
    candidate.driver_license_personal_id = 'test_driver_license_pd_id'
    proc.candidates = [candidate]
    proc._id = 'test_order_id'
    proc.event_index = 0
    f = order_fsm.OrderFsm(proc)
    event = {
        's': 'finished',
        't': 'failed',
        'q': 'reject',
        'r': 'manual',
        'i': 0,
    }
    proc.order_info.statistics.status_updates = [event]
    f.handle_event(event)
    yield status_handling._handle_offer_reject(f)


def _decimal_or_none(x):
    if x is None:
        return None
    return decimal.Decimal(x)


def _make_proc_from_order(order):
    proc = dbh.order_proc.Doc({'order': order})
    if order.performer.park_id:
        driver_id = order.performer.park_id + '_uuid'
        proc.performer.park_id = order.performer.park_id
        proc.performer.driver_id = driver_id
        proc.performer.candidate_index = 0
        candidate = proc.candidates.new()
        candidate.tariff_currency = order.performer.tariff.currency
        candidate.tariff_class = order.performer.tariff.cls
        candidate.driver_id = driver_id
    return proc


@pytest.mark.filldb(orders='switch_to_cash', order_proc='switch_to_cash')
@pytest.mark.parametrize(
    'global_fallback, order_fallback, status, taxi_status, switch_to_cash', [
        (True, False, 'assigned', 'transporting', False),
        (False, True, 'assigned', 'transporting', False),
        (False, False, 'assigned', 'transporting', True),
        (False, False, 'assigned', 'waiting', True),
        (False, False, 'assigned', 'driving', True),
        (False, False, 'pending', None, True),
        (False, False, 'cancelled', None, False),
        (False, False, 'finished', 'cancelled', False),
        (False, False, 'finished', 'complete', False),
        (False, False, 'finished', 'failed', False),
        (False, False, 'finished', 'expired', False),
    ]
)
@pytest.mark.parametrize('order_created', [True, False])
@pytest.inline_callbacks
def test_handle_related_switched_to_cash(
        global_fallback, order_fallback, status, taxi_status, switch_to_cash,
        patch, monkeypatch, stub, mock_taximeter_notify, order_created,
        mock_send_event):
    if not order_created:
        db.order_proc.update({'_id': 'order_id'}, {'$set': {
            'order_info.order_object_skipped': True
        }})
    client_calls = []

    has_performer = taxi_status is not None
    if has_performer:
        performer = stub(
            alias_id='alias_id',
            driver_uuid='driver_uuid',
            park_id='park_id',
            db_id='db_id',
        )
    else:
        performer = None
    monkeypatch.setattr(order_fsm.OrderFsm, 'performer', performer)

    @patch('taxi.internal.notifications.order.notify_on_moved_to_cash')
    @async.inline_callbacks
    def test_notify_moved_to_cash(order_state, with_coupon, log_extra=None):
        yield
        client_calls.append(1)

    OrderProcs = dbh.order_proc.Doc
    yield db.order_proc.update({'_id': 'order_id'}, {'$set': {
        OrderProcs.order.status: status,
        OrderProcs.order.taxi_status: taxi_status,
        OrderProcs.order.version: 2,
        OrderProcs.payment_tech.billing_fallback_enabled: order_fallback,
    }})

    Order = dbh.orders.Doc
    yield db.orders.update({'_id': 'order_id'}, {'$set': {
        Order.payment_tech.billing_fallback_enabled: order_fallback,
        Order.status: status,
        Order.taxi_status: taxi_status,
        Order.payment_tech.sum_to_pay: {'ride': 100000, 'cashback': 1000},
    }})
    yield config.BILLING_DEBT_FALLBACK_ENABLED.save(global_fallback)
    yield dbh.order_proc.Doc.send_related_switch_to_cash(
        'order_id', 'some-id', 'source_order_id', )

    proc = yield dbh.order_proc.Doc.find_one_for_processing('order_id')
    yield ordersync.sync_and_handle_order(
        proc, event_index=0, log_extra=None
    )
    order = yield dbh.orders.Doc.find_one_by_id('order_id')
    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    if switch_to_cash and order_created:
        assert order.payment_tech.type == const.CASH
        assert proc.payment_tech.type == const.CASH
        assert len(client_calls) == 1
        assert mock_taximeter_notify.notify_count == 1
        assert mock_taximeter_notify.last_payment_type == 'cash'
    else:
        assert order.payment_tech.type == const.CARD
        assert order.payment_tech.type == const.CARD
        assert len(client_calls) == 0


@pytest.mark.filldb(
    orders='unbound_card', order_proc='unbound_card', cards='family',
)
@pytest.inline_callbacks
def test_handle_preupdate_order_switch_to_family_card(patch):

    mock_cardstorage(patch)

    order_id = 'f27d3d9263eb4e1ba65b584b9379cd5c'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc)
    status_handling._handle_preupdate_order_change_payment(state)

    method_info = proc._preupdate_order_data.payment_method_info
    assert method_info[0]['tag'] == 'payment_method_info'
    assert method_info[0]['data'].payment_id == 'card-new-card'
    assert method_info[0]['data'].family == {
        'is_owner': False,
        'owner_uid': '12341234',
        'limit': 250000,
        'expenses': 150000,
        'currency': 'RUB',
        'frame': 'month'
    }


@pytest.mark.parametrize('case', [
    'unbound', 'bound', 'notfound'
])
@pytest.mark.filldb(
    orders='unbound_card', order_proc='unbound_card', cards='unbound_card',
)
@pytest.inline_callbacks
def test_handle_preupdate_order_switch_to_card_unbound(patch, case):

    mock_cardstorage(patch)

    if case == 'notfound':
        yield db.cards.remove({'_id': 'id-old-card'})
    elif case == 'unbound':
        yield db.cards.update(
            {'_id': 'id-old-card'}, {'$set': {'unbound': True}}
        )
    order_id = 'f27d3d9263eb4e1ba65b584b9379cd5c'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc)
    status_handling._handle_preupdate_order_change_payment(state)

    method_info = proc._preupdate_order_data.payment_method_info
    assert method_info[0]['tag'] == 'payment_method_info'
    assert method_info[0]['data'].payment_id == 'card-new-card'


@pytest.mark.parametrize('order_id', [
    'b63cbecd55be19118e9eac43d455044b',
    '0819953dab7063d0b46b15d9295bcf8f',
])
@pytest.mark.filldb(
    orders='afs',
    order_proc='afs',
)
@pytest.mark.config(AFS_ORDER_FINISH_POST_EVENT_ENABLED=False)
@pytest.inline_callbacks
def test_handle_post_finish_afs_off(areq_request, order_id):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert False

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    state = order_fsm.OrderFsm(proc)
    status_handling._handle_post_finish(state)

    assert requests_request.calls == []


@pytest.mark.parametrize('order_id,fail,expected_result', [
    (
        'b63cbecd55be19118e9eac43d455044b',
        False,
        {
            'calc': {
                'dist': 15300.189468502998,
                'time': 2084.991586796098
            },
            'zone': 'moscow',
            'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
            'fixed_price': {
                'destination': [
                    37.59495899698706,
                    55.73779738195956
                ],
                'driver_price': 609.0,
                'price': 609.0,
                'price_original': 609.0
            },
            'order_id': 'b63cbecd55be19118e9eac43d455044b',
            'request': {
                'class': 'business',
                'destinations': [
                    {
                        'geopoint': [
                            37.59495899698706,
                            55.73779738195956
                        ]
                    }
                ],
                'due': '2018-11-20T10:54:00+0300',
                'extra_user_phone_id': '5c0e2616030553e658070fe8',
                'source': {
                    'locality': 'Moscow',
                },
                'payment': {
                    'type': 'googlepay',
                },
            },
            'city': u'Москва',
            'statistics': {
                'cancel_distance': 104.57167864797431,
                'cancel_dt': '2018-11-20T10:50:21+0300',
                'cancel_time': 48.265
            },
            'status': 'cancelled',
            'status_updates': [
                {
                    'created': '2018-11-20T10:49:33+0300',
                    'reason_code': 'create',
                    'status': 'pending'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:10+0300',
                    'reason_code': 'seen'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'lookup_generation': 1,
                    'status': 'assigned'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-20T10:50:11+0300',
                    'taxi_status': 'driving'
                },
                {
                    'created': '2018-11-20T10:50:21+0300',
                    'status': 'cancelled'
                }
            ],
            'payment_tech': {
                'type': 'cash',
            },
            'feedback': {

            },
            'taxi_status': 'driving',
            'user_id': '564d49a5d252b097f94eacea37353f4f',
            'user_phone_id': '5bcd7548030553e658298f6c',
            'multiorder_order_number': 0,
            'performer': {
                'clid': '643753730233',
                'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                'uuid': '63f7bce3d3dd4a96a6392c7bc00041f8',
            },
        },
    ),
    (
        '0819953dab7063d0b46b15d9295bcf8f',
        False,
        {
            'calc': {
                'dist': 46073.39288640022,
                'time': 6733.002616620512
            },
            'cost': 1634.0,
            'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
            'fixed_price': {
                'destination': [
                    37.56414175768225,
                    55.72468390881436
                ],
                'driver_price': 1634.0,
                'price': 1634.0,
                'price_original': 1634.0
            },
            'zone': 'moscow',
            'city': u'Масква',
            'order_id': '0819953dab7063d0b46b15d9295bcf8f',
            'request': {
                'destinations': [
                    {
                        'geopoint': [
                            37.57380003148046,
                            55.79313088487496
                        ]
                    },
                    {
                        'geopoint': [
                            37.70467300058783,
                            55.76339138789917
                        ]
                    },
                    {
                        'geopoint': [
                            37.56414175768225,
                            55.72468390881436
                        ]
                    }
                ],
                'due': '2018-11-22T10:44:00+0300',
                'requirements': {
                    'animaltransport': True,
                },
                'class': 'multiclass',
                'comment': 'speed - 600; wait - 2;',
                'source': {},
                'payment': {
                    'type': 'googlepay',
                },
            },
            'statistics': {
                'complete_time': '2018-11-22T10:40:59+0300',
                'driver_delay': 0,
                'start_transporting_time': '2018-11-22T10:39:39+0300',
                'start_waiting_time': '2018-11-22T10:39:36+0300',
                'travel_time': 80.0
            },
            'status': 'finished',
            'status_updates': [
                {
                    'created': '2018-11-22T10:39:16+0300',
                    'reason_code': 'create',
                    'status': 'pending'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-22T10:39:34+0300',
                    'reason_code': 'seen'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-22T10:39:34+0300',
                    'lookup_generation': 1,
                    'status': 'assigned'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-22T10:39:34+0300',
                    'taxi_status': 'driving'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-22T10:39:36+0300',
                    'taxi_status': 'waiting'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-22T10:39:39+0300',
                    'taxi_status': 'transporting'
                },
                {
                    'candidate_index': 1,
                    'created': '2018-11-22T10:40:59+0300',
                    'status': 'finished',
                    'taxi_status': 'complete'
                }
            ],
            'payment_tech': {
                'type': 'cash',
            },
            'feedback': {
                'comment': 'post msg',
            },
            'taxi_status': 'complete',
            'user_id': '8c1e0c51fefcfb21eab6b2f36e532e2d',
            'user_phone_id': '5bcd7548030553e658298f6c',
            'performer': {
                'clid': '643753730233',
                'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                'uuid': '0086d777de0d4c35a50a3bfce71c8d52',
            },
        },
    ),
    (
        'b63cbecd55be19118e9eac43d455044b',
        True,
        {},
    ),
    (
        '0819953dab7063d0b46b15d9295bcf8f',
        True,
        {},
    ),
])
@pytest.mark.filldb(
    orders='afs',
    order_proc='afs',
)
@pytest.mark.config(AFS_ORDER_FINISH_POST_EVENT_ENABLED=True)
@pytest.inline_callbacks
def test_handle_post_finish_afs_on(areq_request, order_id, fail,
                                   expected_result):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == (
            'http://antifraud.taxi.dev.yandex.net/events/order_finish_post')
        if not fail:
            assert kwargs['json'] == expected_result
            return areq_request.response(200, '{}')
        else:
            return areq_request.response(500)

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)

    state = order_fsm.OrderFsm(proc)
    status_handling._handle_post_finish(state)

    assert len(requests_request.calls) == 1


@pytest.mark.filldb(orders='switch_to_cash', order_proc='switch_to_cash')
@pytest.mark.parametrize(
    'antifraud_finished, status, update', [
        (None, None, False),
        (True, 'assigned', True),
        (False, 'finished', True),
    ]
)
@pytest.mark.config(BILLING_DEBT_FALLBACK_ENABLED=False)
@pytest.inline_callbacks
@pytest.mark.parametrize('order_object_created', [True, False])
def test_handle_preupdate_proc_related_switched_to_cash(
        antifraud_finished, status, update, patch, order_object_created):
    @patch('taxi.internal.order_kit.antifraud.stop_procedure_and_move_to_cash')
    @async.inline_callbacks
    def stop_procedure_and_move_to_cash(order_doc, extra_request=None, log_extra=None):
        raise exceptions.RaceConditionError

    order_id = 'order_id'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    if not order_object_created:
        proc.order_info.order_object_skipped = True

    state = order_fsm.OrderFsm(proc)
    if not order_object_created:
        db.orders.remove({'_id': 'order_id'})
        yield status_handling.\
            _handle_preupdate_proc_related_switched_to_cash(state)
    elif not update:
        with pytest.raises(exceptions.RaceConditionError):
            yield status_handling.\
                _handle_preupdate_proc_related_switched_to_cash(state)
    else:
        Order = dbh.orders.Doc

        yield db.orders.update({'_id': 'order_id'}, {'$set': {
            Order.payment_tech.antifraud_finished: antifraud_finished,
            Order.status: status,
        }})
        try:
            yield status_handling.\
                _handle_preupdate_proc_related_switched_to_cash(state)
        except BaseException:
            pytest.fail('Unexpected exception')


@pytest.mark.parametrize(
    'do_commit, cp',
    [
        (True, None),
        (
            False,
            dbh.orders.CurrentPrices(
                user_total_price=475.0,
                user_total_display_price=475.0,
                user_ride_display_price=475.0,
                cashback_price=0.0,
                charity_price=0.0,
                kind=u'taximeter'
            )
        )
    ]
)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_ENABLED_PY2=True)
@pytest.mark.filldb(order_proc='moved_to_cash')
@pytest.inline_callbacks
def test_handle_preupdate_proc_moved_to_cash(patch, do_commit, cp):
    order_id = 'order_id_1'

    @patch('taxi_stq._client.put')
    @pytest.inline_callbacks
    def _mock_put(queue, eta=None, task_id=None, args=None, kwargs=None):
        assert queue == 'current_prices_calculator'
        assert args == (order_id,)
        assert task_id == order_id
        yield

    yield config.CURRENT_PRICES_CALCULATOR_DO_COMMIT.save(do_commit)
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc)
    yield status_handling._handle_preupdate_proc_moved_to_cash(state)
    assert len(_mock_put.calls) == 1
    assert state.proc.preupdated_order_data.current_prices == cp


@pytest.mark.filldb(orders='afs', order_proc='afs',
                    tariff_settings='for_get_custom_rebate_test')
@pytest.mark.parametrize(
    'countries,should_fetch_expected', [
        ([], False),
        (['rus'], True),
    ]
)
@pytest.inline_callbacks
def test_should_fetch_receipt(countries, should_fetch_expected):
    order_id = 'b63cbecd55be19118e9eac43d455044b'

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc)
    yield config.ORDERS_HISTORY_SHOW_FETCHED_RECEIPT_IN_COUNTRIES.save(
        countries)
    tariff_settings = yield dbh.tariff_settings.Doc.find_by_home_zone(
        state.proc.order.nearest_zone
    )
    should_fetch_actual = yield status_handling._should_fetch_receipt(
        state, tariff_settings
    )
    assert should_fetch_actual == should_fetch_expected


@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.parametrize(
    'legacy_mode,order_id,expected_stq_put',
    [
        (
            True,
            'order_1',
            None,
        ),
        (
            True,
            'order_9',
            {
                'queue': 'zendesk_dispatcher_price',
                'task_id': 'order_9',
                'eta': datetime.datetime(2019, 1, 1, 0, 1, 30),
                'args': ('order_9',),
                'kwargs': {},
            },
        ),
        (
            False,
            'order_9',
            {
                'queue': 'support_info_change_price',
                'task_id': 'order_9',
                'eta': datetime.datetime(2019, 1, 1, 0, 1, 30),
                'args': ('order_9',),
                'kwargs': {},
            },
        ),
    ],
)
@pytest.inline_callbacks
def test_process_dispatcher_price(patch, legacy_mode, order_id,
                                  expected_stq_put):
    yield config.CHANGE_PRICE_LEGACY_MODE.save(legacy_mode)

    @patch('taxi_stq._client.put')
    @pytest.inline_callbacks
    def _dummy_put(queue, eta=None, task_id=None, args=None, kwargs=None):
        yield

    class _DummyState:
        def __init__(self):
            self.order_id = order_id

    yield status_handling._process_dispatcher_price(_DummyState())
    stq_put_calls = _dummy_put.calls
    if expected_stq_put is None:
        assert not stq_put_calls
    else:
        del stq_put_calls[0]['kwargs']['log_extra']
        assert stq_put_calls[0] == expected_stq_put


@pytest.mark.parametrize('order_id, cash_friendly', [
    ('order_cashfirendly', True),
    ('order_justcard', False),
])
@pytest.mark.filldb(
    order_proc='change_payment_success',
    promocode_series='change_payment_success'
)
@pytest.inline_callbacks
def test_handle_preupdate_proc_change_payment_success(order_id, cash_friendly):

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc)

    yield status_handling._handle_preupdate_proc_change_payment_success(state)
    yield status_handling.handle_new_status(state.proc, 0)
    (update, query) = yield state.proc.mark_as_sync(event_index=0)

    if cash_friendly:
        assert not state.proc._preupdate_order_data.unmark_coupon_used
        assert update['$set'].get('order.coupon.was_used') is None
    else:
        assert state.proc._preupdate_order_data.unmark_coupon_used
        assert update['$set'].get('order.coupon.was_used') is False


@pytest.mark.filldb(
    order_proc='change_payment_success',
)
@pytest.inline_callbacks
def test_handle_change_payment_success_discard_event():

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_discard_event')
    state = order_fsm.OrderFsm(proc)

    # check that there won't be failure:
    # 'NoneType' object has no attribute 'reason_code'
    yield status_handling._handle_change_payment_success(state)
    yield status_handling.handle_new_status(state.proc, 0)
    yield state.proc.mark_as_sync(event_index=0)


@pytest.mark.parametrize(
    'start_payment_type,status_updates_id,do_notify',
    [
        ('cash', 'to_card', True),
        ('card', 'moved_to_cash_switch_to_card', True),
        ('card', 'related_moved_to_cash_switch_to_card', True),
        ('cash', 'to_card_with_extra_events', True),
        ('cash', 'double_switch_to_card', False),
        ('card', 'to_card', False),
        ('card', 'moved_to_cash_finished_to_card', False),
    ],
)
@pytest.mark.filldb(order_proc='change_payment_success_notify')
@pytest.inline_callbacks
def test_handle_change_payment_success_notify(
        patch,
        load,
        mock_taximeter_notify,
        start_payment_type,
        status_updates_id,
        do_notify,
):
    status_updates_objects = json.loads(
        load('status_updates_for_change_payment_success.json'),
    )
    status_updates = status_updates_objects[status_updates_id]
    yield db.order_proc.update(
        {'_id': 'order_id'},
        {
            '$set': {
                'order.request.payment.type': start_payment_type,
                'order_info.statistics.status_updates': status_updates,
            },
        },
    )

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)
    state.event_index = len(status_updates) - 1
    yield status_handling._handle_change_payment_success(state)

    if do_notify:
        assert mock_taximeter_notify.notify_count == 1
        assert mock_taximeter_notify.last_payment_type == 'card'
    else:
        assert mock_taximeter_notify.notify_count == 0


@pytest.mark.filldb(order_proc='autoreorder')
@pytest.inline_callbacks
@pytest.mark.parametrize('order_id, expected_event_properties', [
    ('order_with_autoreorder', []),
    ('order_with_autoreorder_eta_autoreorder', ['eta_autoreorder']),
])
def test_handle_autoreorder_send_dm_event(patch, order_id, expected_event_properties):
    @patch('taxi_stq.client.driver_metrics_client')
    def driver_metrics_client_task(*args, **kwargs):
        return

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc=proc)
    yield status_handling._handle_autoreordering(state)

    calls = driver_metrics_client_task.calls
    assert len(calls) == 1
    assert calls[0]['kwargs']['event'] == {
        'driver_id': 'clid_driver_id',
        'candidate_index': 0,
        'tariff_class': u'econom',
        'license': {},
        'update_index': -1,
        'order_id': order_id,
        'timestamp': '{}',
        'reason_code': u'autoreorder',
        'taxi_status': None,
        'distance_to_a': {},
        'time_to_a': {},
        'udid': None,
        'reason': u'manual',
        'handler': 'auto_reorder',
        'dp_values': {},
        'payment_type': None,
        'v': 2,
        'zone': {},
        'properties': expected_event_properties
    }


@pytest.mark.filldb(order_proc='change_payment')
@pytest.inline_callbacks
@pytest.mark.parametrize('order_id, intent_enable, expected_args, expected_kwargs', [
    ('order_debt',
     True,
     ('order_debt',),
     {'intent': invoice_handler.INTENT_DEBT, 'log_extra': None}
    ),
    ('order_change_payment',
     True,
     ('order_change_payment',),
     {'intent': invoice_handler.INTENT_CHANGE_PAYMENT, 'log_extra': None},
    ),
    ('order_debt',
     False,
     ('order_debt',),
     {'log_extra': None}
    ),
])
def test_handle_change_payment(patch, order_id, intent_enable, expected_args, expected_kwargs):
    @patch('taxi_stq._client.put')
    @async.inline_callbacks
    def put(queue, eta=None, task_id=None, args=None, kwargs=None,
            src_tvm_service=None):
        assert args == expected_args
        assert kwargs == expected_kwargs
        yield

    yield config.TRANSACTIONS_ENABLE_INTENT.save(intent_enable)

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    state = order_fsm.OrderFsm(proc)

    yield status_handling._handle_change_payment(state)
    assert len(put.calls) == 1


@pytest.mark.filldb(order_proc='ride_report')
@pytest.inline_callbacks
def test_handle_sent_ride_report(patch):
    @patch('taxi.internal.order_kit.plg.status_handling._ride_report')
    @async.inline_callbacks
    def _ride_report(order_id, log_extra=None):
        yield

    @patch('taxi.internal.promotions_manager.on_order_complete')
    @async.inline_callbacks
    def on_order_complete(proc, log_extra=None):
        yield

    @patch('taxi.internal.notifications.order.notify_on_complete')
    @async.inline_callbacks
    def notify_on_complete(proc, log_extra=None, tvm_src_service=None):
        yield

    @patch('taxi.internal.order_kit.plg.status_handling._process_dispatcher_price')
    @async.inline_callbacks
    def process_dispatcher_price(state, log_extra=None):
        yield

    @patch('taxi.internal.drivers_ratings.rates.send_order_event_to_dm')
    @async.inline_callbacks
    def send_order_event_to_dm(event, state, log_extra=None):
        yield

    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='new_ride_report_processing',
                value={'enabled': False},
            )
        ]
        async.return_value(result)

    proc = yield dbh.order_proc.Doc.find_one_by_id('order_id')
    state = order_fsm.OrderFsm(proc)
    yield status_handling._handle_complete(state)
    assert len(_ride_report.calls) == 1
