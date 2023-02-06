INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    department,
    piece
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02',
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'liambaev',
    'Лиам',
    'Баев',
    '2016-06-02',
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'orangevl',
    'Семён',
    'Решетняк',
    '2016-06-02',
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'device25',
    'Андрей',
    'Бахвалов',
    '2016-06-02',
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'whitelist_login_1',
    'Александр',
    'Николаев',
    '2016-06-02',
    null,
    false
),
(
    1120000000252888,
     NOW(),
    'black_whitelist_login',
    'black',
    'white',
    '2016-06-02',
    null,
    false
);



INSERT INTO agent.users_payday (login,payday_uuid,created,status,card_mask,phone_pd_id,ticket_tracker) VALUES
('webalex','3326fb28-32d9-4694-86ef-ee45ea548c01',NOW(),'pending_documents','4276********3250','7f8d5e36-7bf2-425a-8463-6ed8e61e9e23','PAYDAY-1'),
( 'liambaev','007bc7a5-4b5c-4d44-84f5-dca9649c2dae',NOW(),'active','4276********3250','dc6732e6-834e-4cea-9be2-2cbc3e5864f5','PAYDAY-1'),
( 'orangevl','007bc7a5-4b5c-4d44-84f5-dca9649c2dae',NOW(),'avialable',null,null,null);
