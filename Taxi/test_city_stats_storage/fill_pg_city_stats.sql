INSERT INTO discounts_operation_calculations.city_stats(
    city,
    sum_gmv,
    city_population,
    avg_order_cost,
    avg_currency_rate,
    trips_count,
    min_date
)
VALUES ('test_city', 400500.40, 100500, 680.857, 0.18, 10500, '2022-04-12'),
       ('test_city2', 200600.0, 200, 333.857, 4.18, 1234, '2022-04-12');


INSERT INTO discounts_operation_calculations.city_trips_with_surge(
    id,
    city,
    surge,
    trips_count
)
VALUES (1, 'test_city', 1.2, 100),
       (2, 'test_city', 1.3, 80),
       (3, 'test_city', 1.5, 80),
       (4, 'test_city', 1.6, 60),
       (5, 'test_city', 1.8, 60),
       (6, 'test_city', 2.0, 50),
       (7, 'test_city', 2.1, 40),
       (8, 'test_city', 2.4, 30),
       (9, 'test_city', 2.7, 50),
       (10, 'test_city', 3.0, 5),
       (11, 'test_city2', 1.1, 55),
       (12, 'test_city2', 1.4, 12),
       (13, 'test_city2', 2.5, 60),
       (14, 'test_city2', 4.0, 8);
