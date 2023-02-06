INSERT INTO eats_restapp_marketing.advert
(updated_at, place_id, averagecpc, campaign_id, group_id, ad_id, banner_id, content_id,
is_active, passport_id, strategy_type)
VALUES (NOW(), 1, 10000000, 1, 1, 1, 1, 1, true, 1, 'average_cpc'),
       (NOW(), 2, 10000000, 2, 2, 2, 2, 2, true, 1, 'average_cpc'),
       (NOW(), 3, 10000000, 3, 3, 3, 3, 3, true, 1, 'average_cpc'),

       (NOW(), 4, 10000000, 1, 1, 1, 1, 1, true, 2, 'average_cpc'),
       (NOW(), 5, 10000000, 2, 2, 2, 2, 2, true, 2, 'average_cpc'),
       (NOW(), 6, 10000000, 3, 3, 3, 3, 3, true, 2, 'average_cpc');

INSERT INTO eats_restapp_marketing.balance
    (advert_id, status, sending_time, next_request_time)
VALUES (1,'high_balance', NULL, NOW() - interval '1 day'),
       (2,'zero_balance', NULL, NOW() - interval '1 day'),
       (3,'zero_balance', NOW() + interval '1 day', NOW() - interval '1 day'),

       (4,'high_balance', NULL, NOW() - interval '1 day'),
       (5,'zero_balance', NOW() + interval '1 day', NOW() - interval '1 day'),
       (6,'zero_balance', NOW(), NOW() + interval '1 day'),

       (7,'zero_balance', NOW(), NOW() - interval '2 day');
