insert into access_control.system (name)
values ('group1');
insert into access_control.users (provider, provider_user_id)
values ('yandex', 'user1');
insert into access_control.groups (name, slug, system_id)
values ('group1', 'group1', 1);
insert into access_control.roles (name, slug, system_id)
values ('role1', 'role1', 1);
insert into access_control.permissions (system_id, name)
values (1, 'permission1');
insert into access_control.m2m_permissions_roles (permission_id, role_id)
values (1, 1);
insert into access_control.permission_calculation_rules (system_id, storage, path, version, name)
values (1, 'body', 'org', 1, 'org_body_rule');
insert into access_control.calculated_permissions (role_id, rule_id, rule_value)
values (1, 1, 'taxi');
insert into access_control.m2m_groups_roles (group_id, role_id)
values (1, 1);
insert into access_control.m2m_groups_users (group_id, user_id)
values (1, 1);
insert into access_control.restrictions(role_id, handler_path, handler_method, restriction)
values (1, '/foo/bar', 'POST', ('{}'))
