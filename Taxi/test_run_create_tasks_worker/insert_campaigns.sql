INSERT INTO eats_restapp_marketing.advert
(
    updated_at,
    place_id,
    averagecpc,
    passport_id,
    is_active
)
VALUES 
    (NOW(), 1, 21000000, 11, false),
    (NOW(), 2, 22000000, 22, false),
    (NOW(), 33, 22000000, 22, false)
;

INSERT INTO eats_restapp_marketing.advert_for_create
(
    advert_id,
    token_id,
    averagecpc
)
VALUES 
    (1, 31, 21000000),
    (2, 31, 22000000),
    (3, 31, 22000000);
