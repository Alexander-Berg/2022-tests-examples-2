INSERT INTO fleet_customers.customers (
    id,
    park_id,
    personal_phone_id,
    name,
    created_at,
    sms_enabled,
    invoice_enabled,
    comment
) VALUES (
    'existing_customer_id',
    'park_id',
    'existing_personal_phone_id',
    'existing_name',
    '2022-01-01T00:00:00+00:00',
    true,
    true,
    NULL
), (
    'existing_customer_id1',
    'park_id',
    'existing_personal_phone_id1',
    'existing_name1',
    '2022-01-01T00:00:00+00:00',
    true,
    true,
    NULL
), (
    'existing_customer_id2',
    'park_id',
    'existing_personal_phone_id2',
    NULL,
    '2022-01-01T00:00:00+00:00',
    true,
    true,
    NULL
), (
    'deleted_customer_id',
    'park_id',
    NULL,
    NULL,
    '2022-01-01T00:00:00+00:00',
    true,
    true,
    NULL
), (
    'customer_id_other_park',
    'other_park_id',
    'personal_phone_id_other_park',
    'name_other_park',
    '2022-01-01T00:00:00+00:00',
    true,
    true,
    'comment'
)
;
