INSERT INTO inapp_communications.promos_on_map_cache (
    yandex_uid,
    created_at,
    updated_at,
    longitude,
    latitude,
    promos_on_map
) VALUES
(
    'yauid',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    37.211375,
    55.477068,
    '{"objects":[{"longitude":37.56,"latitude":55.77,"promotion_id":"published_promo_on_map_id"}]}'::jsonb
),
(
    'yauid2',
    CURRENT_TIMESTAMP - INTERVAL '300 seconds',
    CURRENT_TIMESTAMP - INTERVAL '300 seconds',
    37.211375,
    55.477068,
    '{"objects":[{"longitude":37.56,"latitude":55.77,"promotion_id":"published_promo_on_map_id"}]}'::jsonb
);
