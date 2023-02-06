insert into
    access_control.groups (id, slug, name, parent_id, system_id)
values
    (1, 'system_main_group_1', 'system main group 1', null, 1),
    (2, 'system_main_group_2', 'system main group 2', 1, 1),
    (3, 'system_second_group_1', 'system second group 1', null, 2)
;
