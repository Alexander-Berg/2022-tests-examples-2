insert into access_control.system (name)
values ('group1');
insert into access_control.users (provider, provider_user_id)
values ('yandex', 'user1');
insert into access_control.users (provider, provider_user_id)
values ('yandex', 'user2');
insert into access_control.groups (name, slug, system_id)
values ('treegroup1', 'treegroup1', 1);
insert into access_control.groups (parent_id, name, slug, system_id)
values (1, 'treegroup12', 'treegroup12', 1);
insert into access_control.groups (parent_id, name, slug, system_id)
values (2, 'treegroup123', 'treegroup123', 1);
insert into access_control.groups (parent_id, name, slug, system_id)
values (2, 'treegroup124', 'treegroup124', 1);
insert into access_control.roles (name, slug, system_id)
values ('role1', 'role1', 1);
insert into access_control.roles (name, slug, system_id)
values ('role2', 'role2', 1);
insert into access_control.roles (name, slug, system_id)
values ('role3', 'role3', 1);
insert into access_control.permissions (system_id, name)
values (1, 'permission1');
insert into access_control.m2m_permissions_roles (permission_id, role_id)
values (1, 1);
insert into access_control.permissions (system_id, name)
values (1, 'permission2');
insert into access_control.m2m_permissions_roles (permission_id, role_id)
values (2, 2);
insert into access_control.permissions (system_id, name)
values (1, 'permission3');
insert into access_control.m2m_permissions_roles (permission_id, role_id)
values (3, 3);
insert into access_control.m2m_groups_roles (group_id, role_id)
values (1, 1);
insert into access_control.m2m_groups_roles (group_id, role_id)
values (3, 2);
insert into access_control.m2m_groups_roles (group_id, role_id)
values (4, 3);
insert into access_control.m2m_groups_users (group_id, user_id)
values (3, 1);
insert into access_control.m2m_groups_users (group_id, user_id)
values (4, 2);
