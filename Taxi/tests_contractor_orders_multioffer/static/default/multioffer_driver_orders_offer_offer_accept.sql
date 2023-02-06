INSERT INTO multioffer.multioffers (updated_at, id, created_at, order_id, lookup_request, auction) 
    VALUES (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c316', now(), '123', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', null),
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c319', now(), '123', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', null), 
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c317', now(), '456', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', null),
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c318', now(), '124', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', '{"iteration": 1, "auction_type": "auction", "min_price": 1000, "max_price": 3000}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, answer, park_id, driver_profile_id, score, alias_id, candidate_json)
    VALUES('72bcbde8-eaed-460f-8f88-eeb4e056c316', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_1', 0, 'alias_id', '{}'), 
          ('72bcbde8-eaed-460f-8f88-eeb4e056c319', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_1', 0, 'alias_id', '{}'), 
          ('72bcbde8-eaed-460f-8f88-eeb4e056c319', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_2', 1, 'alias_id', '{}'), 
          ('72bcbde8-eaed-460f-8f88-eeb4e056c319', 'declined'::multioffer.offer_status, false, 'park_id', 'driver_profile_id_3', 2, 'alias_id', '{}'), 
          ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_1', 0, 'alias_id', '{}'), 
          ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'accepted'::multioffer.offer_status, true, 'park_id', 'driver_profile_id_2', 1, 'alias_id', '{}'),
          ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_1', 0, 'alias_id', '{}'),
          ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_9', 0, 'alias_id', '{}');
