insert into cars_catalog.colors
(
    raw_color,
    normalized_color,
    color_code
)
values
    ('Бронза', 'бронза', '555555');

insert into cars_catalog.brand_models
(
    raw_brand,
    raw_model,
    normalized_mark_code,
    normalized_model_code,
    corrected_model
)
values
    ('ford', 'Mustang', 'FORD', 'MUSTANG', 'ford Mustang');

insert into cars_catalog.prices
(
    normalized_mark_code,
    normalized_model_code,
    car_year,
    car_age,
    car_price
)
values
    ('TOYOTA', 'CAMRY', 2013, 2003, 100);

insert into cars_catalog.autoru_prices_cache
    (mark_code, model_code, age, price, loaded_at)
values
       ('FORD', 'GALAXY', 2, '684068.6', '2019-05-01+00'),
       ('FORD', 'GALAXY', 9, '350000.7', '2019-05-01+00');
