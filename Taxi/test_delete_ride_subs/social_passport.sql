INSERT INTO persey_payments.ride_subs
    (
        yandex_uid,
        phone_id,
        brand,
        fund_id,
        mod,
        parent_ride_subs_id,
        locale
    )
VALUES
    (
        'portal_uid',
        'af35af35af35af35af35af35',
        'yataxi',
        'friends',
        10,
        1,
        'ru'
    );

INSERT INTO persey_payments.active_ride_subs
    (
        ride_subs_id,
        yandex_uid,
        brand
    )
VALUES
    (
        2,
        'portal_uid',
        'yataxi'
    );
