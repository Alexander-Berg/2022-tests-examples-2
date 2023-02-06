insert into
    access_control.permissions (system_id, name)
values
    (1, 'system_main_role_1_permission_1'),
    (1, 'system_main_role_2_permission_1'),
    (1, 'system_main_role_3_permission_1'),
    (1, 'system_main_role_3_permission_2'),
    (2, 'system_second_role_1_2_permission_1'),
    (2, 'system_second_role_2_permission_1'),
    (1, 'system_main_empty_permission_1'),
    (1, 'system_main_empty_permission_2')
;

insert into
    access_control.m2m_permissions_roles (permission_id, role_id)
values
    (1, 1), (2, 2), (3, 3), (4, 3), (5, 4), (5, 5), (6, 5)
;
