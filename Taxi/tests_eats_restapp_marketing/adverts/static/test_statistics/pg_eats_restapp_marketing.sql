INSERT INTO eats_restapp_marketing.advert
(
    place_id,
    campaign_id,
    banner_id,
    is_active,
    passport_id,
    updated_at
)
VALUES
(
    1,
    1,
    1,
    true,
    1,
    now()
);

INSERT INTO eats_restapp_marketing.advert_orders_stats
(
    place_id,
    day_orders,
    week_orders,
    month_orders,
    all_orders,
    updated_at
)
VALUES
(
    1,
    10,
    70,
    300,
    500,
    now()
);

INSERT INTO eats_restapp_marketing.orders_info (
    updated_at,
    place_id,
    dt,
    ad_newcommer,
    ad_oldcommer_ad,
    ad_oldcommer_organic,
    organic_newcommer,
    organic_oldcommer_ad,
    organic_oldcommer_organic,
    good_shows,
    good_clicks,
    ad_newcommer_gmv,
    organic_oldcommer_ad_gmv,
    ad_oldcommer_ad_gmv,
    ad_oldcommer_organic_gmv,
    eventcost_rub
)
VALUES
(now(), 1, '2021-08-02', 1, 0, 0, 0, 0, 0, 0, 1, 3, 4, 5, 20.5, 1.0),
(now(), 1, '2021-08-03', 1, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 30.5, 0.0),
(now(), 1, '2021-08-04', 2, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 100, 2.0);
