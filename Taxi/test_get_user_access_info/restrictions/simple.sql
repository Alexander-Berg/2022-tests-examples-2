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
insert into access_control.m2m_groups_roles (group_id, role_id)
values (1, 1);
insert into access_control.m2m_groups_users (group_id, user_id)
values (1, 1);


insert into access_control.restrictions (role_id, handler_path, handler_method, restriction)
values (1, '/example/handler1', 'POST'::access_control.http_method_t,
'{"init": {"arg_name": "body:sample_int_value",'
'"arg_type": "int", "value": 3}, "type": "lte"}'::jsonb);
insert into access_control.restrictions (role_id, handler_path, handler_method, restriction)
values (1, '/example/handler2', 'GET'::access_control.http_method_t,
'{"init": {"predicates": [{"init": {"arg_name":'
' "body:sample_field.subfield", "set_elem_type": "string",'
' "set": ["value1", "value2"]}, "type": "in_set"}, {"init": '
'{"arg_name": "query:sample_double_value", "arg_type": "double",'
' "value": 5.6}, "type": "lt"}]}, "type": "all_of"}'::jsonb);
