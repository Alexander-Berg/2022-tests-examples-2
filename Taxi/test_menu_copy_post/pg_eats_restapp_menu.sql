INSERT INTO eats_restapp_menu.menu_categories(hash, json, origin_id)
VALUES ('cGijaeNvGeqgE3KXkgnbyA', '{"origin_id":"103263","name":"Завтрак","sort":130,"available":true}', '103263'),
       ('7OprL8pisQH9nuaEavPqaA', '{"origin_id":"103265","name":"Закуски","sort":160,"available":true}', '103265');

INSERT INTO eats_restapp_menu.menu_to_categories(hash, hashes)
VALUES ('Jly24hdsOplLFU1pwvXZRA', ARRAY['cGijaeNvGeqgE3KXkgnbyA', '7OprL8pisQH9nuaEavPqaA']);

INSERT INTO eats_restapp_menu.menu_item_data_bases(hash, json)
VALUES ('3DYMsodJhgctIqBPqPB2sg', '{"name":"Сметана 20%","description":"","measure":50.0,"measureUnit":"г"}'),
       ('bKrzofHPCzLC3jbJJ6vSHg', '{"name":"Сухофрукты","description":"","measure":35.0,"measureUnit":"г"}');

INSERT INTO eats_restapp_menu.menu_item_data(hash, json)
VALUES ('J5KM3ksN3atJuLawCpHzZQ', '{"origin_id":"1234595","category_origin_ids":["103263"],"price":"100","vat":"0","sort":100,"legacy_id":37660168,"available":true,"pictures":[{"avatarnica_identity":"1368744/9d2253f1d40f86ff4e525e998f49dfca"}]}'),
       ('bZh1-urGAsvDbG-yHfVQKw', '{"origin_id":"1234583","category_origin_ids":["103263"],"price":"100","vat":"0","sort":100,"legacy_id":37660163,"available":true,"pictures":[{"avatarnica_identity":"1370147/36ca994761eb1fd00066ac634c96e0d9"}]}');

INSERT INTO eats_restapp_menu.menu_options_bases
VALUES ('11FxOYiYfpMxmANj4kGJzg', '[]');

INSERT INTO eats_restapp_menu.menu_options
VALUES('11FxOYiYfpMxmANj4kGJzg', '[]');

INSERT INTO eats_restapp_menu.menu_items(hash, data_base_hash, data_hash, options_base_hash, options_hash, origin_id)
VALUES ('1OGZuMFJeUD8yFaSJXdg_w', '3DYMsodJhgctIqBPqPB2sg', 'J5KM3ksN3atJuLawCpHzZQ', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234595'),
       ('38jcShGOQU43tEy-2okKLg', 'bKrzofHPCzLC3jbJJ6vSHg', 'bZh1-urGAsvDbG-yHfVQKw', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234583');

INSERT INTO eats_restapp_menu.menu_to_items(hash, hashes)
VALUES ('cth27DbS0H_aZNL8gq_MGA', ARRAY['1OGZuMFJeUD8yFaSJXdg_w', '38jcShGOQU43tEy-2okKLg']);

INSERT INTO eats_restapp_menu.menus(place_id, items_hash, categories_hash, origin, status, errors_json)
VALUES (109151, 'cth27DbS0H_aZNL8gq_MGA', 'Jly24hdsOplLFU1pwvXZRA', 'user_generated', 'applied', NULL),
       (109152, 'cth27DbS0H_aZNL8gq_MGA', 'Jly24hdsOplLFU1pwvXZRA', 'user_generated', 'applied', NULL),
       (109153, 'cth27DbS0H_aZNL8gq_MGA', 'Jly24hdsOplLFU1pwvXZRA', 'user_generated', 'applied', NULL),
       (109154, 'cth27DbS0H_aZNL8gq_MGA', 'Jly24hdsOplLFU1pwvXZRA', 'user_generated', 'applied', NULL);

SELECT setval('eats_restapp_menu.menus_id_seq', 10, true);
