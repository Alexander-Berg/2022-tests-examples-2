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
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'name_1', FALSE),
(DEFAULT, 'name_2', TRUE);

INSERT INTO consumers.consumer_voice_gateways
(consumer_id, gateway_id)
VALUES
(1, 'id_1'),
(2, 'id_1');

INSERT INTO regions.regions
(id, deleted)
VALUES
(1, TRUE),
(2, TRUE);

INSERT INTO regions.gateway_region_settings
(
    region_id, gateway_id,
    enabled, city_id,
    enabled_for
)
VALUES
(
    1, 'id_1',
    TRUE, 'Moscow',
    '{"passenger", "passenger"}'
);

INSERT INTO regions.vgw_enable_settings
(
    gateway_id, region_id, consumer_id,
    enabled
)
VALUES
(
    'id_1', 1, 1,
    TRUE
),
(
    'id_1', 1, 2,
    TRUE
);
