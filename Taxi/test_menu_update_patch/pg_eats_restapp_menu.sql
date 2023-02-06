INSERT INTO eats_restapp_menu.menu_categories(hash, json, origin_id)
VALUES ('cGijaeNvGeqgE3KXkgnbyA', '{"origin_id":"103263","name":"Завтрак","sort":130,"available":true,"legacy_id":123}', '103263'),
       ('7OprL8pisQH9nuaEavPqaA', '{"origin_id":"103265","name":"Закуски","sort":160,"available":true,"legacy_id":567}', '103265');

INSERT INTO eats_restapp_menu.menu_to_categories(hash, hashes)
VALUES ('Jly24hdsOplLFU1pwvXZRA', ARRAY['7OprL8pisQH9nuaEavPqaA', 'cGijaeNvGeqgE3KXkgnbyA']);

INSERT INTO eats_restapp_menu.menu_item_data_bases(hash, json)
VALUES ('7lTf-KMko8ztWQRe5Uvq5g', '{"name":"Сметана 20%","description":"","weight":{"value":"50","unit":"г"}}'),
       ('KuZBq6IrxmkJ7SayDAKukQ', '{"name":"Сухофрукты","description":"","weight":{"value":"35","unit":"г"}}');

INSERT INTO eats_restapp_menu.menu_item_data(hash, json)
VALUES ('wYQ4mli-PCdUK5abj6d_1A', '{"origin_id":"1234595","category_origin_ids":["103263"],"price":"100","vat":"0","sort":100,"legacy_id":37660168,"available":true,"pictures":[{"avatarnica_identity":"1368744/9d2253f1d40f86ff4e525e998f49dfca"}],"adult":false,"ordinary":true,"choosable":true,"shipping_types":["delivery","pickup"]}'),
       ('1p5HU_vkq9xx0inmbj0e9A', '{"origin_id":"1234583","category_origin_ids":["103263"],"price":"100","vat":"0","sort":100,"legacy_id":37660163,"available":true,"pictures":[{"avatarnica_identity":"1370147/36ca994761eb1fd00066ac634c96e0d9"}],"adult":true,"ordinary":false,"choosable":false,"shipping_types":["delivery","pickup"]}');

INSERT INTO eats_restapp_menu.menu_options_bases
VALUES ('11FxOYiYfpMxmANj4kGJzg', '[]');

INSERT INTO eats_restapp_menu.menu_options
VALUES('11FxOYiYfpMxmANj4kGJzg', '[]');

INSERT INTO eats_restapp_menu.menu_items(hash, data_base_hash, data_hash, options_base_hash, options_hash, origin_id)
VALUES ('2UQ6wQn8GWTNCqWu7due6g', '7lTf-KMko8ztWQRe5Uvq5g', 'wYQ4mli-PCdUK5abj6d_1A', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234595'),
       ('E-OCogy5OchwoFkQBBwUNQ', 'KuZBq6IrxmkJ7SayDAKukQ', '1p5HU_vkq9xx0inmbj0e9A', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234583');

INSERT INTO eats_restapp_menu.menu_to_items(hash, hashes)
VALUES ('TqjC5e1bquH7XSjQ25GSRg', ARRAY['2UQ6wQn8GWTNCqWu7due6g', 'E-OCogy5OchwoFkQBBwUNQ']);

INSERT INTO eats_restapp_menu.menus(place_id, items_hash, categories_hash, origin, status, errors_json)
VALUES (109151, 'TqjC5e1bquH7XSjQ25GSRg', 'Jly24hdsOplLFU1pwvXZRA', 'user_generated', 'applied', NULL);

INSERT INTO eats_restapp_menu.revision_transitions(place_id, old_revision, menu_id)
VALUES (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 1);
