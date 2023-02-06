-- noinspection SqlNoDataSourceInspectionForFile

INSERT INTO biometry_etalons.etalons
(
    id,
    version,
    modified,
    created
)
VALUES
    (
        '000000000000000000000001',
        1,
        '2019-04-10 10:00:00.000000',
        '2019-04-10 10:00:00.000000'
    ),
    (
        '000000000000000000000002',
        1,
        '2019-04-10 10:00:00.000000',
        '2019-04-10 10:00:00.000000'
    );

INSERT INTO biometry_etalons.profiles
(
    id,
    profile_id,
    profile_type,
    provider,
    meta,
    idempotency_token,
    etalon_id,
    updated_at
)
VALUES
    (
        '000000000000000000000001',
        'park00000000000000000001_driver000000000000000001',
        'park_driver_profile_id',
        'taxi',
        '{ "park_id": "123" }',
        'unique_token',
        '000000000000000000000001',
        '2019-04-10 10:00:00.000000'
    ),
    (
        '000000000000000000000002',
        'park00000000000000000002_driver000000000000000002',
        'park_driver_profile_id',
        'signalq',
        '{ "park_id": "123" }',
        'unique_token2',
        '000000000000000000000002',
        '2019-04-10 10:00:00.000000'
    );

INSERT INTO biometry_etalons.media
(
    id,
    etalon_set_id,
    park_id,
    driver_profile_id,
    media_storage_id,
    media_storage_type,
    type,
    media_storage_bucket,
    is_active,
    modified,
    created
)
VALUES
    (
        '1',
        '000000000000000000000001',
        'park00000000000000000001',
        'driver000000000000000001',
        'ms0000000000000000000001',
        'media-storage',
        'selfie',
        'driver_photo',
        false,
        '2019-04-10 10:00:00.000000',
        '2019-04-10 10:00:00.000000'
    ),
    (
        '2',
        '000000000000000000000002',
        'park00000000000000000001',
        'driver000000000000000001',
        'ms0000000000000000000002',
        'signalq',
        'photo',
        'driver_photo',
        true,
        '2019-04-10 10:00:00.000000',
        '2019-04-10 10:00:00.000000'
    ),
    (
        '3',
        '000000000000000000000001',
        'park00000000000000000001',
        'driver000000000000000001',
        'ms0000000000000000000003',
        'media-storage',
        'voice',
        'driver_photo',
        true,
        '2019-04-10 10:00:00.000000',
        '2019-04-10 10:00:00.000000'
    ),
    (
        '4',
        '000000000000000000000002',
        'park00000000000000000001',
        'driver000000000000000001',
        'ms0000000000000000000004',
        'media-storage',
        'video',
        'driver_photo',
        false,
        '2019-04-10 10:00:00.000000',
        '2019-04-10 10:00:00.000000'
    ),
    (
        '5',
        '000000000000000000000002',
        'park00000000000000000005',
        'driver000000000000000005',
        'ms0000000000000000000005',
        'media-storage',
        'video',
        'driver_photo',
        false,
        '2019-04-10 10:00:00.000000',
        '2222-04-10 10:00:00.000000'
    );

INSERT INTO biometry_etalons.face_features
(
    id,
    features,
    etalon_id,
    media_id
)
VALUES
    (
        '1',
        '{1., 1., 1.}',
        '000000000000000000000001',
        '1'
    ),
    (
        '2',
        '{2., 2., 2.}',
        '000000000000000000000002',
        '4'
    ),
    (
        '3',
        '{3., 3., 3.}',
        '000000000000000000000002',
        '5'
    );

INSERT INTO biometry_etalons.media_meta
(
    id,
    media_id,
    key,
    value
)
VALUES
(
    '1',
    '1',
    'ha',
    'haha'
),
(
    '2',
    '1',
    'he',
    'hehe'
),
(
    '5',
    '5',
    'ho',
    'hoho'
);
