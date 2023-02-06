INSERT INTO multioffer.multioffers (updated_at, id, created_at, order_id, lookup_request, settings, auction)
    VALUES (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c316', now(), '123', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}}', '{"is_auction": false}'::jsonb, null),
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c319', now(), '123', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}, "order": {"nearest_zone": "moscow"}}', '{"dispatch_type": "auction", "is_auction": true, "max_waves": 10}'::jsonb,
            '{
                "iteration": 1,
                "auction_type": "auction",
                "min_price": 1000,
                "max_price": 3000
            }'::jsonb),
           (now(), '72bcbde8-eaed-460f-8f88-eeb4e056c317', now(), '456', '{"lookup":{"generation": 1, "version": 1, "wave": 2}, "callback":{"url": "some_url", "timeout_ms": 500, "attempts": 2}, "order": {"nearest_zone": "moscow"}}', '{"dispatch_type": "auction", "is_auction": true, "max_waves": 10}'::jsonb,
            '{
                "iteration": 1,
                "auction_type": "auction",
                "min_price": 1000,
                "max_price": 3000
            }'::jsonb);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, answer, park_id, driver_profile_id, score, alias_id, candidate_json, enriched_json, auction)
    VALUES ('72bcbde8-eaed-460f-8f88-eeb4e056c316', 'sent'::multioffer.offer_status, null , 'park_id', 'driver_profile_id_1', 0, 'alias_id_1', '{}', '{}', null),
           ('72bcbde8-eaed-460f-8f88-eeb4e056c319', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_1', 0, 'alias_id_1', '{}',
            '{
                "name": "Иванов Иван Иванович",
                "unique_driver_id": "60c9ccf18fe28d5ce431ce88",
                "license_id": "318fb895466a4cd599486ada5c5c0ffa",
                "driver_license": "OXO000473",
                "car": {
                    "color": "зеленый",
                    "model": "Audi A6",
                    "dbcar_id": "e14bf78adb2943d398bca593cb0a8200",
                    "raw_color": "Зеленый",
                    "color_code": "007F00"
                },
                "tags": [
                    "some_tag"
                ],
                "classes": [
                    "econom"
                ],
                "route_info": {
                    "time": 225,
                    "distance": 1935,
                    "properties": {
                    "toll_roads": false
                    },
                    "approximate": false
                },
                "chain_info": {
                    "order_id": "7835cd0325ab2f2dabf7933e2d680a25",
                    "left_dist": 767,
                    "left_time": 129,
                    "destination": [
                    48.5748790393024,
                    54.38051404037958
                    ]
                }
            }',
            '{
                "iteration": 0,
                "driver_bid_info": {
                    "min_price": 1000,
                    "max_price": 3000
                }
            }'::jsonb),
           ('72bcbde8-eaed-460f-8f88-eeb4e056c319', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_2', 1, 'alias_id_2', '{}', '{}',
            '{
                "iteration": 0,
                "driver_bid_info": {
                    "min_price": 1000,
                    "max_price": 3000
                }
            }'::jsonb),
           ('72bcbde8-eaed-460f-8f88-eeb4e056c319', 'declined'::multioffer.offer_status, false , 'park_id', 'driver_profile_id_3', 2, 'alias_id_3', '{}', '{}',
            '{
                "iteration": 0,
                "driver_bid_info": {
                    "min_price": 1000,
                    "max_price": 3000
                }
            }'::jsonb),
           ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'sent'::multioffer.offer_status, null, 'park_id', 'driver_profile_id_1', 0, 'alias_id_1', 
            '{
                "uuid": "driver_profile_id_1",
                 "unique_driver_id": "uniq_id_1",
                "car_number": "car_number_1"
            }', 
            '{
                "name": "Иванов Иван Иванович",
                "unique_driver_id": "60c9ccf18fe28d5ce431ce88",
                "license_id": "318fb895466a4cd599486ada5c5c0ffa",
                "driver_license": "OXO000473",
                "car": {
                    "color": "зеленый",
                    "model": "Audi A6",
                    "dbcar_id": "e14bf78adb2943d398bca593cb0a8200",
                    "raw_color": "Зеленый",
                    "color_code": "007F00"
                },
                "tags": [
                    "some_tag"
                ],
                "classes": [
                    "econom"
                ],
                "route_info": {
                    "time": 225,
                    "distance": 1935,
                    "properties": {
                    "toll_roads": false
                    },
                    "approximate": false
                },
                "chain_info": {
                    "order_id": "7835cd0325ab2f2dabf7933e2d680a25",
                    "left_dist": 767,
                    "left_time": 129,
                    "destination": [
                    48.5748790393024,
                    54.38051404037958
                    ]
                }
            }',
            '{
                "iteration": 1,
                "driver_bid_info": {
                    "min_price": 1000,
                    "max_price": 3000
                }
            }'::jsonb),
           ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'accepted'::multioffer.offer_status, true, 'park_id', 'driver_profile_id_2', 1, 'alias_id_2', '{
               "uuid": "driver_profile_id_2",
               "unique_driver_id": "uniq_id_2"
           }', '{}', null);
