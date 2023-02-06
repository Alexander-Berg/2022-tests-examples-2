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
    (1, 31, 'aa945b93-759b-4e72-9af4-2ff26496291d', 21000000),
    (2, 31, '641d1037-b37c-44a1-8baf-311e92c3f053', 22000000),
    (3, 31, 'c7d543da-d5a0-4009-915a-307a0972c06f', 22000000);