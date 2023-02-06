INSERT INTO shard0.activity_events_unsent(id,event_at,activity_event) VALUES
(
    1,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid1",
        "dbid": "12345",
        "udid": "udid1",
        "activities": [
            {
                "status": "free",
                "geoareas": ["zone1"],
                "end": "2020-01-01T09:00:10+00:00",
                "start": "2020-01-01T09:00:00+00:00",
                "tags": ["fixer"],
                "activity_points": 99.0,
                "available_tariff_classes": ["econom", "vip"],
                "profile_payment_type_restrictions": "none"
            }
        ],
        "end": "2019-10-11T10:39:00+00:00",
        "start": "2020-01-01T09:00:00+00:00",
        "rule_types": ["driver_fix"]
    }'
);
