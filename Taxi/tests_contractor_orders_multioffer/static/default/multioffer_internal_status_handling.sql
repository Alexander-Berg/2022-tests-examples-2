INSERT INTO multioffer.multioffers (updated_at, id, created_at, order_id, auction, settings) 
    VALUES (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c316', now(), '123', null, '{}'),
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c317', now(), '124', '{"iteration": 1, "auction_type": "auction", "min_price": 1000, "max_price": 3000}', '{}'),
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c318', now(), '125', '{"iteration": 1, "auction_type": "auction", "min_price": 1000, "max_price": 3000}', '{}');

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json) 
    VALUES('72bcbde8-eaed-460f-8f88-eeb4e056c316', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id', 0, 'alias_id', '{}'), 
          ('72bcbde8-eaed-460f-8f88-eeb4e056c316', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id_9', 0, 'alias_id', '{}'),
          ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id', 0, 'alias_id', '{}'),
          ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id_9', 0, 'alias_id', '{}'),
          ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id', 0, 'alias_id', '{}'),
          ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id_9', 0, 'alias_id', '{}');

INSERT INTO multioffer.multioffer_bids (id, multioffer_id, park_id, driver_profile_id, status, reason, updated_at, price)
    VALUES('0be9a612-83f8-4f52-b585-16085c20299d', '72bcbde8-eaed-460f-8f88-eeb4e056c317', 'park_id', 'driver_profile_id', 'created'::multioffer.bid_status, null, now(), 1500),
          ('0be9a612-83f8-4f52-b585-16085c20399d', '72bcbde8-eaed-460f-8f88-eeb4e056c317', 'park_id', 'driver_profile_id_9', 'created'::multioffer.bid_status, null, now(), 1600);
