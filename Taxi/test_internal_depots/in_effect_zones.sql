INSERT INTO depots_wms.companies (company_id,
                                  external_id,
                                  ownership,
                                  title,
                                  fullname,
                                  legal_address,
                                  actual_address,
                                  address,
                                  phone,
                                  email,
                                  psrn,
                                  tin)
VALUES ('6490c0508a8c4370be75096d9f0ef615000200010001',
        'd6d90560-dc76-11ea-8ea5-37d3d3ea33da',
        'yandex',
        'ООО Рога и Копыта',
        'ООО Рога и Копыта',
        'Юр. адрес',
        'Факт. адрес',
        '2021-07-29 15:33:39.898566 +00:00',
        '2384234892',
        'kjsdfhks@sfsdfsd.ru',
        '123',
        '321123321');

INSERT INTO depots_wms.depots
(depot_id, external_id, updated, name, address, title, location, timezone, region_id, currency, status, source, timetable)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100012020',
        '2020',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_1',
        'Доширбург, Яичное лапшассе, 39',
        'Мир Дошиков',
        (5.0, 5.0)::depots_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        'WMS',
        ARRAY[('everyday'::depots_wms.day_type, ('08:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[]);

INSERT INTO depots_wms.depots
(depot_id, external_id, updated, name, address, title, location, timezone, region_id, currency, status, source,
 allow_parcels, company_id, oebs_depot_id, timetable)
VALUES ('ddb8a6fbcee34b38b5281d8ea6ef749a000100012021',
        '2021',
        '2019-12-01 01:01:01.000000+00',
        'test_lavka_2',
        'Доширбург, Яичное лапшассе, 39',
        'Мир Дошиков',
        (6.0, 6.0)::depots_wms.depot_location,
        'Europe/Moscow',
        213,
        'RUB',
        'active',
        'WMS',
        true,
        '6490c0508a8c4370be75096d9f0ef615000200010001',
        'oebs-depot-id-for-test_lavka_1',
        ARRAY[('everyday'::depots_wms.day_type, ('08:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[]);

INSERT INTO depots_wms.depots (depot_id, updated, status, external_id, cluster, title, name, region_id, address,
                               location, "zone",
                               currency, timetable, timezone, source, root_category_id, assortment_id, price_list_id,
                               company_id,
                               allow_parcels, options, phone_number, email, directions, telegram, open_ts, hidden)
VALUES ('e8756eee278742e99624399f81841c07000300010000', '2021-08-13 09:19:48.502139 +00:00', 'active', '266222',
        'Тель-Авив', 'Zeev Jabutinsky Road 124, Ramat Gan, Israel', 'lavka_zabotinsky_124', '131',
        'Jabotinski, 124 Ramat Gan, Israel', '(32.0901309999999995,34.8205510000000018)', '{}', 'ILS',
        ARRAY[('everyday'::depots_wms.day_type, ('08:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        'Asia/Jerusalem', 'WMS', 'a04e2ecb54344fc0945a623e14e2617c000200010001',
        'afa1095fbcee462dafe65632e095fca9000200010001', '21477d99cd9b40068e797daa49faf801000300010000',
        'fcc89d85e5e444268628bbdbe6795c21000200010000', 'false', '{
    "tristero": false
  }', '+972533481762', '', '', '------', '2018-12-31 21:00:00.000000 +00:00', 'false'),
       ('c3df22637dc341d9a21cdc00774a241a000100010001', '2021-08-14 04:20:39.546843 +00:00', 'active', '383762',
        'Санкт-Петербург', 'Маршала Казакова, 72', 'yandekslavka_marshala_kazakova_72k1', '2',
        '198335, г. Санкт-Петербург, ул. Маршала Казакова, дом 72, корпус 1, строение 1',
        '(59.8674480000000031,30.1718410000000006)', '{}', 'RUB',
        ARRAY[('everyday'::depots_wms.day_type, ('08:00','23:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        'Europe/Moscow', 'WMS',
        '8f4cf8acbf2c4fe5876f20fb12f01a51000100010001', 'dc464bea93294d6da9b1727eb12c1073000200010000',
        '4cdfbe900cdb4a92aa2545d711b311c7000200010000', '2fda2157e6ba4e84b65efdd93626adfe000100010001', 'true', '{
         "tristero": true
       }', '+79296223987', '-----@gmail.com',
        'Лавка находиться в подвальном помещении с торца здания, рядом универсам "Верный". На двери вывеска "Яндекс.Лавка".',
        '------telegramm--', '2018-12-31 21:00:00.000000 +00:00', 'false'
        );
