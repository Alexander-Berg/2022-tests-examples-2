INSERT INTO multioffer.multioffers (id, order_id, lookup_request, status, updated_at)
    VALUES ('61234567-89ab-cdef-0123-456789abcdef', 'order_id_6', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', 'completed', '2022-02-08 12:00:00.000000+03');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer, winner_driving)
    VALUES ('61234567-89ab-cdef-0123-456789abcdef', 'win'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', TRUE, TRUE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('61234567-89ab-cdef-0123-456789abcdef', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 10, 'alias_id2', '{}', TRUE);

INSERT INTO multioffer.multioffers (id, order_id, lookup_request, status, updated_at)
    VALUES ('61234567-89ab-cdef-0123-456789abcdec', 'order_id_6', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', 'completed', '2022-02-08 12:00:00.000000+03');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer, winner_driving)
    VALUES ('61234567-89ab-cdef-0123-456789abcdec', 'win'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', TRUE, FALSE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('61234567-89ab-cdef-0123-456789abcdec', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 10, 'alias_id2', '{}', TRUE);

INSERT INTO multioffer.multioffers (id, order_id, lookup_request, status, updated_at)
    VALUES ('61234567-89ab-cdef-0123-456789abcdeb', 'order_id_6', '{"lookup":{"generation": 1, "version": 1, "wave": 3}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', 'in_progress', '2022-02-08 12:00:00.000000+03');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('61234567-89ab-cdef-0123-456789abcdeb', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{}', TRUE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('61234567-89ab-cdef-0123-456789abcdeb', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 10, 'alias_id2', '{}', TRUE);
