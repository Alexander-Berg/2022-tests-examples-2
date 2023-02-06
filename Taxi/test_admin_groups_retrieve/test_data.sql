insert into access_control.system (name)
values ('system1');
insert into access_control.groups (name, slug, parent_id, system_id)
values
    ('agroup1', 'agroup1', null, 1),
    ('zgroup11', 'zgroup11', 1, 1),
    ('bgroup12', 'bgroup12', 1, 1),
    ('xgroup2', 'xgroup2', null, 1),
    ('qgroup3', 'qgroup3', null, 1);
