INSERT INTO multioffer.multioffers (id, order_id, lookup_request, status)
    VALUES ('66234567-89ab-cdef-0123-456789abcdef', 'order_id_66', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', 'completed');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('66234567-89ab-cdef-0123-456789abcdef', 'win'::multioffer.offer_status, 'park_id', 'driver_profile_id1', 0, 'alias_id1', '{"candidate_id":"won_candidate"}', TRUE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('66234567-89ab-cdef-0123-456789abcdef', 'lose'::multioffer.offer_status, 'park_id', 'driver_profile_id2', 10, 'alias_id2', '{}', TRUE);

