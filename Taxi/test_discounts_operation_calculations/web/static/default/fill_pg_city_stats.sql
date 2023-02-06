INSERT INTO discounts_operation_calculations.city_stats(
    city,
    sum_gmv,
    city_population,
    avg_order_cost,
    avg_currency_rate,
    trips_count,
    min_date
)
VALUES ('test_city', 400503, 1005996, 684.8574100625857, 0.18180542954194057, 10500, '2022-03-28');


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
       (10, 'test_city', 3.0, 5);
