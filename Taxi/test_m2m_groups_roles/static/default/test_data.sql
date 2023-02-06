insert into access_control.system(name) values
('system_1'),
('system5')
;
insert into access_control.groups (name, slug, system_id)
values
('группа 1', 'group1', 1),
('group2', 'group2', 2),
('group3', 'group3', 2)
;
insert into access_control.roles (name, slug, system_id)
values
('главная роль', 'main_role', 1),
('другая роль', 'other_role', 1),
('существующая роль', 'existed_role', 1),
('role1', 'role1', 2),
('role2', 'role2', 2),
('role3', 'role3', 2)
;
insert into access_control.m2m_groups_roles (group_id, role_id)
values
(1, 3),
(2, 4),
(2, 5),
(2, 6),
(3, 4)
;
