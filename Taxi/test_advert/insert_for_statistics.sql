INSERT INTO eats_restapp_marketing.advert
(updated_at, place_id, campaign_id, group_id, ad_id, banner_id, averagecpc,
is_active, passport_id)
VALUES (NOW(), 3965, 399264, 4, 5, 1, 25000000, false, 1229582676);

INSERT INTO eats_restapp_marketing.advert_orders_stats
(place_id, day_orders, week_orders, month_orders, all_orders, updated_at)
VALUES (3965, 1,2,3,4, '2020-12-04T05:00:00+0300');

INSERT INTO eats_restapp_marketing.orders_info (
    updated_at,
    place_id,
    dt,
    ad_newcommer,
    ad_oldcommer_ad,
    organic_oldcommer_ad,
    organic_newcommer,
    ad_oldcommer_organic,
    organic_oldcommer_organic,
    good_shows,
    good_clicks,
    ad_newcommer_gmv,
    organic_oldcommer_ad_gmv,
    ad_oldcommer_ad_gmv,
    eventcost_rub
)
VALUES
(NOW(), 3965, '2021-05-25', 1,2,3,4,5,6,123,42,0,0,0,1.0),
(NOW(), 3965, '2021-05-23', 2,3,4,5,6,7,123,42,0,0,0,0.5),
(NOW(), 3965, '2021-05-18', 2,3,4,5,6,7,123,42,0,0,0,1.08),
(NOW(), 3965, '2021-05-07', 4,5,6,7,8,9,42,17,0,0,0,0.25),
(NOW(), 3965, '2021-05-03', 4,5,6,7,8,9,42,17,0,0,0,1.45),
(NOW(), 4, '2021-05-24', 13,14,15,16,17,18,2,0,0,0,0,5.0)
