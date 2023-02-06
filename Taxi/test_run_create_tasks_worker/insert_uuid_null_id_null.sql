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
    (NOW(), 1, 21000000, 11, false, null),
    (NOW(), 2, 22000000, 22, false, null),
    (NOW(), 33, 22000000, 22, false, null)
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
