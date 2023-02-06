insert into access_control.system (name)
values ('system1'),
       ('system2'),
       ('system3'),
       ('system4');
insert into access_control.users (provider, provider_user_id)
values ('yandex', '1111111111111111'),
       ('yandex', '1134567890123456');
insert into access_control.groups (name, slug, system_id)
values ('group1', 'group1', 1),
       ('group2', 'group2', 1),
       ('group1', 'group1', 2),
       ('group1', 'group1', 3),
       ('group1', 'group1', 4);
insert into access_control.m2m_groups_users (group_id, user_id)
values (1, 1);
