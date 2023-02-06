CALL bte.insert_event(
        'event_ref',
        '2020-01-01 00:00+00'::timestamptz,
        '2020-01-01 00:00+00'::timestamptz,
        'db_id_uuid',
        '1M'::interval,
        '{
            "status": "free",
            "geoareas": ["msk"],
            "available_tariff_classes": ["econom", "comfort"],
            "tags": ["df"],
            "profile_payment_type_restrictions": "none",
            "activity_points": 95,
            "unique_driver_id": "33550336",
            "clid": "8128"
        }'
    );
CALL bte.insert_event(
        'event_ref',
        '2020-01-01 00:01+00'::timestamptz,
        '2020-01-01 00:01+00'::timestamptz,
        'db_id_uuid',
        '1M'::interval,
        '{
            "status": "free",
            "geoareas": ["msk"],
            "available_tariff_classes": ["econom", "comfort"],
            "tags": ["df"],
            "profile_payment_type_restrictions": "none",
            "activity_points": 95,
            "unique_driver_id": "33550336",
            "clid": "8128"
        }'
    );
