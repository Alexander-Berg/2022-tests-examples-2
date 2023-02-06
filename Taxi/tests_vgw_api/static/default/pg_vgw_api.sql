-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO voice_gateways.voice_gateways
(
    id,
    info.host, info.ignore_certificate,
    settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
    token
)
VALUES
(
    'id_1',
    'host_1', FALSE,
    10, FALSE, 'name_1', 100,
    'token_1'
),
(
    'id_2',
    'host_2', TRUE,
    20, TRUE, 'name_2', 200,
    'token_2'
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'name_1', FALSE),
(DEFAULT, 'name_2', TRUE),
(DEFAULT, 'name_3', TRUE);

INSERT INTO consumers.consumer_voice_gateways
(consumer_id, gateway_id)
VALUES
(1, 'id_1'),
(2, 'id_1'),
(1, 'id_2');

INSERT INTO regions.regions
(id)
VALUES
(1),
(2),
(3);

INSERT INTO regions.gateway_region_settings
(
    region_id, gateway_id,
    enabled, city_id,
    enabled_for
)
VALUES
(
    2, 'id_1',
    FALSE, 'Moscow',
    '{"passenger", "driver"}'
),
(
    2, 'id_2',
    TRUE, 'Moscow',
    '{"passenger"}'
),
(
    1, 'id_1',
    TRUE, 'Moscow',
    '{}'
);

INSERT INTO regions.vgw_enable_settings
(
    gateway_id, region_id, consumer_id,
    enabled, updated_at
)
VALUES
(
    'id_1', 2, 1,
    FALSE, '2021-09-09 12:00:00+03:00'
),
(
    'id_2', 2, 1,
    TRUE, '2021-09-09 12:00:00+03:00'
),
(
    'id_2', 2, 2,
    TRUE, '2021-09-09 12:00:00+03:00'
),
(
    'id_1', 1, 1,
    TRUE, '2021-09-09 12:00:00+03:00'
),
(
    'id_1', 1, 2,
    TRUE, '2021-09-09 12:00:00+03:00'
);
