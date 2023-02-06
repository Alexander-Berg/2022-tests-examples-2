import json

USER_ID_PREFIX = 'user'
DEFAULT_PARK_NAME = 'park1'
DEFAULT_PASSPORT_UID = '1'
DEFAULT_GROUP_ID = 'gid1'
DEFAULT_EMAIL = 'default@yandex.ru'
DEFAULT_ENABLE = True

# Generated via `tvmknife unittest service -s 111 -d 2001353`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxDJk3o:NS'
    '1Oifl9430iF8V4az7lQaGQIJzxthJu3lXmYjD'
    '-RISAwnMJMW2nr0clA9rSleKPhCZVQWMipPn_'
    'CXjYOLCb5EbuCkoB45M4uF3EmbSt93-spTKfd'
    'Jp-pjdEyAdJN_2bFpXDW3OEE9cixMGa_4VyoZ'
    'wTrLwKQYJLDqJGmo2Wzpw'
)

SERVICE_TICKET_HEADER = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}

USER_IN_REDIS_JSON = json.loads(
    b'{"Email":"default@yandex.ru",'
    b'"Enable":true,"Group":"gid1",'
    b'"IsSuperUser":false,'
    b'"YandexConfirmed":false,'
    b'"YandexUid":"1"}',
)


def make_redis_user(uid, group=DEFAULT_GROUP_ID):
    return json.dumps(
        {
            'YandexUid': uid,
            'Group': group,
            'Email': DEFAULT_EMAIL,
            'Enable': DEFAULT_ENABLE,
        },
    )


def make_user_without_id(
        park_id=None,
        passport_uid=None,
        group_id=None,
        email=None,
        is_enabled=True,
        is_confirmed=False,
        is_superuser=False,
        is_multifactor_authentication_required=False,
        is_usage_consent_accepted=False,
        display_name=None,
        group_name=None,
):
    user = {
        'park_id': park_id or DEFAULT_PARK_NAME,
        'passport_uid': passport_uid or DEFAULT_PASSPORT_UID,
        'yandex_uid': passport_uid or DEFAULT_PASSPORT_UID,
        'group_id': group_id or DEFAULT_GROUP_ID,
        'email': email or DEFAULT_EMAIL,
        'is_enabled': is_enabled,
        'is_confirmed': is_confirmed,
        'is_multifactor_authentication_required': (
            is_multifactor_authentication_required
        ),
        'is_superuser': is_superuser,
        'is_usage_consent_accepted': is_usage_consent_accepted,
    }
    if display_name:
        user['display_name'] = display_name
    if group_name:
        user['group_name'] = group_name
    return user


def make_user(
        id_,
        park_id=DEFAULT_PARK_NAME,
        passport_uid=None,
        is_enabled=True,
        is_confirmed=False,
        is_superuser=False,
        is_multifactor_auth_required=False,
        is_usage_consent_accepted=False,
        display_name=None,
        group_id=None,
        group_name=None,
):
    uid = passport_uid or str(id_)
    usr = make_user_without_id(
        park_id=park_id,
        passport_uid=uid,
        is_enabled=is_enabled,
        is_confirmed=is_confirmed,
        is_superuser=is_superuser,
        is_multifactor_authentication_required=is_multifactor_auth_required,
        is_usage_consent_accepted=is_usage_consent_accepted,
        display_name=display_name,
        group_id=group_id,
        group_name=group_name,
    )
    usr['id'] = USER_ID_PREFIX + str(id_)
    return usr


def make_users(
        id_list,
        park_id=DEFAULT_PARK_NAME,
        passport_uid=None,
        is_enabled=True,
        is_confirmed=False,
        is_superuser=False,
        is_multifactor_authentication_required=False,
        is_usage_consent_accepted=False,
):
    return [
        make_user(
            id_,
            park_id,
            passport_uid,
            is_enabled,
            is_confirmed,
            is_superuser,
            is_multifactor_authentication_required,
            is_usage_consent_accepted,
        )
        for id_ in id_list
    ]


GRANTS = [
    'orders',
    'fines',
    'news',
    'support',
    'drivers_messages',
    'tariffs',
    'payments_groups',
    'settings',
    'service_pay_system',
    'report_cash',
    'reports',
    'driver_read_common',
    'driver_write_common',
    'driver_add_money',
    'driver_withdraw_money',
    'driver_scoring_read',
    'driver_scoring_buy',
    'car_read_common',
    'car_write_common',
    'users',
    'users_grants',
    'cashbox',
    'api',
    'park_contacts_read',
    'park_contacts_write',
    'segments',
    'legal_entities',
    'gas',
    'map',
    'support_chat_read',
    'support_chat_write',
    'recurring_payments_read',
    'recurring_payments_write',
    'work_rules_write',
    'report_orders_download',
    'report_orders_moderation',
    'report_payouts',
    'report_quality',
    'report_summary',
    'report_summary_download',
    'segments_download',
    'aggregator',
    'billing',
    'cars_list_download',
    'dashboard_read_common',
    'drivers_list_download',
    'finance_statements_read',
    'finance_statements_run',
    'finance_statements_write',
    'instant_payouts_read',
    'report_cash_download',
    'report_orders',
]

GRANTS_MARKETPLACE = ['read_company_postings']


def make_grant(grant, enabled=None):
    grant = {'id': grant}
    if enabled is not None:
        grant['enabled'] = enabled
    return grant


PERMISSION_ID = 'permission_1'


def build_config_permission(
        permission_id=PERMISSION_ID,
        enabled_for='all',
        required_permissions=None,
        is_internal=False,
        filters=None,
):
    permission_params = {
        'description': 'test',
        'enabled_for': enabled_for,
        'is_internal': is_internal,
    }
    if required_permissions:
        permission_params['required_permissions'] = required_permissions
    if filters:
        permission_params['filters'] = filters

    return {permission_id: permission_params}
