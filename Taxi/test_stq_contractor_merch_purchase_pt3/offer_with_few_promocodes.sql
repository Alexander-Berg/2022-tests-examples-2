INSERT INTO contractor_merch.promocodes (
    id,
    feeds_admin_id,

    status,

    number,

    created_at,
    updated_at
) VALUES (
    'p1',
    'f1',

    'available',

    '[{"number": "WSFWF151", "caption": "Макдоналдс"}, {"number": "WSFWF132", "caption": "Автомойка"}, {"number": "WSFWF21323", "caption": "Шаверма"}]',

    NOW(),
    NOW()
), (
    'p2',
    'f2',

    'available',

    'WSFWF11412',

    NOW(),
    NOW()
);
