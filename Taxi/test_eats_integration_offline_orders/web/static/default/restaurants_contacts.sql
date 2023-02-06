INSERT INTO restaurants_contacts (
    uuid,
    place_id,
    title,
    fullname_id,
    phone_id,
    email_id,
    telegram_login_id,
    comment,
    deleted_at
)
VALUES
(
     'contact_uuid_1',
     'place_id__1',
     'ЛПР',
     'personal_fullname_id_1',
     'personal_phone_id_1',
     NULL,
     NULL,
     'звонить в будни',
     NULL
),
(
     'contact_uuid_2',
     'place_id__1',
     'ЛПР',
     'personal_fullname_id_2',
     'personal_phone_id_2',
     'personal_email_id_2',
     NULL,
     'звонить в будни',
     NOW()
)
;
