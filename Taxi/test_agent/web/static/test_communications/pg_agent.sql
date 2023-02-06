INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02'
);

INSERT INTO agent.mass_notifications (id,creator,created_at,target_users,viewed_users,title,body,link,type,targets)
VALUES ('5c140185d6f24d1a55412dba1f357ef','webalex',NOW(),100,0,'Test 1','Test1',null,'warning','{}');

INSERT INTO agent.notifications
(id, login, created_at, title, body, notification_type,mass_id)
VALUES ('72691367106446e48815f31894274401','webalex','2021-01-02 00:00:01'::timestamp,'Test 1','Test 1','warning','5c140185d6f24d1a55412dba1f357ef'),
       ('72691367106446e48815f31894274402','webalex','2021-01-02 00:00:02'::timestamp,'Test 2','Test 2','warning',null),
       ('72691367106446e48815f31894274403','webalex','2021-01-02 00:00:03'::timestamp,'Test 3','Test 3','warning',null),
       ('72691367106446e48815f31894274404','webalex','2021-01-02 00:00:04'::timestamp,'Test 4','Test 4','warning',null),
       ('72691367106446e48815f31894274405','webalex','2021-01-02 00:00:05'::timestamp,'Test 5','Test 5','warning',null);
