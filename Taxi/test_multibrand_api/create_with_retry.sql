INSERT INTO persey_payments.ride_subs
    (
        yandex_uid,
        phone_id,
        brand,
        fund_id,
        mod,
        locale
    )
VALUES
    (
        'phonish_uid',
        'af35af35af35af35af35af35',
        'yataxi',
        'friends',
        777,
        'en'
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
        'phonish_uid',
        'yataxi'
    );
