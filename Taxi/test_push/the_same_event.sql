INSERT INTO bte.payloads (aggregation_key, payload)
VALUES ('7877083c797c386ca7c73349d40c962c', '{
        "activity_points": 93.0,
        "available_tariff_classes": [
          "econom",
          "express",
          "uberx"
        ],
        "geoareas": [
          "moscow_center"
        ],
        "profile_payment_type_restrictions": "none",
        "status": "free",
        "tags": [
          "high_activity",
          "park_test_1",
          "some_tag"
        ],
        "unique_driver_id": "5e53a07da11531e403a96a66",
        "clid": "100500"
      }');

INSERT INTO bte.events (amount, driver_id, event_ref, event_at, aggregation_key)
VALUES (
    '60 seconds',
    '7ad36bc7560449998acbe2c57a75c293_16f2b3c714a6ef8724e9226390910626',
    '1234567890123456',
    '2020-06-02 18:44:00+00:00',
    '7877083c797c386ca7c73349d40c962c'
    );
