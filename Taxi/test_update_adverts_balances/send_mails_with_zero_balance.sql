INSERT INTO eats_restapp_marketing.advert
(id, updated_at, place_id, averagecpc, campaign_id, group_id, ad_id, banner_id, content_id, is_active, passport_id, strategy_type)
VALUES (1, NOW(), 1, 10000000, 1, 1, 1, 1, 1, true, 1, 'average_cpc'),
       (2, NOW(), 2, 10000000, 1, 2, 2, 2, 2, true, 1, 'average_cpc'),
       (3, NOW(), 3, 10000000, 1, 3, 3, 3, 3, true, 1, 'average_cpc'),
       (4, NOW(), 4, 10000000, 4, 4, 4, 4, 4, true, 2, 'average_cpc'),
       (5, NOW(), 5, 10000000, 5, 5, 5, 5, 5, false, 1, 'average_cpc'),
       (6, NOW(), 6, 10000000, 6, 6, 6, 6, 6, false, 2, 'average_cpa'),
       (7, NOW(), 7, 10000000, 7, 7, 7, 7, 7, true, 3, 'average_cpc');

INSERT INTO eats_restapp_marketing.balance
    (advert_id, status, sending_time, next_request_time)
VALUES (1,'zero_balance', NOW() - interval '1 day', NOW() + interval '2 day'),
       (2,'zero_balance', NULL, NOW() + interval '2 day'),
       (3,'zero_balance', NOW() + interval '2 day', NOW() + interval '2 day'),
       (4,'high_balance', NOW() - interval '2 day', NOW() + interval '2 day'),
       (5,'zero_balance', NOW() - interval '2 day', NOW() + interval '2 day'),
       (6,'zero_balance', NOW() - interval '2 day', NOW() + interval '2 day'),
       (7,'zero_balance', NOW() - interval '1 day', NOW() + interval '2 day');
