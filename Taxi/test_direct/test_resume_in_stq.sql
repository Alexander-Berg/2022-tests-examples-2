INSERT INTO eats_restapp_marketing.advert
(updated_at, place_id, averagecpc, campaign_id, group_id, ad_id, banner_id, content_id,
is_active, passport_id)
VALUES (NOW(),2,1000000, 399264, 1234, 5, 1, 2, false, 1229582676),
       (NOW(),23,1233123, 399264, 3455, 15, 21, 32, false, 1229582676);

INSERT INTO eats_restapp_marketing.keywords
    (advert_id, keyword_id)
VALUES (1,1);
