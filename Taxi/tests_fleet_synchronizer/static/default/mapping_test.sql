INSERT INTO fleet_sync.parks_mappings
    (park_id, mapped_park_id, app_family)
VALUES ('p1', 'uber_p1', 'uberdriver'),
       ('p1', 'vezet_p1', 'vezet');

INSERT INTO fleet_sync.drivers_mappings
    (park_id, driver_id, mapped_driver_id, app_family)
VALUES ('p1', 'd1', 'uber_d1', 'uberdriver'),
       ('p1', 'd1', 'vezet_d1', 'vezet');

INSERT INTO fleet_sync.cars_mappings
    (park_id, car_id, mapped_car_id, app_family)
VALUES ('p1', 'c1', 'uber_c1', 'uberdriver'),
       ('p1', 'c1', 'vezet_c1', 'vezet');
