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
    'gateway_id_1',
    '$mockserver', FALSE,
    90, TRUE, 'gateway_name_1', 100,
    'gateway_token_1'
),
(
    'gateway_id_2',
    '$mockserver', TRUE,
    1, FALSE, 'gateway_name_2', 100,
    'gateway_token_2'
);

INSERT INTO consumers.consumers
(id, name, enabled)
VALUES
(DEFAULT, 'consumer_name_1', TRUE);

INSERT INTO consumers.consumer_voice_gateways
(consumer_id, gateway_id)
VALUES
(1, 'gateway_id_1'),
(1, 'gateway_id_2');

INSERT INTO regions.regions
(id)
VALUES
(1);

INSERT INTO regions.gateway_region_settings
(
    region_id, gateway_id,
    enabled, city_id,
    enabled_for
)
VALUES
(
    1, 'gateway_id_2',
    TRUE, 'Moscow',
    '{"passenger", "driver"}'
);

INSERT INTO regions.vgw_enable_settings
(
    gateway_id, region_id, consumer_id,
    enabled
)
VALUES
(
    'gateway_id_2', 1, 1,
    TRUE
);
