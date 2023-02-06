INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at,team
)
VALUES
    (1120000000252888, NOW(), 'liambaev', 'Лиам', 'Баев', '2016-06-02',null ),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2016-06-02',null);



INSERT INTO agent.mass_notifications
(
 id,
 creator,
 created_at,
 target_users,
 viewed_users,
 title,
 body,
 link,
 type,
 targets
)
VALUES
(
 'faadb32303664af38b75ff2653e1bb43',
 'webalex',
 '2022-04-20 16:10:02',
 100,
 0,
 'Title 2',
 'Body 2',
 'url 2',
 'warning',
 '[{"type": "projects", "value": ["calltaxi"]}]'
);


INSERT INTO agent.notifications (mass_id, url_link, viewed_at, is_viewed, notification_type, body, title, created_at, login, id) VALUES
(
 'faadb32303664af38b75ff2653e1bb43',
 null,
 NOW(),
 true,
 'warning',
 'Test',
 'Test',
 NOW(),
 'webalex',
 '63cae574fca043d8833d7bb9a9bb7ef2'
),
(
 'faadb32303664af38b75ff2653e1bb43',
 null,
 NOW(),
 true,
 'warning',
 'Test',
 'Test',
 NOW(),
 'liambaev',
 '63cae574fca043d8833d7bb9a9bb7ef1'
);
