insert into
    access_control.users (id, provider, provider_user_id)
values
    (1, 'yandex', 'user1'),
    (2, 'yandex', 'user2'),
    (3, 'yandex', 'user3'),
    (4, 'yandex', 'user4'),
    (5, 'yandex', 'user5'),
    (6, 'yandex', 'user6'),
    (7, 'yandex', 'user7'),
    (8, 'yandex', 'user8'),
    (9, 'yandex', 'user9'),
    (10, 'yandex', 'user10')
;

insert into
    access_control.m2m_groups_users (group_id, user_id)
values
    (1, 1),
    (2, 2),
    (2, 3),
    (1, 4),
    (1, 5),
    (2, 5),
    (1, 6),
    (2, 6),
    (1, 7),
    (2, 8),
    (2, 9),
    (2, 10)
;
