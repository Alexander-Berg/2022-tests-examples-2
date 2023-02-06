INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'stations_fetcher',
'stations_fetcher',
'{"first_instant":0,"host_filter":{"fqdn_host_pattern":"","ctype":"testing_dispatch","host_pattern":""},"period":"100ms","default_employer":"default","bp_description":"","operator_id":"default","freshness":"1m","groupping_attributes":[],"taxi_config_settings":""}',
false
);

INSERT INTO rt_background_settings
(bp_name, bp_type, bp_settings, bp_enabled)
VALUES
(
'supply_reservation',
'supply_reservation',
'{"bp_description":"","groupping_attributes":[],"host_filter":{"fqdn_host_pattern":"","ctype":"testing_platform","host_pattern":""},"period":"10s","taxi_config_settings":"","freshness":"1m","notifier_name":"null"}',
false
);

INSERT INTO tag_descriptions (name, class_name, tag_description_object, deprecated, description, explicit_unique_policy) VALUES ('yd_new_supply_promise', 'supply_promise_tag', '{"operator_id":"yd_new","unique_policy":"non_unique","external_options":[],"description":"","default_days_planned_count":7,"explicit_unique_policy":"non_unique"}', false, '', 'non_unique');
INSERT INTO tag_descriptions (name, class_name, tag_description_object, deprecated, description, explicit_unique_policy) VALUES ('yd_new_supply_promise_reservation', 'supply_reservation_tag', '{"unique_policy":"non_unique","description":"description","explicit_unique_policy":"non_unique"}', false, 'description', 'non_unique');

INSERT INTO employers (employer_code, employer_type, employer_meta) VALUES ('testAPI', 'default', 'EiAzOWM1YjlkNzVlYzY0NDdiYjYxZWJiZTExYWFhODFmMhoO0J7QntCeIHRlc3RBUEkiCHN0YW5kYXJkKgx0ZXN0QVBJLW1haW4wFDoKNzcxNjc2MDMwMUABSgE7UgBaEggAEAAYACDIASjIATDoBzjIAWIiY29ycC50ZXN0cGFydG5lcmFwaTczOTYyQHlhbmRleC5ydWiV0rXuAXIMdGVzdF9jb21tZW50eIOMjZ4CggEWCg7QntCe0J4gdGVzdEFQSRIAGgAiAIgBAA==');

INSERT INTO stations (station_name, station_id, operator_id, operator_station_id, station_meta, revision, enabled_in_platform, need_synchronization) VALUES ('улица Электродная', 'e03f0622-92d5-4934-bed7-557937ffe33f', 'testAPI', 'brt-main', 'ChwNQwEXQhWdA19CGYZWJ2co4EJAITbLZaNz4EtAGAEitgEKDNCg0L7RgdGB0LjRjxIM0JzQvtGB0LrQstCwGgzQnNC+0YHQutCy0LAiDNCc0L7RgdC60LLQsDoh0K3Qu9C10LrRgtGA0L7QtNC90LDRjyDRg9C70LjRhtCwQgUy0YEyOIIBG9Ce0YHQvdC+0LLQvdC+0Lkg0YHQutC70LDQtIoBL9GD0LvQuNGG0LAg0K3Qu9C10LrRgtGA0L7QtNC90LDRjywgMiwg0YHRgtGAIDI4kAHVATIV0J7QntCeINCR0LDRgNC40YHRgtCwUABaCwoJGAAgtxIofzADYgsKCRgAILQQKH8wA2oAegCIAQCYAQCyAQC6AQl3YXJlaG91c2U=', 590004978, true, true);
INSERT INTO stations (station_name, station_id, operator_id, operator_station_id, station_meta, revision, enabled_in_platform, need_synchronization) VALUES ('Основная станция для тестирования', '7c4054cd-d768-4062-8f8d-d0c9b3c8c4e8', 'testAPI', 'testMain', 'ChwNQwEXQhWdA19CGYZWJ2co4EJAITbLZaNz4EtAGAEikgEKDNCg0L7RgdGB0LjRjxIM0JzQvtGB0LrQstCwGgzQnNC+0YHQutCy0LAiDNCc0L7RgdC60LLQsDoh0K3Qu9C10LrRgtGA0L7QtNC90LDRjyDRg9C70LjRhtCwQgUy0YEyOIoBKdGD0Lsg0K3Qu9C10LrRgtGA0L7QtNC90LDRjywgMiwg0YHRgtGAIDI4kAHVATI/0J7RgdC90L7QstC90LDRjyDRgdGC0LDQvdGG0LjRjyDQtNC70Y8g0YLQtdGB0YLQuNGA0L7QstCw0L3QuNGPUABaCwoJGGQgtxIofzADYgsKCRhkILcSKH8wA2oQCOgHEJBOGJBOIJBOKLDqAXoAiAEBmAEAsgEAugEJd2FyZWhvdXNlyAEA', 616646459, true, true);
INSERT INTO stations (station_name, station_id, operator_id, operator_station_id, station_meta, revision, enabled_in_platform, need_synchronization) VALUES ('Москва, Новинский бульвар, 8', '2c20f2d5-2d02-46a9-9ca5-f5fb0e3c0d4f', 'testAPI', 'testAPI-25', 'ChwNp1YWQhVXAV9CGdVCyeTUykJAITGUE+0q4EtAGAEilwEKDNCg0L7RgdGB0LjRjxIM0JzQvtGB0LrQstCwGgzQnNC+0YHQutCy0LAiDNCc0L7RgdC60LLQsDoh0J3QvtCy0LjQvdGB0LrQuNC5INCx0YPQu9GM0LLQsNGAQgE4igEy0JzQvtGB0LrQstCwLCDQndC+0LLQuNC90YHQutC40Lkg0LHRg9C70YzQstCw0YAsIDiQAdUBMitD0LrQu9Cw0LQg0KLQtdGB0YLQvtCy0YvQuSDQutC70LjQtdC90YIgQVBJUABaCwoJGGQgtxIofzADYgsKCRhkILcSKH8wA2oAegCIAQGYAQA=', 563484669, true, true);

INSERT INTO station_tags (object_id, class_name, tag_name, tag_object, comments) VALUES ('2c20f2d5-2d02-46a9-9ca5-f5fb0e3c0d4f', 'supply_promise_tag', 'yd_new_supply_promise', 'CugBQ2hjeU16b3pNQ3N3TXpvd01DOHlNem8xTUNzd016b3dNQklmQ0FVUUFSb0ZNakU2TURBaURXUnBjbVZqZEY5dFlYSm5hVzRxQXkwMWN6SnNDakVLQjNOMFlYUnBiMjRhSmdva1pUZGhPRGMzWW1ZdFl6UTJNaTAwWWpFNUxXRXdPVEV0WW1Oa05tWmhabVV5T1RobUVoUXJNVG82TURnNk1EQXJNRE02TURBdkt6TXdiU0RvQnlvU2FXNTBaWEoyWVd4ZmQybDBhRjltWldWek1BQkFmMUlBWWdRSUFCQUFRQVZTQUE9PQ==', 'test');
