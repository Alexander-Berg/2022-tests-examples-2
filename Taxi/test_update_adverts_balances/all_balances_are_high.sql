INSERT INTO eats_restapp_marketing.advert
(id, updated_at, place_id, averagecpc, campaign_id, group_id, ad_id, banner_id, content_id, is_active, passport_id, strategy_type)
VALUES (1, NOW(), 1, 10000000, 1, 2, 2, 2, 2, true, 1, 'average_cpc'),
       (2, NOW(), 2, 10000000, 1, 2, 2, 2, 2, true, 2, 'average_cpc');

INSERT INTO eats_restapp_marketing.balance
    (advert_id, status, sending_time, next_request_time)
VALUES (1,'high_balance', NOW() - interval '2 day', NOW() + interval '2 day'),
       (2,'zero_balance', NOW() + interval '2 day', NOW() + interval '2 day');
