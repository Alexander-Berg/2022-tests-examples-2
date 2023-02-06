INSERT INTO auth_data (id, personal_phone_id, code, authorized, attempts, code_created)
VALUES ('3', '111', '666666', false, 0,  '2019-02-01T14:09:30Z'),
       ('4', '123', '666666', false, 0,  '2019-02-01T14:09:30Z'),
       ('5', '666', '666666', false, 0,  '2019-02-01T14:00:00Z'),
       ('6', '666', '666666', false, 3,  '2019-02-01T14:00:00Z'),
       ('7', '666', '666666', false, 4,  '2019-02-01T14:00:00Z'),
       ('8', '777', '666666', false, 0,  '2019-02-01T14:08:00Z'),
       ('9', '666', '666666', true,  0,  '2019-02-01T14:00:00Z'),
       ('42', '777', '123', false, 3, '2019-02-01T14:00:00Z')
    ON CONFLICT DO NOTHING;

INSERT INTO phone_data (personal_phone_id, last_sms_sent)
VALUES ('123', '2019-02-01T14:09:30Z'),
       ('666', '2019-02-01T14:00:00Z'),
       ('777', '2019-02-01T14:08:00Z')
    ON CONFLICT DO NOTHING;
