INSERT INTO eats_restapp_places.place_info (
    place_id,
    name,
    address,
    entrances,
    permalink,
    address_comment,
    full_address_comment)
VALUES
    (111,'11111','addr111',NULL,NULL,'comment111',NULL),
    (222,'22222','addr222','[]','2222','comment222 этаж',NULL),
    (333,'33333','addr333','[{"lat": 50.0,"lon":40.1}]','3333','comment333 этаж','comment333 этаж 3'),
    (444,'44444','addr444','[{"lat": 51.0,"lon":41.1}]','4444','comment444','comment444_full'),
    (555,'55555','addr555','[{"lat": 52.0,"lon":42.1},{"lat": 53.0,"lon":43.1}]','5555','comment555',NULL);

INSERT INTO eats_restapp_places.entrance_photo (
    place_id,
    url,
    status,
    partner_id)
VALUES
    (111,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/111x111','approved',11),
    (111,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/111x112','approved',11),
    (222,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/222x221','approved',11),
    (222,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/222x222','rejected',11),
    (333,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/333x331','approved',11),
    (333,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/333x332','approved',11),
    (333,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/333x333','uploaded',11),
    (444,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/444x444','approved',11),
    (555,'avatars.mds.yandex.net/get-eda/3807631/0d0a910ca161d055b9dbfd0518f2b242/555x555','approved',11);
