INSERT INTO offers.offers (offer_id, created, due, tag, params, payload)
VALUES (
            'offer_id_one',
            '2020-04-20 15:00:00.000000+03',
            '2020-04-20 15:30:00.000000+03',
            'offer_tag_one',
            '{"place_id": "place_id_one"}',
            '{"payload": "i am a payload!"}'
       );

INSERT INTO offers.offers (offer_id, created, due, tag, params, payload)
VALUES (
           'offer_id_one_old',
           '2020-04-20 14:00:00.000000+03',
           '2020-04-20 14:30:00.000000+03',
           'offer_tag_one',
           '{"place_id": "place_id_one"}',
           '{"payload": "i am an old payload!"}'
       );

INSERT INTO offers.offers (offer_id, created, due, tag, params, payload)
VALUES (
           'offer_id_expired',
           '2020-04-19 15:00:00.000000+03',
           '2020-04-19 15:30:00.000000+03',
           'offer_tag_expired',
           '{"place_id": "place_id_expired"}',
           '{"payload": "i am a payload!"}'
       );

INSERT INTO offers.offers (offer_id, created, due, tag, params, payload)
VALUES (
           'offer_id_three',
           '2020-04-20 15:00:00.000000+03',
           '2020-04-20 15:30:00.000000+03',
           'offer_tag_three',
           '{"place_id": "place_id_three"}',
           '{"payload": "i am a payload three!"}'
       );

INSERT INTO offers.offers (offer_id, created, due, tag, params, payload)
VALUES (
           'offer_id_three_old',
           '2020-04-20 14:00:00.000000+03',
           '2020-04-20 14:30:00.000000+03',
           'offer_tag_three',
           '{"place_id": "place_id_three"}',
           '{"payload": "i am an old payload three!"}'
       );
