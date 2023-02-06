insert into
    startrack_reports.representations
(
    action,
    data_key,
    data_key_tanker_key,
    data_value_representation_function,
    position
)
values
    ('drafts.commissions_create', 'zone', 'Зона', '', 1),
    ('drafts.commissions_create', 'enabled', 'Включена', 'bool_repr', 2),
    ('drafts.commissions_edit', 'zone', 'Зона', '', 1);
