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
