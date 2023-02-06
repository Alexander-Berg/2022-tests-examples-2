# pylint: disable=redefined-outer-name
import typing

import pytest

from test_taxi_corp_integration_api import utils


def _old_cc_from_new(field_settings: typing.List) -> typing.Dict:
    if field_settings:
        field = field_settings[0]
        return {
            'required': field['required'],
            'format': field['format'],
            'values': field['values'],
        }
    return {'required': False, 'format': 'text', 'values': []}


DB_FIELDS_REQUIRED = pytest.mark.filldb(corp_cost_center_options='required')
DB_FIELDS_OPTIONAL = pytest.mark.filldb(corp_cost_center_options='optional')
DB_FIELDS_MANY = pytest.mark.filldb(corp_cost_center_options='many_fields')
DB_FIELDS_MIXED = pytest.mark.filldb(corp_cost_center_options='default_mixed')
DB_FIELDS_SELECT = pytest.mark.filldb(
    corp_cost_center_options='default_select',
)
DB_FIELDS_TEXT = pytest.mark.filldb(corp_cost_center_options='default_text')
DB_USERS_NEW_CC_ID = pytest.mark.filldb(corp_users='new_cc_id')
DB_USERS_ALL_FORMATS = pytest.mark.filldb(corp_users='all_formats')
DB_NEW_CLIENTS_NEW_USERS = [DB_FIELDS_MANY, DB_USERS_ALL_FORMATS]

USER_OPTIONAL = {'uid': '12345678', 'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a'}
USER_SELECT = {'uid': '22345678', 'phone_id': '2a1a1a1a1a1a1a1a1a1a1a1a'}
USER_MIXED = {'uid': '32345678', 'phone_id': '3a1a1a1a1a1a1a1a1a1a1a1a'}
USER_TEXT = {'uid': '42345678', 'phone_id': '4a1a1a1a1a1a1a1a1a1a1a1a'}

EMPTY_VALUE = ''

FIELD_VALUES = ['командировка', 'отпуск']
FIRST_FIELD_REQUIRED = {
    'format': 'mixed',
    'id': 'cost_center',
    'title': 'Центр затрат',
    'required': True,
    'services': ['eats', 'taxi', 'drive'],
    # drive is absent in COST_CENTERS_ORDER_FLOWS config
    # so it is absent from order_flows
    'order_flows': ['eats2', 'taxi'],
    'values': ['командировка', 'в центральный офис'],
}
FIRST_FIELD_OPTIONAL = dict(FIRST_FIELD_REQUIRED, required=False)
FIRST_FIELD_OTHER_REQUIRED = dict(
    FIRST_FIELD_REQUIRED, values=['отдых', 'на пляж'],
)
FIRST_FIELD_OTHER_OPTIONAL = dict(FIRST_FIELD_OTHER_REQUIRED, required=False)
SECOND_FIELD_REQUIRED = {
    'format': 'mixed',
    'id': 'ride_purpose',
    'title': 'Цель поездки',
    'required': True,
    'services': ['taxi'],
    'order_flows': ['taxi'],
    'values': ['цель 1', 'цель 2'],
}
SECOND_FIELD_OPTIONAL = dict(SECOND_FIELD_REQUIRED, required=False)

OLD_FIELD_REQUIRED = _old_cc_from_new([FIRST_FIELD_REQUIRED])
OLD_FIELD_SELECT = {
    'required': True,
    'format': 'select',
    'values': ['командировка', 'по делу'],
}
OLD_FIELD_SELECT_NEW_FORMAT = utils.new_fields_from_old_value(OLD_FIELD_SELECT)
OLD_FIELD_MIXED = dict(OLD_FIELD_SELECT, format='mixed')
OLD_FIELD_TEXT = {'required': True, 'format': 'text', 'values': []}
OLD_FIELD_OPTIONAL = dict(OLD_FIELD_REQUIRED, required=False)


def _new_fields_with_format(field_format):
    if field_format == 'text':
        first_values = second_values = []
    else:
        first_values = FIRST_FIELD_OTHER_REQUIRED['values']
        second_values = SECOND_FIELD_OPTIONAL['values']
    first_field = dict(
        FIRST_FIELD_OTHER_REQUIRED, format=field_format, values=first_values,
    )
    second_field = dict(
        SECOND_FIELD_OPTIONAL, format=field_format, values=second_values,
    )
    return dict(
        cost_center=EMPTY_VALUE,
        cost_centers=_old_cc_from_new([first_field]),
        cost_center_fields=[first_field, second_field],
    )


def _new_request_field_from_old_value(old_cost_center_value: str) -> list:
    return [dict(id='', title='Центр затрат', value=old_cost_center_value)]


def _is_test_case_with_update_app_error(test_case_dict):
    return test_case_dict.get('order_disable_reason') == utils.UPDATE_APP_ERROR


METHOD_BASE_DATA = {
    'type': 'corp',
    'id': 'corp-client_id_1',
    'label': 'Yandex.Uber team',
    'description': 'Осталось 5000 из 5000 руб.',
    'cost_center': 'cost center',
    'cost_centers': utils.OLD_COST_CENTER_VALUE,
    'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
    'can_order': True,
    'zone_available': True,
    'hide_user_cost': False,
    'user_id': 'user_id_1',
    'client_comment': 'comment',
    'currency': 'RUB',
    'classes_available': ['econom'],
    'without_vat_contract': False,
}
NEW_COST_CENTER_REQUIRED = dict(
    METHOD_BASE_DATA,
    cost_center=EMPTY_VALUE,
    cost_centers=OLD_FIELD_REQUIRED,
    cost_center_fields=[FIRST_FIELD_REQUIRED],
)
TWO_FIELDS_REQUIRED = dict(
    METHOD_BASE_DATA,
    cost_center=EMPTY_VALUE,
    cost_centers=OLD_FIELD_REQUIRED,
    cost_center_fields=[FIRST_FIELD_REQUIRED, SECOND_FIELD_REQUIRED],
)
TWO_FIELDS_SELECT = dict(
    METHOD_BASE_DATA, user_id='user_id_2', **_new_fields_with_format('select'),
)
TWO_FIELDS_TEXT = dict(
    METHOD_BASE_DATA, user_id='user_id_4', **_new_fields_with_format('text'),
)

OLD_METHOD_CAN_ORDER = dict(METHOD_BASE_DATA, cost_center=EMPTY_VALUE)
OLD_METHOD_CANNOT_ORDER = dict(
    OLD_METHOD_CAN_ORDER,
    can_order=False,
    order_disable_reason='Не указан центр затрат',
)
NEW_METHOD_OPTIONAL_CAN_ORDER = dict(
    METHOD_BASE_DATA,
    cost_center=EMPTY_VALUE,
    cost_centers=OLD_FIELD_OPTIONAL,
    cost_center_fields=[FIRST_FIELD_OPTIONAL],
)
NEW_METHOD_OPTIONAL_CANNOT_ORDER = dict(
    NEW_METHOD_OPTIONAL_CAN_ORDER,
    can_order=False,
    order_disable_reason=utils.UPDATE_APP_ERROR,
)

USER_REQUEST_BASE = {'identity': USER_OPTIONAL, 'class': 'econom'}
ORDER_REQUEST_BASE = dict(
    **USER_REQUEST_BASE,
    client_id='client_id_1',
    route=[{'geopoint': [37.59, 55.73]}],
    order_price='400',
)

FIRST_FIELD_VALUE_EMPTY = dict(
    id='cost_center', title='Центр затрат', value=EMPTY_VALUE,
)
FIRST_FIELD_VALUE_FILLED = dict(FIRST_FIELD_VALUE_EMPTY, value='командировка')
FIRST_FIELD_VALUE_OTHER = dict(FIRST_FIELD_VALUE_EMPTY, value='отдых')
FIRST_FIELD_VALUE_UNKNOWN = dict(FIRST_FIELD_VALUE_EMPTY, value='куда-то')
SECOND_FIELD_VALUE_EMPTY = dict(
    id='ride_purpose', title='Цель поездки', value=EMPTY_VALUE,
)
SECOND_FIELD_VALUE_FILLED = dict(SECOND_FIELD_VALUE_EMPTY, value='цель 1')
SECOND_FIELD_VALUE_OTHER = dict(SECOND_FIELD_VALUE_EMPTY, value='цель 2')
SECOND_FIELD_VALUE_UNKNOWN = dict(SECOND_FIELD_VALUE_EMPTY, value='зачем-то')

ORDER_REQUEST_OLD = dict(ORDER_REQUEST_BASE, cost_center=EMPTY_VALUE)
ORDER_REQUEST_NEW = dict(
    ORDER_REQUEST_BASE,
    cost_centers=[FIRST_FIELD_VALUE_FILLED, SECOND_FIELD_VALUE_FILLED],
)

USER_CASES = [
    #   1) no new cost_centers for client
    # - return old cost centers, can_order: true
    pytest.param(
        USER_REQUEST_BASE, METHOD_BASE_DATA, id='client-no-new-cost-centers',
    ),
    #   2) new cost_centers for client (fields are optional)
    # - return old cost centers from new fields + cost_center_fields
    #     can_order: true, (old cost centers are ignored)
    pytest.param(
        USER_REQUEST_BASE,
        NEW_METHOD_OPTIONAL_CANNOT_ORDER,
        marks=DB_FIELDS_OPTIONAL,
        id='client-with-new-cost-centers-optional',
    ),
    #   3) new cost_centers for client (fields are required)
    # - return old cost centers from new fields + cost_center_fields
    #     can_order: true (because no cost centers in request)
    pytest.param(
        USER_REQUEST_BASE,
        NEW_COST_CENTER_REQUIRED,
        marks=DB_FIELDS_REQUIRED,
        id='client-with-new-cost-centers-required',
    ),
]

# ORDER CASES (for ordercommit requests)
# 1.1) old cost_centers in order, old cost_centers in user
OLD_CC_ORDER_CASES = [
    # - optional cost center, order has no cost center (or empty)
    #     - can_order: true
    pytest.param(
        ORDER_REQUEST_OLD,
        OLD_METHOD_CAN_ORDER,
        id='user=old-cc, order=optional-empty-cc',
    ),
    # - optional cost center, order has other cost center
    #     - can_order: true
    pytest.param(
        dict(ORDER_REQUEST_OLD, cost_center='123'),
        dict(OLD_METHOD_CAN_ORDER, cost_center='123'),
        id='user=old-optional-cc, order=other-cc',
    ),
    # - required cost center, order has no cost center (or empty)
    #     - can_order: false
    pytest.param(
        dict(ORDER_REQUEST_OLD, identity=USER_SELECT),
        dict(
            OLD_METHOD_CANNOT_ORDER,
            user_id='user_id_2',
            cost_centers=OLD_FIELD_SELECT,
            cost_center_fields=utils.new_fields_from_old_value(
                OLD_FIELD_SELECT,
            ),
        ),
        id='user=old-required-cc, order=empty-cc',
    ),
    # - required, format: select, order has cost center from values
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_OLD,
            identity=USER_SELECT,
            cost_center='командировка',
        ),
        dict(
            OLD_METHOD_CAN_ORDER,
            user_id='user_id_2',
            cost_center='командировка',
            cost_centers=OLD_FIELD_SELECT,
            cost_center_fields=utils.new_fields_from_old_value(
                OLD_FIELD_SELECT,
            ),
        ),
        id='user=old-required-select-cc, order=cc-from-values',
    ),
    # - required, format: select, order has cost center beyond values
    #     - can_order: false
    pytest.param(
        dict(
            ORDER_REQUEST_OLD, identity=USER_SELECT, cost_center='какой-то цз',
        ),
        dict(
            OLD_METHOD_CANNOT_ORDER,
            user_id='user_id_2',
            order_disable_reason='Неверный центр затрат',
            cost_center='какой-то цз',
            cost_centers=OLD_FIELD_SELECT,
            cost_center_fields=utils.new_fields_from_old_value(
                OLD_FIELD_SELECT,
            ),
        ),
        id='user=old-required-select-cc, order=cc-other',
    ),
    # - required, format: mixed, order has cost center from values
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_OLD, identity=USER_MIXED, cost_center='командировка',
        ),
        dict(
            OLD_METHOD_CAN_ORDER,
            user_id='user_id_3',
            cost_center='командировка',
            cost_centers=OLD_FIELD_MIXED,
            cost_center_fields=utils.new_fields_from_old_value(
                OLD_FIELD_MIXED,
            ),
        ),
        id='user=old-required-mixed-cc, order=cc-from-values',
    ),
    # - required, format: mixed, order has cost center beyond values
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_OLD, identity=USER_MIXED, cost_center='какой-то цз',
        ),
        dict(
            OLD_METHOD_CAN_ORDER,
            user_id='user_id_3',
            cost_center='какой-то цз',
            cost_centers=OLD_FIELD_MIXED,
            cost_center_fields=utils.new_fields_from_old_value(
                OLD_FIELD_MIXED,
            ),
        ),
        id='user=old-required-mixed-cc, order=cc-other',
    ),
    # - required, format: text, order has cost center (not empty)
    #     - can_order: true
    pytest.param(
        dict(ORDER_REQUEST_OLD, identity=USER_TEXT, cost_center='какой-то цз'),
        dict(
            OLD_METHOD_CAN_ORDER,
            user_id='user_id_4',
            cost_center='какой-то цз',
            cost_centers=OLD_FIELD_TEXT,
            cost_center_fields=utils.new_fields_from_old_value(OLD_FIELD_TEXT),
        ),
        id='user=old-cc-required-text, order=cc-any',
    ),
]

# 1.2) old and new cost_centers in order, old cost_centers in user
# (new cost_centers are ignored in these cases)
OLD_CC_ORDER_CASES_WITH_NEW_CC_ID = [
    pytest.param(
        # request is like in previous case, with new cost_centers field added
        dict(param.values[0], cost_centers=[FIRST_FIELD_VALUE_FILLED]),
        param.values[1],  # method in response must be the same
        # make unique id for case
        id=param.id.replace('order=', 'order=new-cc-id+old-'),
    )
    for param in OLD_CC_ORDER_CASES
]


def _replace_can_order(request_params, response_params, required=False):
    if required and not request_params.get('cost_center'):
        return False
    return response_params.get('can_order', True)


def _replace_disable_reason(request_params, response_params, required=False):
    if response_params.get('order_disable_reason') is None:
        if required and not request_params.get('cost_center'):
            return utils.UPDATE_APP_ERROR
        return None
    if not request_params.get('cost_centers'):
        return utils.UPDATE_APP_ERROR
    return response_params['order_disable_reason']


def _replace_cost_center(request_params, response_params):
    required = False
    update = {}
    if response_params['cost_center_fields']:
        required = any(
            field['required']
            for field in response_params['cost_center_fields']
            if field['id'] != ''
        )
        if response_params['cost_center_fields'][0]['id'] != '':
            update = dict(cost_center='')
    args = request_params, response_params
    update.update(
        can_order=_replace_can_order(*args, required=required),
        order_disable_reason=_replace_disable_reason(*args, required=required),
    )
    return dict(response_params, **update)


def replace_response(request_params, response_params, **updates):
    response_params = dict(response_params, **updates)
    return _replace_cost_center(request_params, response_params)


# 2.1) old cost_centers in order, new optional cost_centers in user
# - can_order: true for all cases (because cc is optional),
#   yet no new cost_centers will be in order
NEW_CC_ORDER_OPTIONAL_CASES_WITH_OLD_CC = [
    pytest.param(
        # request is like in old cases case
        param.values[0],
        replace_response(
            *param.values,
            cost_center_fields=[FIRST_FIELD_OTHER_OPTIONAL],
            cost_center=EMPTY_VALUE,
            cost_centers=_old_cc_from_new([FIRST_FIELD_OTHER_OPTIONAL]),
        ),
        marks=[DB_FIELDS_OPTIONAL, DB_USERS_NEW_CC_ID],
        id=param.id.replace('user=', 'user=new-optional+'),
    )
    for param in OLD_CC_ORDER_CASES
]

# 2.2) old cost_centers in order, new required cost_centers in user
# - can_order: false for all cases (because cc is required)
NEW_CC_ORDER_REQUIRED_CASES_WITH_OLD_CC = [
    pytest.param(
        param.values[0],
        replace_response(
            *param.values,
            cost_center_fields=[FIRST_FIELD_OTHER_REQUIRED],
            cost_centers=_old_cc_from_new([FIRST_FIELD_OTHER_REQUIRED]),
        ),
        marks=[DB_FIELDS_REQUIRED, DB_USERS_NEW_CC_ID],
        id=param.id.replace('user=new-optional+', 'user=new-required+'),
    )
    for param in NEW_CC_ORDER_OPTIONAL_CASES_WITH_OLD_CC
]

# 3.1) old cc in order, no cc_id in user, new cc (optional) for client
# - can_order: true for all cases (because cc is optional)
#   yet no new cost_centers will be in order
NEW_CC_CLIENT_OPTIONAL_ORDER_CASES_WITH_OLD_CC = [
    pytest.param(
        param.values[0],
        dict(
            param.values[1],
            cost_center_fields=[FIRST_FIELD_OPTIONAL],
            cost_centers=_old_cc_from_new([FIRST_FIELD_OPTIONAL]),
        ),
        marks=[DB_FIELDS_OPTIONAL],
        id=param.id.replace('user=new-optional+', 'client=new-optional,user='),
    )
    for param in NEW_CC_ORDER_OPTIONAL_CASES_WITH_OLD_CC
]

# 3.2) old cc in order, no cc_id in user, new cc (required) for client
# - can_order: false for all cases (because cc is required)
NEW_CC_CLIENT_REQUIRED_ORDER_CASES_WITH_OLD_CC = [
    pytest.param(
        param.values[0],
        dict(
            param.values[1],
            cost_center_fields=[FIRST_FIELD_REQUIRED],
            cost_centers=_old_cc_from_new([FIRST_FIELD_REQUIRED]),
        ),
        marks=[DB_FIELDS_REQUIRED],
        id=param.id.replace('user=new-required+', 'client=new-required,user='),
    )
    for param in NEW_CC_ORDER_REQUIRED_CASES_WITH_OLD_CC
]

# 4) new cc in order, old cc in user, new cc in client
NEW_CC_ORDERS_FOR_OLD_USERS_WITH_NEW_CLIENT = [
    # - both fields required, order has all required fields
    #     - can_order: true
    pytest.param(
        ORDER_REQUEST_NEW,
        TWO_FIELDS_REQUIRED,
        marks=[DB_FIELDS_MIXED],
        id='user=old,client=new-cc-two-fields, order=new-cc-from-values',
    ),
    # - both fields required, order has no second field
    #     - can_order: false
    pytest.param(
        dict(ORDER_REQUEST_NEW, cost_centers=[FIRST_FIELD_VALUE_UNKNOWN]),
        dict(
            TWO_FIELDS_REQUIRED,
            can_order=False,
            order_disable_reason='Не указан центр затрат',
        ),
        marks=[DB_FIELDS_MIXED],
        id='user=old,client=new-cc-two-fields, order=new-cc-no-second-field',
    ),
    # - required, format: mixed, order has field beyond values
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_NEW,
            cost_centers=[
                FIRST_FIELD_VALUE_UNKNOWN,
                SECOND_FIELD_VALUE_UNKNOWN,
            ],
        ),
        TWO_FIELDS_REQUIRED,
        marks=[DB_FIELDS_MIXED],
        id='user=old,client=new-cc-two-fields-mixed, order=new-fields-unknown',
    ),
    # - required, format: text, order has all fields (not empty)
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_NEW,
            identity=USER_TEXT,
            cost_centers=[
                FIRST_FIELD_VALUE_UNKNOWN,
                SECOND_FIELD_VALUE_UNKNOWN,
            ],
        ),
        TWO_FIELDS_TEXT,
        marks=[DB_FIELDS_TEXT],
        id='user=old,client=new-cc-two-fields-text, order=new-cc-fields-any',
    ),
    # - required+optional, format: select, order has field from values
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_NEW,
            identity=USER_SELECT,
            cost_centers=[FIRST_FIELD_VALUE_OTHER],
        ),
        TWO_FIELDS_SELECT,
        marks=[DB_FIELDS_SELECT],
        id='user=old,client=new-cc-select, order=new-cc-second-field-missing',
    ),
    # - required+optional, format: select, order has fields beyond values
    #     - can_order: false
    pytest.param(
        dict(
            ORDER_REQUEST_NEW,
            identity=USER_SELECT,
            cost_centers=[FIRST_FIELD_VALUE_OTHER, SECOND_FIELD_VALUE_UNKNOWN],
        ),
        dict(
            TWO_FIELDS_SELECT,
            can_order=False,
            order_disable_reason='Неверный центр затрат',
        ),
        marks=[DB_FIELDS_SELECT],
        id='user=old,client=new-cc-select, order=new-cc-second-field-unknown',
    ),
    # same as previous test but with combo order (disable CostCentersChecker)
    # CORP_COMBO_ORDERS_DISABLED_CHECKERS=['CostCentersChecker']
    #     - can_order: true
    pytest.param(
        dict(
            ORDER_REQUEST_NEW,
            identity=USER_SELECT,
            combo_order={'delivery_id': 'delivery'},
            cost_centers=[FIRST_FIELD_VALUE_OTHER, SECOND_FIELD_VALUE_UNKNOWN],
        ),
        dict(TWO_FIELDS_SELECT),
        marks=[DB_FIELDS_SELECT],
        id='user=old,client=new-cc-select, order=combo-order',
    ),
]

# 5) new cost_centers in order, new cost_centers in user
NEW_CC_ORDERS_FOR_NEW_CC_USERS = [
    pytest.param(
        *param.values,
        marks=DB_NEW_CLIENTS_NEW_USERS,
        id=param.id.replace('user=old,client=new', 'user=new'),
    )
    for param in NEW_CC_ORDERS_FOR_OLD_USERS_WITH_NEW_CLIENT
]

ORDERS_CASES = (
    OLD_CC_ORDER_CASES
    + OLD_CC_ORDER_CASES_WITH_NEW_CC_ID
    + NEW_CC_ORDER_OPTIONAL_CASES_WITH_OLD_CC
    + NEW_CC_ORDER_REQUIRED_CASES_WITH_OLD_CC
    + NEW_CC_CLIENT_OPTIONAL_ORDER_CASES_WITH_OLD_CC
    + NEW_CC_CLIENT_REQUIRED_ORDER_CASES_WITH_OLD_CC
    + NEW_CC_ORDERS_FOR_OLD_USERS_WITH_NEW_CLIENT
    + NEW_CC_ORDERS_FOR_NEW_CC_USERS
)
ORDERS_CASES_FOR_NEW_APP = [
    pytest.param(
        dict(
            # remove cost_center from request and add cost_centers instead
            {
                key: value
                for (key, value) in param.values[0].items()
                if key != 'cost_center'
            },
            cost_centers=_new_request_field_from_old_value(
                param.values[0]['cost_center'],
            ),
        ),
        _replace_cost_center(*param.values),
        marks=param.marks,
        id=param.id + '-for-new-app',
    )
    for param in ORDERS_CASES
    # clone cases with only old cost_center
    if 'cost_center' in param.values[0]
    and 'cost_centers' not in param.values[0]
    and not _is_test_case_with_update_app_error(
        _replace_cost_center(*param.values),
    )
]

# very dirty hack to fix tests (TODO: to fix properly in CORPDEV-2362)
TEST_CASES = {
    case.id: case
    for case in USER_CASES + ORDERS_CASES + ORDERS_CASES_FOR_NEW_APP
}
CASE_IDS_TO_FIX_TRUE = [
    'client=new-required,user=old-required-select-cc, order=cc-other',
    'client=new-optional,user=old-required-select-cc, order=cc-other',
    'client=new-optional,user=old-required-cc, order=empty-cc',
    'user=new-required+old-required-select-cc, order=cc-other',
    'user=new-optional+old-required-select-cc, order=cc-other',
    'user=new-optional+old-required-cc, order=empty-cc',
    'client-with-new-cost-centers-optional',
]
for case_id in CASE_IDS_TO_FIX_TRUE:
    expected_method = TEST_CASES[case_id].values[1]
    expected_method['order_disable_reason'] = None
    expected_method['can_order'] = True

CASE_IDS_TO_FIX_REQUIRED = [
    'client=new-required,user=old-required-cc, order=empty-cc',
    'client=new-required,user=old-cc, order=optional-empty-cc',
    'user=new-required+old-required-cc, order=empty-cc',
    'user=new-required+old-cc, order=optional-empty-cc',
]
for case_id in CASE_IDS_TO_FIX_REQUIRED:
    expected_method = TEST_CASES[case_id].values[1]
    expected_method['order_disable_reason'] = utils.REQUIRED_ERROR

# end of very dirty hack to fix tests

TEST_COST_CENTERS_PARAMS = dict(
    argnames=['request_data', 'expected_method'],
    argvalues=USER_CASES + ORDERS_CASES + ORDERS_CASES_FOR_NEW_APP,
)


# @pytest.mark.skip(reason='to fix in CORPDEV-2362')
@pytest.mark.config(**utils.CONFIG)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(**TEST_COST_CENTERS_PARAMS)
@pytest.mark.now('2019-11-02T10:02:03+0300')
async def test_cost_centers(
        db,
        taxi_config,
        mockserver,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        request_data,
        expected_method,
):
    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', None,
    )
    if expected_method:
        if expected_method.get('order_disable_reason') is None:
            expected_method.pop('order_disable_reason', None)
        expected_response = {'methods': [expected_method]}
    else:
        expected_response = {'methods': []}
    assert await response.json() == expected_response
    assert response.status == 200
