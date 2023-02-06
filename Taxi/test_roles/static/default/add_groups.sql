insert into
    access_control.groups (id, slug, name, system_id, parent_id)
values
    (1, 'system_main_group_1', 'system main group 1', 1, null),
    (2, 'system_main_group_2', 'system main group 2', 1, null),
    (3, 'system_main_group_3', 'system main group 3', 1, null),
    (4, 'system_second_group_1', 'system second group 1', 2, null),
    (5, 'system_second_group_2', 'system second group 2', 2, 4)
;
