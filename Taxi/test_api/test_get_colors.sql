insert into cars_catalog.colors
(
    raw_color,
    normalized_color,
    color_code
)
values
    ('бронза', 'бронза', '444444'),
    ('Бронза', 'бронза', '555555'),
    ('БРОнза ', 'бронза', '333333'),
    ('карбоновый', 'карбоновый', '000000'),
    ('бирюза', 'бирюза', null::text),
    ('голубой топаз', 'голубой топаз', 'CC0001'),
    ('неголубой топаз', 'неголубой топаз', 'AA0001'),
    ('очень неголубой топаз', 'очень неголубой топаз', 'BB0001');