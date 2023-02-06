import decimal


# common
PARK_ID = 'extra_super_park_id'
IDEMPOTENCY_TOKEN = 'extra_super_idempotency_token'
X_YA_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxDe9no:ULpQccuOm6SKtwoVE'
    'iO1IK_G5OWMfyeZlXIm-w3o3m4u4l1voLP-8tfJyoLpAoOV51CiH'
    'x5xjtQSN-u_3hyNdePIj6VvDHR5KfPQGqT6hjsjqwU2HpArsUXHM'
    'yk0mFSixyOqE2ety5ofeWBC29RYonNklTAWt--ivuRblG2Wbco'
)
GROUP_ID = 'gid1'
GROUP_NAME = 'group1'
EMAIL = 'default@yandex.ru'
USER_IP = '1.2.3.4'
HEADERS = {
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
    'X-Ya-Service-Ticket': X_YA_SERVICE_TICKET,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': PARK_ID,
}
PARAMS = {'park_id': PARK_ID}
BASE_YANDEX_AUTHOR_IDENTITY = {
    'identity': {
        'type': 'passport_user',
        'user_ip': USER_IP,
        'passport_uid': '1',
    },
}
BASE_YANDEX_TEAM_AUTHOR_IDENTITY = {
    'identity': {
        'type': 'passport_yandex_team',
        'user_ip': USER_IP,
        'passport_uid': '1',
    },
}
BASE_SCRIPT_AUTHOR_IDENTITY = {
    'identity': {'type': 'script', 'script_id': 'extra_super_script_id'},
}
BASE_JOB_AUTHOR_IDENTITY = {
    'identity': {'type': 'job', 'job_name': 'extra_super_job_name'},
}
BASE_REQUEST_AUTHOR = {
    'consumer': 'extra_super_consumer',
    'identity': {
        'type': 'passport_user',
        'user_ip': USER_IP,
        'passport_uid': '1',
    },
}
LOG_INFO = {
    'park_id': PARK_ID,
    'user_id': 'user1',
    'user_name': '--',
    'counts': 0,
    'ip': USER_IP,
}
MAXIMUM_LENGTH_NAME = 'abcde' * 100  # max_length = 500
TOO_LONG_NAME = 'too_long_name' * 100
TRUNCATED_TOO_LONG_NAME = TOO_LONG_NAME[0:500]

# work-rules
PARK_DEFAULT_RULE_ID = 'e26a3cf21acfe01198d50030487e046b'
PARK_SELFREG_RULE_ID = '656cbf2ed4e7406fa78ec2107ec9fefe'
UBER_INTEGRATION_RULE_ID = '551dbceed3fc40faa90532307dceffe8'
COMMERCIAL_HIRING_RULE_ID = '9dd42b2db67c4e088df6eb35d6270e58'
COMMERCIAL_HIRING_WITH_CAR_RULE_ID = 'badd1c9d6b6b4e9fb9e0b48367850467'
VEZET_RULE_ID = '3485aa955a484ecc8ce5c6704a52e0af'

RULE_WORK_ITEMS_PREFIX = 'RuleWork:Items:'
RULE_WORK_CALC_TABLE_ITEMS_PREFIX = 'RuleWork:CalcTable:Items:'

BASE_REQUEST_WORK_RULE = {
    'commission_for_subvention_percent': '3.2100',
    'commission_for_workshift_percent': '1.2300',
    'commission_for_driver_fix_percent': '12.3456',
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': True,
    'name': 'Name',
    'type': 'commercial_hiring',
}
BASE_RESPONSE_WORK_RULE = {
    'commission_for_subvention_percent': '0.0000',
    'commission_for_workshift_percent': '0.0000',
    'commission_for_driver_fix_percent': '0.0000',
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': False,
    'is_workshift_enabled': False,
    'name': '',
    'type': 'park',
}
BASE_REQUEST_BODY = {
    'author': BASE_REQUEST_AUTHOR,
    'work_rule': BASE_REQUEST_WORK_RULE,
}

BASE_REDIS_RULE = {
    'CommisisonForSubventionPercent': 3.21,
    'CommissionForDriverFixPercent': 12.3456,
    'DisableDynamicYandexCommission': False,
    'Enable': True,
    'IsDriverFixEnabled': False,
    'Name': 'Name',
    'WorkshiftCommissionPercent': 1.23,
    'WorkshiftsEnabled': True,
    'YandexDisableNullComission': False,
    'YandexDisablePayUserCancelOrder': False,
}
BASE_CALC_TABLE_ENTRY = {
    'commission_fixed': '1.2000',
    'commission_percent': '3.4000',
    'order_type_id': 'extra_super_order_type1',
    'is_enabled': True,
}
BASE_REDIS_CALC_TABLE_ENTRY = {
    'Fix': 1.2000,
    'IsEnabled': True,
    'Percent': 3.4000,
}

BASE_PG_WORK_RULE = {
    'park_id': PARK_ID,
    'idempotency_token': None,
    'commission_for_driver_fix_percent': decimal.Decimal('12.3456'),
    'commission_for_subvention_percent': decimal.Decimal('3.2100'),
    'commission_for_workshift_percent': decimal.Decimal('1.2300'),
    'is_archived': False,
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_default': False,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': True,
    'name': 'Name',
    'type': 'park',
}

WORK_RULE_INSERT_QUERY = (
    'INSERT INTO driver_work_rules.work_rules ('
    'park_id,'
    'id,'
    'idempotency_token,'
    'commission_for_driver_fix_percent,'
    'commission_for_subvention_percent,'
    'commission_for_workshift_percent,'
    'is_commission_if_platform_commission_is_null_enabled,'
    'is_commission_for_orders_cancelled_by_client_enabled,'
    'is_driver_fix_enabled,'
    'is_dynamic_platform_commission_enabled,'
    'is_enabled,'
    'is_workshift_enabled,'
    'name,'
    'type,'
    'created_at,'
    'updated_at'
    ')'
    'VALUES ('
    '\'{}\','
    '\'{}\','
    '\'{}\','
    '3.21,'
    '12.3456,'
    '1.23,'
    'true,'
    'true,'
    'true,'
    'true,'
    'true,'
    'true,'
    '\'Name\','
    '\'park\','
    '\'2019-02-14 11:48:33.644361\','
    '\'2020-02-14 11:48:33.644361\''
    ');'
)

# order-types
RULE_TYPE_ITEMS_KEY = 'RuleType:Items:' + PARK_ID
RULE_TYPE_NAMES_TO_IDS = 'RuleType:ByName:Items:' + PARK_ID
YANDEX = 'af0efd4b0fa9e111a6fc00304879209b'

BASE_REDIS_ORDER_TYPE = {
    'Name': 'Name',
    'Color': 'White',
    'ShowAddress': True,
    'ShowPhone': True,
    'MorningValue': 3,
    'MorningPerroid': 'м',
    'MorningDescription': '1 м',
    'NightValue': -1,
    'NightPerroid': 'скрыть',
    'NightDescription': 'Всегда',
    'WeekendDescription': 'Всегда',
    'AutoCancel': 10,
    'CancelCost': 50.0,
    'WaitingCost': 50.0,
    'LocalizedName': 'Название',
}
BASE_RESPONSE_ORDER_TYPE = {
    'id': 'order_type_1',
    'autocancel_time_in_seconds': 10,
    'driver_cancel_cost': '50.0000',
    'color': 'White',
    'name': 'Name',
    'is_client_address_shown': True,
    'is_client_phone_shown': True,
    'driver_waiting_cost': '50.0000',
    'morning_visibility': {'period': 'м', 'value': 3},
    'night_visibility': {'period': 'скрыть', 'value': -1},
    'weekend_visibility': {'period': '', 'value': 0},
}
