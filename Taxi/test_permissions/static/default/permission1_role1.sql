insert into access_control.permissions(system_id, name)
values (1, 'permission1');

insert into access_control.m2m_permissions_roles (role_id, permission_id)
values (1, 1);
