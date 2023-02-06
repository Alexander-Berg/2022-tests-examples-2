INSERT INTO multioffer.multioffers (id, order_id, lookup_request)
    VALUES ('21234567-89ab-cdef-0123-456789abcdef', 'order_id_2', '{"lookup":{"generation": 1, "version": 1, "wave": 1}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('21234567-89ab-cdef-0123-456789abcdef', 'declined'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', FALSE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('21234567-89ab-cdef-0123-456789abcdef', 'declined'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 0, 'alias_id2', '{}', FALSE);

