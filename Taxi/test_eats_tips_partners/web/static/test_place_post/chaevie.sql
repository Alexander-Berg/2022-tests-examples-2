INSERT INTO modx_web_user_attributes (
    internalKey,
    fullname,
    name_small,
    phone,
    saving_up_for,
    photo,
    date_reg,
    best2pay_card_token,
    best2pay_card_pan,
    best2pay,
    best2pay_phone,
    address,
    b2p_block_mcc,
    b2p_block_full,
    is_admin_reg,
    date_first_pay
)
VALUES
(10, 'Чаевых Василий Вилларибо', 'Васёк', '9000000010', 'трактор', '', 1, 'token1', 'pan1', '123', 1, '', 0, 0, 0, 0),
(11, 'Чаевых Петр Вилларибо', 'Петро', '9000000011', '','ссылка_на_s3', 1, 'token2', 'pan2', '123', 1, '', 1, 0, 0, 0)
;

INSERT INTO modx_web_users (id, username)
VALUES
    (1, '9000000001'),
    (2, '9000000002')
;


INSERT INTO modx_web_groups (webuser, webgroup)
VALUES
       (1, 2),
       (2, 2)
;
