-- noinspection SqlNoDataSourceInspectionForFile

ALTER TABLE voice_gateways.voice_gateways DISABLE TRIGGER status_changed_tr;
INSERT INTO voice_gateways.voice_gateways
(
    id,
    enabled_at,
    info.host, info.ignore_certificate,
    settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
    token,
    disable_reason,
    enable_after,
    relapse_count
)
VALUES
(
    'id_1',
    '2021-09-11 11:00:00+03:00',  -- success period (30 mins) passed
    'host_1', FALSE,
    10, FALSE, 'name_1', 100,
    'token_1',
    'some disable reason',
    '2021-09-11 10:00:00+03:00',
    2
);
ALTER TABLE voice_gateways.voice_gateways ENABLE TRIGGER status_changed_tr;
