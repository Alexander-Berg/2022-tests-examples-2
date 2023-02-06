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
    'work_rule_1',
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
    'e26a3cf21acfe01198d50030487e046b', /* 'type': 'park', 'subtype': 'default' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    '',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
    'extra_super_park_id',
    '656cbf2ed4e7406fa78ec2107ec9fefe', /* 'type': 'park', 'subtype': 'selfreg' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    '',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
   'extra_super_park_id',
   '551dbceed3fc40faa90532307dceffe8', /* 'type': 'park', 'subtype': 'uber_integration' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    '',
    'park',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
   'extra_super_park_id',
   '3485aa955a484ecc8ce5c6704a52e0af', /* 'type': 'vezet', 'subtype': 'default' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    '',
    'vezet',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
   'extra_super_park_id',
   '9dd42b2db67c4e088df6eb35d6270e58', /* 'type': 'commercial_hiring', 'subtype': 'default' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    'abcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcdeabcde',
    'commercial_hiring',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
), (
   'extra_super_park_id',
   'badd1c9d6b6b4e9fb9e0b48367850467', /* 'type': 'commercial_hiring_with_car', 'subtype': 'default' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    'too_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nametoo_long_nam',
    'commercial_hiring_with_car',
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
    '3485aa955a484ecc8ce5c6704a52e0af', /* 'type': 'vezet', 'subtype': 'default' */
    NULL,
    0.0,
    0.0,
    0.0,
    true,
    true,
    false,
    true,
    false,
    false,
    '',
    'vezet',
    '2019-02-14 11:48:33.644361',
    '2020-02-14 11:48:33.644361'
)
