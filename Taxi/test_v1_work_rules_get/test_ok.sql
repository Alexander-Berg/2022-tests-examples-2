/* 'park_id': 'extra_super_park_id' */
INSERT INTO driver_work_rules.work_rules (
    park_id,
    id,
    idempotency_token,
    commission_for_driver_fix_percent,
    commission_for_subvention_percent,
    commission_for_workshift_percent,
    is_commission_if_platform_commission_is_null_enabled,
    is_commission_for_orders_cancelled_by_client_enabled,
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
    'extra_super_park_id',
    'extra_super_work_rule_id1',
    NULL,
    12.3456,
    3.21,
    1.23,
    true,
    true,
    false,
    true,
    true,
    true,
    'Name',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
    'extra_super_park_id',
    'extra_super_work_rule_id2',
    NULL,
    12.3456,
    3.21,
    1.23,
    true,
    true,
    false,
    true,
    true,
    true,
    'Name',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
    'extra_super_park_id',
    '656cbf2ed4e7406fa78ec2107ec9fefe', /* 'type': 'park', 'subtype': 'selfreg' */
    NULL,
    12.3456,
    3.21,
    1.23,
    true,
    true,
    false,
    true,
    true,
    true,
    'Name',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
);

/* 'park_id': 'extra_super_park_id2' */
INSERT INTO driver_work_rules.work_rules (
    park_id,
    id,
    idempotency_token,
    commission_for_driver_fix_percent,
    commission_for_subvention_percent,
    commission_for_workshift_percent,
    is_commission_if_platform_commission_is_null_enabled,
    is_commission_for_orders_cancelled_by_client_enabled,
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
    'extra_super_park_id2',
    '656cbf2ed4e7406fa78ec2107ec9fefe', /* 'type': 'park', 'subtype': 'selfreg' */
    NULL,
    12.3456,
    3.21,
    1.23,
    true,
    true,
    false,
    true,
    true,
    true,
    'Name',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
);
