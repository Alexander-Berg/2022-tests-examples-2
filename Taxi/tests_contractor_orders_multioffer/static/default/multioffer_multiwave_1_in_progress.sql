INSERT INTO multioffer.multioffers (id, order_id, status, lookup_request, settings)
    VALUES ('ecc6dc92-6d56-48a3-884d-f31390cd9a3c', 'order_id', 'in_progress'::multioffer.multioffer_status, '{"lookup":{"generation": 1, "version": 1, "wave": 1}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}, "order": {"nearest_zone": "moscow"}}', '{"dispatch_type": "test_multioffer", "max_waves": 2}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('ecc6dc92-6d56-48a3-884d-f31390cd9a3c', 'declined'::multioffer.offer_status, '7f74df331eb04ad78bc2ff25ff88a8f2', '4bb5a0018d9641c681c1a854b21ec9ab', 0, 'alias_id1', '{}', FALSE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('ecc6dc92-6d56-48a3-884d-f31390cd9a3c', 'sent'::multioffer.offer_status, 'a3608f8f7ee84e0b9c21862beef7e48d', 'e26e1734d70b46edabe993f515eda54e', 1, 'alias_id2', '{}', NULL);

