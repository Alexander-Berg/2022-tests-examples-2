INSERT INTO supportai.actions_miscs (id, project_id, misc_slug, misc_name)
VALUES
(1, 'detmir_dialog', 'geo_stores2ids_dm', 'Магазины ДМ');


INSERT INTO supportai.actions_miscs_container (id, misc_id, misc)
VALUES
(1, 1,
$$
{
    "city": "москва",
    "metro": "выставочная",
    "orient": "столица",
    "street": "краснооктябрьская",
    "store_id" : "1976"
}
$$
),
(2, 1,
$$
{
    "city": "сафоново",
    "metro": null,
    "orient": null,
    "street": null,
    "store_id" : "345"
}
$$
);
