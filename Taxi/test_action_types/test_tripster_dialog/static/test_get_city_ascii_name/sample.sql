INSERT INTO supportai.actions_miscs (id, project_id, misc_slug, misc_name)
VALUES
(2, 'tripster_dialog', 'get_city_ascii_name', 'Маппинг названий магазинов в латиницу');

INSERT INTO supportai.actions_miscs_container (id, misc_id, misc)
VALUES
(1, 2,
$$
{
    "city": "джубга",
    "ascii_name": "Dzhubga"
}
$$
),
(2, 2,
$$
{"city": "гусь-хрустальный", "ascii_name": "Gus_Khrustalny"}
$$
);
