INSERT INTO eats_restapp_places.place_info (
    place_id,
    name,
    address,
    entrances,
    permalink,
    address_comment,
    full_address_comment)
VALUES
    (222,'name222','address222',NULL,'222',NULL,NULL);

INSERT INTO eats_restapp_places.entrance_photo (
    place_id,
    url,
    status,
    partner_id)
VALUES
    (222,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/111x111','approved',22),
    (222,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/111x112','approved',22);
