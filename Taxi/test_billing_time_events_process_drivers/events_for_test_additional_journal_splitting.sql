CALL bte.insert_event(
    'event_ref_1',
    '2020-06-30 10:58+00'::timestamptz,
    '2020-06-30 09:58+00'::timestamptz,
    'dbid_uuid1',
    '1M'::interval,
    '{
        "status": "free",
        "geoareas": ["mkad"],
        "available_tariff_classes": ["comfort"],
        "tags": ["tag1", "tag2"],
        "profile_payment_type_restrictions": "cash",
        "activity_points": 95,
        "unique_driver_id": "8589869056",
        "clid": "8128"
    }'
);
CALL bte.insert_event(
    'event_ref_1',
    '2020-06-30 10:59+00'::timestamptz,
    '2020-06-30 09:59+00'::timestamptz,
    'dbid_uuid1',
    '1M'::interval,
    '{
        "status": "free",
        "geoareas": ["mkad"],
        "available_tariff_classes": ["comfort"],
        "tags": ["tag1", "tag2"],
        "profile_payment_type_restrictions": "cash",
        "activity_points": 95,
        "unique_driver_id": "8589869056",
        "clid": "8128"
    }'
);
CALL bte.insert_event(
    'event_ref_1',
    '2020-06-30 11:00+00'::timestamptz,
    '2020-06-30 10:00+00'::timestamptz,
    'dbid_uuid1',
    '1M'::interval,
    '{
        "status": "free",
        "geoareas": ["mkad"],
        "available_tariff_classes": ["comfort"],
        "tags": ["tag1", "tag2"],
        "profile_payment_type_restrictions": "cash",
        "activity_points": 95,
        "unique_driver_id": "8589869056",
        "clid": "8128"
    }'
);
