INSERT INTO eats_restapp_marketing.advert
(
    updated_at,
    place_id,
    averagecpc,
    passport_id,
    is_active,
    campaign_id
)
VALUES
    (NOW(), 1, 21000000, 11, false, 11),
    (NOW(), 2, 22000000, 22, false, 22),
    (NOW(), 33, 22000000, 22, false, 333)
;

INSERT INTO eats_restapp_marketing.advert_for_create
(
    advert_id,
    token_id,
    campaign_uuid,
    averagecpc
)
VALUES
    (1, 31, null, 21000000),
    (2, 31, null, 22000000),
    (3, 31, null, 22000000);
