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
        "rule_types": ["shuttle"]
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
                "geoareas": ["zone2"],
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
        "rule_types": ["driver_fix"]
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
                "geoareas": ["zone2"],
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
        "rule_types": ["geo_booking"]
    }'
),
(
    2,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid5",
        "dbid": "12345_67890",
        "udid": "udid5",
        "activities": [
            {
                "status": "free",
                "geoareas": ["zone2"],
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
        "rule_types": ["geo_booking", "driver_fix"]
    }'
),
(
    3,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid6",
        "dbid": "12345_67890",
        "udid": "udid6",
        "activities": [
            {
                "status": "free",
                "geoareas": [],
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
        "rule_types": ["driver_fix"]
    }'
),
(
    4,
    '2020-01-01 12:00:00.000000+03',
    '{
        "clid": "clid1",
        "uuid": "uuid7",
        "dbid": "12345_67890",
        "udid": "udid7",
        "activities": [
            {
                "status": "free",
                "geoareas": [],
                "end": "2020-01-01T09:00:10+00:00",
                "start": "2020-01-01T09:00:00+00:00",
                "tags": ["fixer"],
                "activity_points": 100.0,
                "available_tariff_classes": ["econom", "vip"],
                "profile_payment_type_restrictions": "none"
            }
        ],
        "end": "2019-10-11T10:39:00+00:00",
        "start": "2020-01-01T09:00:00+00:00"
    }'
);
