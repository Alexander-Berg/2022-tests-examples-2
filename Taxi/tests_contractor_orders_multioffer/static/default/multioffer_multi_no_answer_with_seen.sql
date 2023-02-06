INSERT INTO multioffer.multioffers (id, order_id, lookup_request)
    VALUES ('41234567-89ab-cdef-0123-456789abcdef', 'order_id_4', '{"lookup":{"generation": 1, "version": 1, "wave": 1}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, seen_data)
    VALUES ('41234567-89ab-cdef-0123-456789abcdef', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', '{}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, seen_data)
    VALUES ('41234567-89ab-cdef-0123-456789abcdef', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 0, 'alias_id2', '{}', '{}');

