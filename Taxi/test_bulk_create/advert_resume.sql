INSERT INTO eats_restapp_marketing.advert
(created_at, updated_at, place_id, campaign_id, group_id, ad_id, banner_id, is_active, weekly_spend_limit, averagecpc, passport_id)
VALUES ('2021-01-10T00:00:00.000000+0000', NOW(), 123, 123, 123, 123, 123, false, 10000000000, 10000000, 1229582676);


INSERT INTO eats_restapp_marketing.advert_for_create
(advert_id, token_id, averagecpc, weekly_spend_limit)
VALUES (1, 1, 20000000, 15000000000);
