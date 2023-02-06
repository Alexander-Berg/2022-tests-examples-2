BEGIN;

ALTER TABLE storage.places
    ALTER COLUMN brand TYPE storage.place_brand_v2
        USING brand::storage.place_brand_v2;

DROP CAST (storage.place_brand AS storage.place_brand_v2);
DROP CAST (storage.place_brand_v2 AS storage.place_brand);

DROP FUNCTION place_brand_v2_to_place_brand (storage.place_brand_v2);
DROP FUNCTION place_brand_to_place_brand_v2 (storage.place_brand);

COMMIT;
