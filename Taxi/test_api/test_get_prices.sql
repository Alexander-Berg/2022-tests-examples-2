insert into cars_catalog.prices
(
    car_year,
    car_age,
    car_price,
    normalized_mark_code,
    normalized_model_code
)
values
    (2013, 5, 600000, 'TOYOTA', 'CAMRY'),
    (null::integer, 4, 6000, 'TOYOTA', 'CAMRY'),
    (2010, 8, 500000, 'TOYOTA', 'COROLLA'),
    (2010, 8, -1, 'VAZ', 'KALINA'),
    (2010, 8, -1, 'FERRARI', 'ITALIA'),
    (2010, 8, -1, 'BMW', '7ER'),
    (2010, 8, -1, 'AUDI', 'TT'),
    (2020, 0, -1, 'AUDI', 'TT'),
    (2015, 3, -1, 'AUDI', 'A8'),
    (2010, 8, -1, 'ASTON_MARTIN', 'DB9'),
    (2010, 8, -1, 'BMW', 'X6');
