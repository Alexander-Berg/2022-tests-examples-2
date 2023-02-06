UPDATE multioffer.multioffer_drivers
SET offer_status = 'accepted'::multioffer.offer_status,
    answer = TRUE,
    answer_sent_at = '2022-05-30T11:59:59.000000Z'
WHERE multioffer_id = '72bcbde8-eaed-460f-8f88-eeb4e056c317'
  AND driver_profile_id = ANY(ARRAY['driver_profile_id_1', 'driver_profile_id_2']);

INSERT INTO multioffer.multioffer_bids (id, multioffer_id, status, park_id, driver_profile_id, price, auction)
    VALUES ('b5d8c6fa-c891-4306-924f-0db1c217eb28', '72bcbde8-eaed-460f-8f88-eeb4e056c317', 'created', 'park_id', 'driver_profile_id_2', 1000, 
            '{
                "iteration": 1,
                "auction_type": "auction",
                "min_price": 1000,
                "max_price": 3000
            }'::jsonb),
            ('0be9a613-83f8-4f52-b585-16085c20299d', '72bcbde8-eaed-460f-8f88-eeb4e056c317', 'rejected', 'park_id', 'driver_profile_id_1', 1500, 
            '{
                "iteration": 1,
                "auction_type": "auction",
                "min_price": 1000,
                "max_price": 3000
            }'::jsonb),
           ('0be9a612-83f8-4f52-b585-16085c20299d', '72bcbde8-eaed-460f-8f88-eeb4e056c317', 'created', 'park_id', 'driver_profile_id_1', 1000, 
            '{
                "iteration": 1,
                "auction_type": "auction",
                "min_price": 1000,
                "max_price": 3000
            }'::jsonb);
