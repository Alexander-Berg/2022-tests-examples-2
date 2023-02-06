import bson
import collections
import copy
import datetime
import json

from django import test as django_test
from django.core import urlresolvers
import freezegun
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import commission_manager
from taxi.internal import dbh
from taxi.internal.order_kit import payment_helpers
from taxi.util import decimal
from taxiadmin.api.views import commissions


_MISSING = object()
_END_OF_TIME = datetime.datetime(2999, 12, 31, 21)

_DEFAULT_BRANDING_DISCOUNTS = [
    {
        'marketing_level': [
            'lightbox',
            'co_branding',
            'sticker'
        ],
        'value': '0.05'
    }
]


ContractData = collections.namedtuple(
    'ContractData', [
        'id',
        'has_commission',
        'type',
        'begin',
        'end',
        'payment_type',
        'min_order_cost',
        'max_order_cost',
        'expired_cost',
        'expired_percent',
        'has_fixed_cancel_percent',
        'cancel_percent',
        'vat',
        'taximeter_payment',
        'callcenter_commission_percent',
        'acquiring_percent',
        'agent_percent',
        'branding_discounts',
        'percent',
        'data',
        'tag',
    ]
)


def _make_add_or_edit_request_data(
        id=_MISSING,
        type='fixed_percent',
        begin=datetime.datetime(2016, 10, 30, 19, 23),
        payment_type='card',
        min_order_cost='1',
        max_order_cost='6000',
        expired_cost='800',
        expired_percent='0.11',
        has_fixed_cancel_percent=True,
        cancel_percent='0.09',
        vat='1.18',
        taximeter_payment='2',
        callcenter_commission_percent='0.0000',
        acquiring_percent='0.02',
        agent_percent='0.0001',
        branding_discounts=None,
        end=_MISSING,
        percent=_MISSING,
        cost_norm=_MISSING,
        numerator=_MISSING,
        asymp=_MISSING,
        max_commission_percent=_MISSING,
        commission=_MISSING,
        cancel_commission=_MISSING,
        expired_commission=_MISSING,
        tariff_class=_MISSING,
        pattern_id='5cc09f28efb903fd53a793ab',
        tag='',
):
    if branding_discounts is None:
        branding_discounts = _DEFAULT_BRANDING_DISCOUNTS
    request_data = {
        'type': type,
        'begin': _format_datetime(begin),
        'payment_type': payment_type,
        'min_order_cost': min_order_cost,
        'max_order_cost': max_order_cost,
        'vat': vat,
        'taximeter_payment': taximeter_payment,
        'callcenter_commission_percent': callcenter_commission_percent,
        'acquiring_percent': acquiring_percent,
        'agent_percent': agent_percent,
        'ticket': 'TAXIRATE-1',
    }
    _maybe_add_end(request_data, end)
    keys_and_values = [
        ('id', id),
        ('percent', percent),
        ('cancel_percent', cancel_percent),
        ('expired_percent', expired_percent),
        ('expired_cost', expired_cost),
        ('has_fixed_cancel_percent', has_fixed_cancel_percent),
        ('cost_norm', cost_norm),
        ('numerator', numerator),
        ('asymp', asymp),
        ('max_commission_percent', max_commission_percent),
        ('commission', commission),
        ('cancel_commission', cancel_commission),
        ('expired_commission', expired_commission),
        ('branding_discounts', branding_discounts),
        ('tariff_class', tariff_class),
        ('pattern_id', pattern_id),
        ('tag', tag),
    ]
    for key, value in keys_and_values:
        if value is not _MISSING:
            request_data[key] = value
    return request_data


def _maybe_add_end(request_data, end):
    if end is not _MISSING:
        if end is None:
            request_data['end'] = end
        else:
            request_data['end'] = _format_datetime(end)


def _format_datetime(d_time):
    return d_time.strftime('%Y-%m-%dT%H:%M:%S')


_FIXED_PERCENT_DATA = ContractData(
    id=None,
    has_commission=True,
    type='fixed_percent',
    begin=datetime.datetime(2016, 10, 30, 16, 23),
    end=datetime.datetime(2016, 12, 30, 21),
    payment_type='card',
    min_order_cost='1',
    max_order_cost='6000',
    expired_cost='800',
    expired_percent='0.11',
    has_fixed_cancel_percent=True,
    cancel_percent='0.09',
    vat='1.18',
    taximeter_payment='0.08',
    callcenter_commission_percent='0.0000',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    branding_discounts=_DEFAULT_BRANDING_DISCOUNTS,
    percent='0.03',
    data={},
    tag=None,
)
_FIXED_PERCENT_REQUEST_KWARGS = dict(
    type='fixed_percent',
    end=datetime.datetime(2016, 12, 31),
    percent='0.03',
    taximeter_payment='0.08',
)
_SAME_FIXED_PERCENT_REQUEST_KWARGS = dict(
    type='fixed_percent',
    # naive moscow local time
    begin=datetime.datetime(2017, 1, 1),
    end=datetime.datetime(2019, 1, 1),
    payment_type='cash',
    branding_discounts=[],
    has_fixed_cancel_percent=False,
    min_order_cost='0',
    max_order_cost='6000',
    percent='0.11',
    expired_cost='800',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    cancel_percent='0.11',
    expired_percent='0.11',
    vat='1.18',
    taximeter_payment='1',
    callcenter_commission_percent='0',
)
_SAME_FIXED_PERCENT_DATA = ContractData(
    id=None,
    has_commission=True,
    type='fixed_percent',
    payment_type='cash',
    begin=datetime.datetime(2016, 12, 31, 21),
    end=datetime.datetime(2018, 12, 31, 21),
    branding_discounts=[],
    has_fixed_cancel_percent=False,
    min_order_cost='0',
    max_order_cost='6000',
    percent='0.11',
    expired_cost='800',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    cancel_percent='0.11',
    expired_percent='0.11',
    vat='1.18',
    callcenter_commission_percent='0.0000',
    taximeter_payment='1',
    data={},
    tag=None,
)

_ALMOST_SAME_FIXED_PERCENT_REQUEST_KWARGS = copy.deepcopy(
    _SAME_FIXED_PERCENT_REQUEST_KWARGS
)
_ALMOST_SAME_FIXED_PERCENT_REQUEST_KWARGS['vat'] = '1.17'

_ASYMPTOTIC_FORMULA_DATA = ContractData(
    id=None,
    has_commission=True,
    type='asymptotic_formula',
    begin=datetime.datetime(2016, 10, 30, 16, 23),
    end=datetime.datetime(2016, 12, 30, 21),
    payment_type='card',
    min_order_cost='1',
    max_order_cost='6000',
    expired_cost='800',
    expired_percent='0.11',
    has_fixed_cancel_percent=True,
    cancel_percent='0.09',
    vat='1.18',
    callcenter_commission_percent='0.0000',
    taximeter_payment='1',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    branding_discounts=_DEFAULT_BRANDING_DISCOUNTS,
    percent='0',
    data={
        'cost_norm': '-39.399',
        'numerator': '853.8',
        'asymp': '16.2',
        'max_commission_percent': '0.163',
    },
    tag=None,
)
_ASYMPTOTIC_FORMULA_REQUEST_KWARGS = dict(
    type='asymptotic_formula',
    end=datetime.datetime(2016, 12, 31),
    cost_norm='-39.399',
    numerator='853.8',
    asymp='16.2',
    max_commission_percent='0.163',
    taximeter_payment='1',
)
_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS = copy.deepcopy(
    _SAME_FIXED_PERCENT_REQUEST_KWARGS
)
del _SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS['percent']
_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS.update(
    dict(
        type='asymptotic_formula',
        cost_norm='-39.399',
        numerator='853.8',
        asymp='16.2',
        max_commission_percent='0.163',
        branding_discounts=_DEFAULT_BRANDING_DISCOUNTS,
    )
)
_SAME_ASYMPTOTIC_FORMULA_DATA = ContractData(
    id=None,
    has_commission=True,
    type='asymptotic_formula',
    payment_type='cash',
    begin=datetime.datetime(2016, 12, 31, 21),
    end=datetime.datetime(2018, 12, 31, 21),
    branding_discounts=_DEFAULT_BRANDING_DISCOUNTS,
    has_fixed_cancel_percent=False,
    min_order_cost='0',
    max_order_cost='6000',
    percent='0',
    expired_cost='800',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    cancel_percent='0.11',
    expired_percent='0.11',
    vat='1.18',
    callcenter_commission_percent='0.0000',
    taximeter_payment='1',
    data={
        'cost_norm': '-39.399',
        'numerator': '853.8',
        'asymp': '16.2',
        'max_commission_percent': '0.163',
    },
    tag=None,
)

_ALMOST_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS = copy.deepcopy(
    _SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS,
)
_ALMOST_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS['asymp'] = '16.1'

_ANOTHER_ALMOST_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS = copy.deepcopy(
    _SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS
)
_ANOTHER_ALMOST_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS['branding_discounts'][0]['marketing_level'].append('whatever')


_ABSOLUTE_VALUE_DATA = ContractData(
    id=None,
    has_commission=True,
    type='absolute_value',
    begin=datetime.datetime(2016, 10, 30, 16, 23),
    end=datetime.datetime(2016, 12, 30, 21),
    payment_type='card',
    min_order_cost='1',
    max_order_cost='6000',
    expired_cost='0',
    expired_percent='0',
    has_fixed_cancel_percent=True,
    cancel_percent='0',
    vat='1.18',
    callcenter_commission_percent='0.0000',
    taximeter_payment='0',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    branding_discounts=[],
    percent='0',
    data={
        'commission': '300',
        'cancel_commission': '200',
        'expired_commission': '100',
    },
    tag=None,
)
_ABSOLUTE_VALUE_REQUEST_KWARGS = dict(
    type='absolute_value',
    expired_cost=_MISSING,
    cancel_percent=_MISSING,
    has_fixed_cancel_percent=_MISSING,
    expired_percent=_MISSING,
    end=datetime.datetime(2016, 12, 31),
    commission='300',
    cancel_commission='200',
    expired_commission='100',
    taximeter_payment='0',
    branding_discounts=_MISSING,
)
_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS = copy.deepcopy(
    _SAME_FIXED_PERCENT_REQUEST_KWARGS
)
del _SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['percent']
del _SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['cancel_percent']
del _SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['expired_percent']
del _SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['expired_cost']
_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['taximeter_payment'] = '0'
_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['branding_discounts'] = _MISSING
del _SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['has_fixed_cancel_percent']
_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS.update(
    dict(
        type='absolute_value',
        commission='300',
        cancel_commission='200',
        expired_commission='100',
        branding_discounts=[],
    )
)
_SAME_ABSOLUTE_VALUE_DATA = ContractData(
    id=None,
    has_commission=True,
    type='absolute_value',
    payment_type='cash',
    begin=datetime.datetime(2016, 12, 31, 21),
    end=datetime.datetime(2018, 12, 31, 21),
    branding_discounts=[],
    has_fixed_cancel_percent=True,
    min_order_cost='0',
    max_order_cost='6000',
    percent='0',
    expired_cost='00',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    cancel_percent='0',
    expired_percent='0',
    vat='1.18',
    callcenter_commission_percent='0.0000',
    taximeter_payment='0',
    data={
        'commission': '300',
        'cancel_commission': '200',
        'expired_commission': '100',
    },
    tag=None,
)

_ALMOST_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS = copy.deepcopy(
    _SAME_ABSOLUTE_VALUE_REQUEST_KWARGS,
)
_ALMOST_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS['commission'] = '301'

_SMART_EDIT_REQUEST_KWARGS = dict(
    id='id_for_smart_edit',
    type='fixed_percent',
    payment_type='cash',
    branding_discounts=[],
    has_fixed_cancel_percent=False,
    min_order_cost='0',
    max_order_cost='6000',
    percent='0.11',
    expired_cost='800',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    cancel_percent='0.11',
    expired_percent='0.11',
    vat='1.18',
    taximeter_payment='1',
)

_TAG_CREATE_DATA = ContractData(
    id=None,
    has_commission=True,
    type='fixed_percent',
    begin=datetime.datetime(2016, 10, 30, 16, 23),
    end=datetime.datetime(2016, 12, 30, 21, 0),
    payment_type='card',
    min_order_cost='1',
    max_order_cost='6000',
    expired_cost='800',
    expired_percent='0.11',
    has_fixed_cancel_percent=True,
    cancel_percent='0.09',
    vat='1.18',
    taximeter_payment='0.08',
    callcenter_commission_percent='0.0000',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    branding_discounts=_DEFAULT_BRANDING_DISCOUNTS,
    percent='0.03',
    data={},
    tag='great_tag',
)

_TAG_CREATE_REQUEST_KWARGS = dict(
    id='great_tag_id',
    type='fixed_percent',
    end=datetime.datetime(2016, 12, 31),
    percent='0.03',
    taximeter_payment='0.08',
    tag='great_tag',
)

_TAG_EDIT_DATA = ContractData(
    id=None,
    has_commission=True,
    type='fixed_percent',
    begin=datetime.datetime(2016, 10, 30, 16, 23),
    end=datetime.datetime(2016, 12, 30, 21),
    payment_type='card',
    min_order_cost='1',
    max_order_cost='6000',
    expired_cost='800',
    expired_percent='0.11',
    has_fixed_cancel_percent=True,
    cancel_percent='0.09',
    vat='1.18',
    taximeter_payment='0.08',
    callcenter_commission_percent='0.0000',
    acquiring_percent='0.02',
    agent_percent='0.0001',
    branding_discounts=_DEFAULT_BRANDING_DISCOUNTS,
    percent='0.03',
    data={},
    tag='new_great_tag',
)

_TAG_EDIT_REQUEST_KWARGS = dict(
    type='fixed_percent',
    end=datetime.datetime(2016, 12, 31),
    percent='0.03',
    taximeter_payment='0.08',
    tag='new_great_tag',
)


@pytest.mark.filldb(
    commission_contracts='for_commissions_add_or_edit_test',
)
@pytest.mark.config(
    USE_COMMISSIONS_PATTERNS=True
)
@pytest.mark.parametrize(
    'utcnow,zone,method,data,expected_contract,num_added_contracts', [
        (
            datetime.datetime(2016, 10, 7),
            'moscow',
            'add',
            _make_add_or_edit_request_data(**_FIXED_PERCENT_REQUEST_KWARGS),
            _FIXED_PERCENT_DATA,
            1
        ),
        (
            datetime.datetime(2016, 10, 7),
            'moscow',
            'edit',
            _make_add_or_edit_request_data(
                id='some_fixed_percent_commission_contract_id',
                **_FIXED_PERCENT_REQUEST_KWARGS
            ),
            _FIXED_PERCENT_DATA._replace(
                id='some_fixed_percent_commission_contract_id',
            ),
            0,
        ),
        (
            # edit of active
            datetime.datetime(2017, 10, 7),
            'moscow',
            'edit',
            _make_add_or_edit_request_data(
                id='some_fixed_percent_commission_contract_id',
                **_SAME_FIXED_PERCENT_REQUEST_KWARGS
            ),
            _SAME_FIXED_PERCENT_DATA._replace(
                id='some_fixed_percent_commission_contract_id',
            ),
            0,
        ),
        (
            datetime.datetime(2016, 10, 7),
            'spb',
            'add',
            _make_add_or_edit_request_data(
                **_ASYMPTOTIC_FORMULA_REQUEST_KWARGS
            ),
            _ASYMPTOTIC_FORMULA_DATA,
            1,
        ),
        (
            datetime.datetime(2016, 10, 7),
            'spb',
            'edit',
            _make_add_or_edit_request_data(
                id='some_asymptotic_formula_commission_contract_id',
                **_ASYMPTOTIC_FORMULA_REQUEST_KWARGS
            ),
            _ASYMPTOTIC_FORMULA_DATA._replace(
                id='some_asymptotic_formula_commission_contract_id',
            ),
            0,
        ),
        (
            # edit of active
            datetime.datetime(2017, 10, 7),
            'spb',
            'edit',
            _make_add_or_edit_request_data(
                id='some_asymptotic_formula_commission_contract_id',
                **_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS
            ),
            _SAME_ASYMPTOTIC_FORMULA_DATA._replace(
                id='some_asymptotic_formula_commission_contract_id',
            ),
            0,
        ),
        (
            datetime.datetime(2016, 10, 7),
            'voronezh',
            'add',
            _make_add_or_edit_request_data(
                **_ABSOLUTE_VALUE_REQUEST_KWARGS
            ),
            _ABSOLUTE_VALUE_DATA,
            1,
        ),
        (
            datetime.datetime(2016, 10, 7),
            'voronezh',
            'edit',
            _make_add_or_edit_request_data(
                id='some_absolute_value_commission_contract_id',
                **_ABSOLUTE_VALUE_REQUEST_KWARGS
            ),
            _ABSOLUTE_VALUE_DATA._replace(
                id='some_absolute_value_commission_contract_id',
            ),
            0,
        ),
        (
            # edit of active
            datetime.datetime(2017, 10, 7),
            'voronezh',
            'edit',
            _make_add_or_edit_request_data(
                id='some_absolute_value_commission_contract_id',
                **_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS
            ),
            _SAME_ABSOLUTE_VALUE_DATA._replace(
                id='some_absolute_value_commission_contract_id',
            ),
            0,
        ),
        (
            # test tag
            datetime.datetime(2016, 10, 7),
            'moscow',
            'add',
            _make_add_or_edit_request_data(**_TAG_CREATE_REQUEST_KWARGS),
            _TAG_CREATE_DATA,
            1,
        ),
        (
            # test tag
            datetime.datetime(2016, 10, 7),
            'moscow',
            'edit',
            _make_add_or_edit_request_data(
                id='some_fixed_percent_commission_contract_id',
                **_TAG_EDIT_REQUEST_KWARGS
            ),
            _TAG_EDIT_DATA._replace(
                id='some_fixed_percent_commission_contract_id'
            ),
            0,
        ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_commissions_add_or_edit(
        utcnow, zone, method, data, expected_contract, num_added_contracts,
        patch
):
    @patch('taxi.external.tags_service.check_tag')
    @pytest.inline_callbacks
    def check_tag(topic, tag_contains, src_service, tags_service, log_extra):
        async.return_value(None)

    num_contracts_before = yield _get_num_contracts()
    with freezegun.freeze_time(utcnow, ignore=['']):
        response = _do_add_or_edit_request(
            zone=zone,
            method=method,
            data=data,
        )
    num_contracts_after = yield _get_num_contracts()
    assert (num_contracts_after - num_contracts_before) == num_added_contracts
    json_response = json.loads(response.content)
    yield check_response(json_response, expected_contract)


@pytest.inline_callbacks
def check_response(json_response, expected_contract):
    if expected_contract.id is None:
        if bson.ObjectId.is_valid(json_response['id']):
            contract_id = bson.ObjectId(json_response['id'])
        else:
            contract_id = json_response['id']
    else:
        contract_id = expected_contract.id
    contract = yield dbh.commission_contracts.Doc.find_one_by_id(contract_id)

    assert contract.begin == expected_contract.begin
    assert contract.end == expected_contract.end
    conditions = contract.conditions
    assert conditions.payment_type == expected_contract.payment_type
    assert conditions.get('tag') == expected_contract.tag
    commission = contract.commission
    assert commission.has_commission == expected_contract.has_commission
    assert commission.type == expected_contract.type
    assert_inner_decimal_equal(
        commission.min_order_cost,
        expected_contract.min_order_cost,
    )
    assert_inner_decimal_equal(
        commission.max_order_cost,
        expected_contract.max_order_cost,
    )
    assert_inner_decimal_equal(
        commission.expired_cost,
        expected_contract.expired_cost,
    )
    assert_inner_decimal_equal(
        commission.expired_percent,
        expected_contract.expired_percent,
    )
    assert (commission.has_fixed_cancel_percent
            is expected_contract.has_fixed_cancel_percent)
    assert_inner_decimal_equal(
        commission.cancel_percent,
        expected_contract.cancel_percent,
    )
    assert_inner_decimal_equal(
        commission.vat,
        expected_contract.vat,
    )
    assert_inner_decimal_equal(
        commission.taximeter_payment,
        expected_contract.taximeter_payment,
    )
    assert_inner_decimal_equal(
        commission.acquiring_percent,
        expected_contract.acquiring_percent,
    )
    assert_inner_decimal_equal(
        commission.agent_percent,
        expected_contract.agent_percent,
    )
    assert_branding_discounts_equal(
        commission.branding_discounts,
        expected_contract.branding_discounts,
    )
    assert_inner_decimal_equal(
        commission.percent,
        expected_contract.percent,
    )
    if not expected_contract.data:
        assert commission.data == {}
    elif expected_contract.type == commission_manager.ASYMPTOTIC_FORMULA_TYPE:
        assert_asymptotic_data_equal(commission.data, expected_contract.data)
    elif expected_contract.type == commission_manager.ABSOLUTE_VALUE_TYPE:
        assert_absolute_data_equal(commission.data, expected_contract.data)
    else:
        raise ValueError('bad type: {}'.format(expected_contract.type))


@pytest.mark.now('2016-10-07T00:00:00')
@pytest.mark.filldb()
@pytest.mark.parametrize('zone,data,expected_end', [
    (
        'moscow',
        # end is missing - _END_OF_TIME by default
        _make_add_or_edit_request_data(
            type='fixed_percent',
            percent='0.03',
        ),
        _END_OF_TIME,
    ),
    (
        'moscow',
        # end is None - _END_OF_TIME by default
        _make_add_or_edit_request_data(
            type='fixed_percent',
            percent='0.03',
            end=None,
        ),
        _END_OF_TIME,
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_commissions_add_end(zone, data, expected_end):
    _do_add_or_edit_request(
        zone=zone,
        method='add',
        data=data,
    )
    contract = yield _get_single_contract()
    assert contract.end == expected_end


@pytest.mark.filldb(
    commission_contracts='for_commissions_smart_add_or_edit_test',
)
@pytest.mark.parametrize(
    'utcnow,method,data,expected_status_code,'
    'expected_error_code,ids_for_check,expected_dates', [
        (
            datetime.datetime(2017, 12, 31, 20),  # active
            'edit',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2017, 1, 1),
                end=datetime.datetime(2025, 7, 7, 7),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            406,
            'bad_params',
            (None, None),
            (None, None)
        ),
        (
            datetime.datetime(2017, 12, 31, 20),  # active
            'edit',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2017, 1, 1),
                end=datetime.datetime(2019, 1, 1, 1),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            406,
            'bad_params',
            (None, None),
            (None, None)
        ),
        (
            datetime.datetime(2017, 12, 31, 20),  # active
            'edit',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2017, 1, 1),
                end=datetime.datetime(2018, 7, 7, 10),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            200,
            None,
            (None, 'id_for_check_smart_edit_2'),
            (None, datetime.datetime(2018, 7, 7, 7))
        ),
        (
            datetime.datetime(2016, 6, 6, 6),  # future contract
            'edit',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2017, 3, 3, 6),
                end=datetime.datetime(2018, 7, 7, 10),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            200,
            None,
            ('id_for_check_smart_edit_1', 'id_for_check_smart_edit_2'),
            (datetime.datetime(2017, 3, 3, 3), datetime.datetime(2018, 7, 7, 7))
        ),
        (
            datetime.datetime(2016, 6, 6, 6),  # future contract
            'edit',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2014, 3, 3, 6),
                end=datetime.datetime(2018, 7, 7, 10),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            406,
            'bad_params',
            (None, None),
            (None, None)
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            'add',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2018, 3, 3, 6),
                end=datetime.datetime(2018, 7, 7, 10),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            406,
            'bad_params',
            (None, None),
            (None, None)
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            'add',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2018, 3, 3, 6),
                end=datetime.datetime(2025, 7, 7, 10),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            406,
            'bad_params',
            (None, None),
            (None, None)
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            'add',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2020, 2, 2, 5),
                end=datetime.datetime(2025, 7, 7, 10),
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            200,
            None,
            ('id_for_check_smart_edit_3', None),
            (datetime.datetime(2020, 2, 2, 2), None)
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            'add',
            _make_add_or_edit_request_data(
                begin=datetime.datetime(2019, 8, 8, 11),
                end=_MISSING,
                tariff_class='uberx',
                **_SMART_EDIT_REQUEST_KWARGS
            ),
            200,
            None,
            ('id_for_check_smart_edit_uberx', None),
            (datetime.datetime(2019, 8, 8, 8), None)
        )
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_commissions_smart_add_or_edit(
        utcnow, method, data, expected_status_code,
        expected_error_code, ids_for_check, expected_dates):
    with freezegun.freeze_time(utcnow, ignore=['']):
        response = _do_add_or_edit_request(
            zone='moscow',
            method=method,
            data=data,
            expected_code=expected_status_code,
        )

    json_response = json.loads(response.content)
    if expected_error_code:
        assert json_response['code'] == expected_error_code, json_response
    else:
        if ids_for_check[0]:
            contract_prev = yield dbh.commission_contracts.Doc.find_one_by_id(ids_for_check[0])
            assert contract_prev.end == expected_dates[0]
        if ids_for_check[1]:
            contract_next = yield dbh.commission_contracts.Doc.find_one_by_id(ids_for_check[1])
            assert contract_next.begin == expected_dates[1]


@pytest.mark.filldb(
    commission_contracts='for_commissions_add_or_edit_test',
)
@pytest.mark.parametrize(
    'utcnow,data,expected_status_code,expected_error_code', [
        (
            datetime.datetime(2017, 12, 31, 21),
            _make_add_or_edit_request_data(
                id='some_fixed_percent_commission_contract_id',
                **_FIXED_PERCENT_REQUEST_KWARGS
            ),
            406,
            'cant_edit_finished',
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            _make_add_or_edit_request_data(
                id='some_fixed_percent_commission_contract_id',
                **_ALMOST_SAME_FIXED_PERCENT_REQUEST_KWARGS
            ),
            406,
            'cant_edit_active',
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            _make_add_or_edit_request_data(
                id='some_asymptotic_formula_commission_contract_id',
                **_ALMOST_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS
            ),
            406,
            'cant_edit_active',
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            _make_add_or_edit_request_data(
                id='some_asymptotic_formula_commission_contract_id',
                **_ANOTHER_ALMOST_SAME_ASYMPTOTIC_FORMULA_REQUEST_KWARGS
            ),
            406,
            'cant_edit_active',
        ),
        (
            datetime.datetime(2017, 12, 31, 20),
            _make_add_or_edit_request_data(
                id='some_absolute_value_commission_contract_id',
                **_ALMOST_SAME_ABSOLUTE_VALUE_REQUEST_KWARGS
            ),
            406,
            'cant_edit_active',
        ),
    ])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_commissions_edit_failure(
        utcnow, data, expected_status_code, expected_error_code):
    num_contracts_before = yield _get_num_contracts()
    with freezegun.freeze_time(utcnow, ignore=['']):
        response = _do_add_or_edit_request(
            zone=None,
            method='edit',
            data=data,
            expected_code=expected_status_code,
        )
    num_contracts_after = yield _get_num_contracts()

    assert num_contracts_before == num_contracts_after
    json_response = json.loads(response.content)
    assert json_response['code'] == expected_error_code, json_response


@pytest.mark.now('2016-10-07T00:00:00')
@pytest.mark.filldb(
    commission_contracts='for_commissions_delete_test',
)
@pytest.mark.parametrize('ids_for_delete,all_ids_for_check', [
    (
            ['contract_id_middle', 'contract_id_first'],
            [
                ('contract_id_first', 'contract_id_last'),
                ('active_contract', 'contract_id_last')
            ]
    ),
    (
            ['contract_id_first', 'contract_id_middle', 'contract_id_last'],
            [
                ('active_contract', 'contract_id_middle'),
                ('active_contract', 'contract_id_last'),
                ('active_contract', None)
            ]
    ),
    (
            ['contract_id_last', ],
            [
                ('contract_id_middle', None),
            ]
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_commissions_delete(ids_for_delete, all_ids_for_check):
    for id_for_delete, ids_for_check in zip(ids_for_delete, all_ids_for_check):
        num_contracts_before = yield _get_num_contracts()
        _do_delete_request(id_for_delete)
        assert (yield _get_num_contracts()) == num_contracts_before - 1

        contract = yield dbh.commission_contracts.Doc.find_one_by_id(ids_for_check[0])
        if ids_for_check[1]:
            contract_2 = yield dbh.commission_contracts.Doc.find_one_by_id(ids_for_check[1])
            assert contract.end == contract_2.begin
        else:
            assert contract.end == dbh.commission_contracts.DEFAULT_END


@pytest.mark.filldb(
    commission_contracts='for_commissions_delete_test',
)
@pytest.mark.parametrize('utcnow,expected_status_code,expected_error_code', [
    (datetime.datetime(2017, 1, 1), 406, 'cant_delete_active'),
    (datetime.datetime(2017, 12, 31, 21), 406, 'cant_delete_finished'),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_commissions_delete_failure(
        utcnow, expected_status_code, expected_error_code):
    num_contracts_before = yield _get_num_contracts()
    with freezegun.freeze_time(utcnow, ignore=['']):
        response = _do_delete_request(
            contract_id='contract_id_first',
            expected_code=expected_status_code,
        )
    json_response = json.loads(response.content)
    assert json_response['status'] == 'error'
    assert json_response['code'] == expected_error_code
    # checking that nothing was deleted
    assert (yield _get_num_contracts()) == num_contracts_before


@pytest.mark.filldb(
    log_admin='for_commissions_log_test',
)
@pytest.mark.parametrize('contract_id,expected_log_count', [
    ('some_existing_commission_contract_id', 1),
    ('some_not_existing_commission_contract_id', 0),
])
@pytest.mark.asyncenv('blocking')
def test_commissions_log(contract_id, expected_log_count):
    url = '/api/commissions/{}/log/'.format(contract_id)
    response = django_test.Client().get(url)
    actual_log_count = len(json.loads(response.content)['items'])
    assert actual_log_count == expected_log_count


@pytest.mark.filldb(
    commission_contracts='for_commissions_add_or_edit_test',
)
@pytest.mark.parametrize('zone,expected_count', [
    ('moscow', 1),
    ('spb', 1),
    ('voronezh', 1),
])
@pytest.mark.asyncenv('blocking')
def test_commissions_list(zone, expected_count):
    url = '/api/commissions/{}/list/'.format(zone)
    response = django_test.Client().get(url)
    actual_items_count = len(json.loads(response.content)['items'])
    assert actual_items_count == expected_count


@pytest.mark.filldb(
    commission_contracts='for_commissions_add_or_edit_test',
)
@pytest.mark.asyncenv('blocking')
def test_commissions_list_unknown_zone():
    url = '/api/commissions/unknown_zone/list/'
    response = django_test.Client().get(url)
    assert response.status_code == 404


@async.inline_callbacks
def _get_num_contracts():
    count = yield db.commission_contracts.count()
    async.return_value(count)


def _do_add_or_edit_request(zone, method, data, expected_code=200):
    assert method in ['add', 'edit']
    if method == 'edit':
        url = '/api/commissions/edit/'
    else:
        url = '/api/commissions/{}/{}/'.format(zone, method)
    request_body = json.dumps(data)
    response = django_test.Client().post(url, request_body, 'application/json')
    assert response.status_code == expected_code, response.content
    return response


def _do_delete_request(contract_id, expected_code=200):
    url = '/api/commissions/delete/'
    data = {
        'id': contract_id,
        'ticket': 'TAXIRATE-1'
    }
    request_data = json.dumps(data)
    response = django_test.Client().post(url, request_data, 'application/json')
    assert response.status_code == expected_code, response.content
    return response


@async.inline_callbacks
def _get_single_contract():
    num_contracts = yield db.commission_contracts.count()
    assert num_contracts == 1
    contract = dbh.commission_contracts.Doc(
        (yield db.commission_contracts.find_one()),
    )
    async.return_value(contract)


def assert_inner_decimal_equal(inner_value, decimalable_value):
    decimal_value = decimal.Decimal(decimalable_value)
    assert payment_helpers.inner_to_decimal(inner_value) == decimal_value


def assert_branding_discounts_equal(inner, decimalable):
    assert len(inner) == len(decimalable)
    for inner_item, decimalable_item in zip(inner, decimalable):
        inner_level = inner_item['marketing_level']
        decimalable_level = decimalable_item['marketing_level']
        assert inner_level == decimalable_level
        inner_value = inner_item['value']
        decimalable_value = decimalable_item['value']
        assert_inner_decimal_equal(inner_value, decimalable_value)


def assert_asymptotic_data_equal(inner_data, decimalable_data):
    keys = {
        'cost_norm', 'numerator', 'asymp', 'max_commission_percent'
    }
    assert_keys_in_data_equal(inner_data, decimalable_data, keys)


def assert_absolute_data_equal(inner_data, decimalable_data):
    keys = {
        'commission',
        'cancel_commission',
        'expired_commission',
    }
    assert_keys_in_data_equal(inner_data, decimalable_data, keys)


def assert_keys_in_data_equal(inner_data, decimalable_data, keys):
    assert inner_data.viewkeys() == keys
    assert decimalable_data.viewkeys() == keys
    for key in keys:
        inner_value = inner_data[key]
        decimalable_value = decimalable_data[key]
        assert_inner_decimal_equal(inner_value, decimalable_value)


@pytest.mark.filldb(tariff_settings='csv', commission_contracts='csv')
@pytest.mark.parametrize('request_body, status_code, expected', [
    ({"zones": ['voronezh', 'kitezh'], "countries": ['England', 'Neverland']}, 200, 'england_and_voronezh.csv'),
    ({}, 200, 'all_zones.csv'),
    (
        {
            'fields': [
                'conditions.zone',
                'begin',
                'end',
                'commission.callcenter_commission_percent',
            ],
        },
        200,
        'all_zones.custom_order_1.csv',
    ),
    (
        {
            'fields': [
                'conditions.tariff_class',
                'conditions.zone',
                'end',
                'begin',
                'commission.callcenter_commission_percent',
                'conditions.payment_type',
            ]
        },
        200,
        'all_zones.custom_order_2.csv',
    ),
])
@pytest.mark.asyncenv('blocking')
def test_export_to_csv(load, request_body, status_code, expected):
    request_body.update({"date": "2017-07-13T13:33:00+0300"})
    response = django_test.Client().post(
        urlresolvers.reverse(commissions.export_to_csv),
        json.dumps(
            request_body
        ),
        content_type='application/json'
    )
    assert response.status_code == status_code
    assert response.content.decode("utf-8-sig").replace('\r', '') == load(expected)


@pytest.mark.now('2019-07-02T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_create_check(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield

    @patch('uuid.uuid4')
    def uuid4():
        uuid4_tuple = collections.namedtuple('uuid4', 'hex')
        return uuid4_tuple('c2252f07b652410a887bc4599a5f6763')

    client = django_test.Client()
    request_data = load('request/approvals_create_request_data.json')
    expected_response = json.loads(
        load('response/approvals_create_check_expected_response.json'),
    )
    response = client.post(
        '/api/approvals/commissions_create/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200

    response_content = json.loads(response.content)
    response_content.pop('diff')
    assert response_content == expected_response


@pytest.mark.now('2019-07-02T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_create_apply(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('request/approvals_create_request_data.json')
    response = client.post(
        '/api/approvals/commissions_create/apply/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {'status': 'succeeded'}


@pytest.mark.filldb(
    commission_contracts='for_commissions_add_or_edit_test',
)
@pytest.mark.now('2016-10-07T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_edit_check(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield

    client = django_test.Client()
    request_data = load('request/approvals_edit_request_data.json')
    expected_response = json.loads(
        load('response/approvals_edit_check_expected_response.json'),
    )
    response = client.post(
        '/api/approvals/commissions_edit/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_response


@pytest.mark.filldb(
    commission_contracts='for_commissions_add_or_edit_test',
)
@pytest.mark.now('2016-10-07T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_edit_apply(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('request/approvals_edit_request_data.json')
    response = client.post(
        '/api/approvals/commissions_edit/apply/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200


@pytest.mark.filldb(
    commission_contracts='for_commissions_delete_test',
)
@pytest.mark.now('2016-10-07T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_delete_check(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    @patch('taxiadmin.audit.check_taxirate')
    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield

    client = django_test.Client()
    request_data = {
        'id': 'contract_id_last',
    }
    expected_response = json.loads(
        load('response/approvals_delete_check_expected_response.json'),
    )
    response = client.post(
        '/api/approvals/commissions_delete/check/',
        json.dumps(request_data),
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='karachevda',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    response_client = json.loads(response.content)
    response_client.pop('diff')
    assert response_client == expected_response


@pytest.mark.filldb(
    commission_contracts='for_commissions_delete_test',
)
@pytest.mark.now('2016-10-07T22:06:01')
@pytest.mark.asyncenv('blocking')
def test_approvals_delete_apply(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = {
        'id': 'contract_id_last',
        'ticket': 'TAXIRATE-35',
    }
    response = client.post(
        '/api/approvals/commissions_delete/apply/',
        json.dumps(request_data),
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='karachevda',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
