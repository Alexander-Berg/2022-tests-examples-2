BEGIN;

ALTER TABLE storage.places
    ADD new_rating JSON;
COMMIT;
