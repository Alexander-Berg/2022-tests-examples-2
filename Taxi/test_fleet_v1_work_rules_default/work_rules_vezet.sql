INSERT INTO driver_work_rules.work_rules (
    park_id,
    id,
    idempotency_token,
    commission_for_driver_fix_percent,
    commission_for_subvention_percent,
    commission_for_workshift_percent,
    is_archived,
    is_commission_if_platform_commission_is_null_enabled,
    is_commission_for_orders_cancelled_by_client_enabled,
    is_default,
    is_driver_fix_enabled,
    is_dynamic_platform_commission_enabled,
    is_enabled,
    is_workshift_enabled,
    name,
    type,
    created_at,
    updated_at
)
VALUES
(
    'park_with_default_rule',
    'work_rule_id_default',
    NULL,
    12.3456,
    3.21,
    1.23,
    false,
    true,
    true,
    true,
    false,
    true,
    true,
    true,
    'Name',
    'vezet',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
);