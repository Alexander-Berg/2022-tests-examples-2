INSERT INTO multioffer.multioffers (updated_at, id, created_at, order_id, settings)
    VALUES (NOW(), '72bcbde8-eaed-460f-8f88-eeb4e056c316', NOW(), '123', '{"offer_timeout": 15, "play_timeout": 12, "multioffer_timeout": 30}'::jsonb);

INSERT INTO multioffer.multioffers (updated_at, id, created_at, order_id, settings)
    VALUES (NOW(), '72bcbde8-eaed-460f-8f88-eeb4e056c317', NOW(), '321', '{"offer_timeout": 15, "play_timeout": 12, "multioffer_timeout": 30}'::jsonb);

INSERT INTO multioffer.multioffers (updated_at, id, created_at, order_id, settings)
    VALUES (NOW(), '72bcbde8-eaed-460f-8f88-eeb4e056c318', NOW(), '987', '{"offer_timeout": 15, "play_timeout": 12, "multioffer_timeout": 30}'::jsonb);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, enriched_json)
    VALUES ('72bcbde8-eaed-460f-8f88-eeb4e056c316', 'win'::multioffer.offer_status, 'park_id', 'driver_profile_id_1', 0, 'alias_id', '{
          "in_extended_radius": false,
          "route_info": {
            "time": 60,
            "distance": 60
          },
          "classes": [
            "ultima",
            "awesome"
          ],
          "position": [
            37.568388,
            55.784362
          ],
          "chain_info": {
            "destination": [
              39.207141,
              51.662082
            ],
            "left_time": 99,
            "left_dist": 500,
            "order_id": "f3ae2a04966035119c3ea83c8d0197ae"
          }
        }'::jsonb,  '{
          "in_extended_radius": false,
          "some_field": "some_value"
        }'::jsonb),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c316', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id_6', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 300,
            "distance": 2523,
            "approximate": false,
            "properties": {
              "toll_roads": false
            }
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb, '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, enriched_json)
    VALUES ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id_2', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 300,
            "distance": 2523,
            "approximate": false,
            "properties": {
              "toll_roads": false
            }
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id_3', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 90,
            "distance": 250
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'lose'::multioffer.offer_status, 'park_id', 'driver_profile_id_4', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 150,
            "distance": 1000
          },
          "classes": [
            "ultima",
            "awesome"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c317', 'declined'::multioffer.offer_status, 'park_id', 'driver_profile_id_5', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 50,
            "distance": 100
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, enriched_json, auction)
    VALUES ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'sent'::multioffer.offer_status, 'park_id', 'driver_profile_id_7', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 300,
            "distance": 2523,
            "approximate": false,
            "properties": {
              "toll_roads": false
            }
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb, '{
            "iteration": 1
        }'),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'accepted'::multioffer.offer_status, 'park_id', 'driver_profile_id_8', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 90,
            "distance": 250
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb, '{
            "iteration": 1
        }'),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'lose'::multioffer.offer_status, 'park_id', 'driver_profile_id_9', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 150,
            "distance": 1000
          },
          "classes": [
            "ultima",
            "awesome"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb, '{
            "iteration": 2
        }'),
        ('72bcbde8-eaed-460f-8f88-eeb4e056c318', 'declined'::multioffer.offer_status, 'park_id', 'driver_profile_id_10', 0, 'alias_id', '{
          "in_extended_radius": true,
          "route_info": {
            "time": 50,
            "distance": 100
          },
          "classes": [
            "ultima",
            "vip"
          ]
        }'::jsonb,  '{
          "in_extended_radius": true,
          "some_field": "some_value"
        }'::jsonb, '{
            "iteration": 1
        }');

