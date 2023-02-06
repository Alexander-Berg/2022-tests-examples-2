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
        "rule_types": ["geo_booking"]
    }'
),
(
    2,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid2",
        "dbid": "12345",
        "udid": "udid2",
        "activities": [
            {
                "status": "free",
                "geoareas": ["zone1"],
                "end": "2020-01-01T09:00:10+00:00",
                "start": "2020-01-01T09:00:00+00:00",
                "activity_points": 99.0,
                "available_tariff_classes": ["econom", "vip"],
                "profile_payment_type_restrictions": "none",
                "tags": ["fixer"]
            }
        ],
        "end": "2019-10-11T10:39:00+00:00",
        "start": "2020-01-01T09:00:00+00:00",
        "rule_types": ["geo_booking"]
    }'
);

INSERT INTO shard1.activity_events_unsent(id,event_at,activity_event) VALUES
(
    1,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid3",
        "dbid": "12345_67890",
        "udid": "udid3",
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
        "rule_types": ["geo_booking"]
    }'
);

INSERT INTO shard2.activity_events_unsent(id,event_at,activity_event) VALUES
(
    1,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid4",
        "dbid": "12345_67890",
        "udid": "udid4",
        "activities": [
            {
                "status": "free",
                "geoareas": ["zone1"],
                "end": "2020-01-01T09:00:10+00:00",
                "start": "2020-01-01T09:00:00+00:00",
                "tags": ["fixer"],
                "activity_points": 100.0,
                "available_tariff_classes": ["econom", "vip"],
                "profile_payment_type_restrictions": "none"
            }
        ],
        "end": "2019-10-11T10:39:00+00:00",
        "start": "2020-01-01T09:00:00+00:00",
        "profile_payment_type_restrictions": "none",
        "rule_types": ["geo_booking"]
    }'
);
