INSERT INTO cache.offers_loads (user_id, table_name, yql_link, yql_share_link)
VALUES ('user2', '2021-09-21', 'link2', 'sharelink2'),
       ('user2', '2021-09-22', 'link3', 'sharelink3'),
       ('user3', '2021-09-22', NULL, 'sharelink4'),
       ('user3', '2021-09-23', NULL, 'sharelink5'),
       ('user1', '2021-09-21', NULL, 'sharelink6');

INSERT INTO cache.user_offers (offer_id, user_id, table_name, offer_data)
VALUES ('offer1', 'user3', '2021-09-22', '{}'),
       ('offer2', 'user3', '2021-09-22', '{}'),
       ('offer3', 'user3', '2021-09-23', '{}'),
       ('offer4', 'user1', '2021-09-20', '{}'),
       ('offer5', 'user3', '2021-09-22', '{}');

INSERT INTO cache.offers_details (
                                  offer_id, category, dynamic_checked,
                                  yql_link, yql_share_link, prepare_link
                                )
VALUES (
           'offer3', 'econom', true, 'pricing_link3', 'sharelink3', 'prepare3'
       ),
       (
           'offer4', 'econom', true, null, 'sharelink4', 'prepare4'
       ),
       (
           'offer5', 'econom', false, null, null, 'prepare5'
       );
