INSERT INTO eats_restapp_menu.menu_categories(hash, json, origin_id)
VALUES ('9xoXTI6nrE0D_cCXSj4eFA', '{"origin_id":"103263","name":"Завтрак","sort":130,"available":true}', '103263'),
       ('ZZkqt9Nu2AWK4_t5W0-s5g', '{"origin_id":"103265","name":"Закуски","sort":160,"available":true}', '103265');

INSERT INTO eats_restapp_menu.menu_to_categories(hash, hashes)
VALUES ('xVFstG2qgq8l1xT1PpIiRQ', ARRAY['9xoXTI6nrE0D_cCXSj4eFA', 'ZZkqt9Nu2AWK4_t5W0-s5g']),
       ('1231231231231231231231', ARRAY[]::text[]);

INSERT INTO eats_restapp_menu.menu_item_data_bases(hash, json)
VALUES ('3DYMsodJhgctIqBPqPB2sg', '{"name":"Сметана 20%","description":"","measure":50.0,"measureUnit":"г"}'),
       ('bKrzofHPCzLC3jbJJ6vSHg', '{"name":"Сухофрукты","description":"","measure":35.0,"measureUnit":"г"}');

INSERT INTO eats_restapp_menu.menu_item_data(hash, json)
VALUES ('J5KM3ksN3atJuLawCpHzZQ', '{"origin_id":"1234595","category_origin_ids":["103263"],"price":"100.0","vat":"0","sort":100,"legacy_id":37660168,"available":true,"pictures":[{"avatarnica_identity":"1368744/9d2253f1d40f86ff4e525e998f49dfca"}]}'),
       ('bZh1-urGAsvDbG-yHfVQKw', '{"origin_id":"1234583","category_origin_ids":["103263"],"price":"100.0","vat":"0","sort":100,"legacy_id":37660163,"available":true,"pictures":[{"avatarnica_identity":"1370147/36ca994761eb1fd00066ac634c96e0d9"}]}');

INSERT INTO eats_restapp_menu.menu_options_bases
VALUES ('11FxOYiYfpMxmANj4kGJzg', '[]');

INSERT INTO eats_restapp_menu.menu_options
VALUES('11FxOYiYfpMxmANj4kGJzg', '[]');

INSERT INTO eats_restapp_menu.menu_items(hash, data_base_hash, data_hash, options_base_hash, options_hash, origin_id)
VALUES ('1OGZuMFJeUD8yFaSJXdg_w', '3DYMsodJhgctIqBPqPB2sg', 'J5KM3ksN3atJuLawCpHzZQ', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234595'),
       ('38jcShGOQU43tEy-2okKLg', 'bKrzofHPCzLC3jbJJ6vSHg', 'bZh1-urGAsvDbG-yHfVQKw', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234583');

INSERT INTO eats_restapp_menu.menu_to_items(hash, hashes)
VALUES ('cth27DbS0H_aZNL8gq_MGA', ARRAY['1OGZuMFJeUD8yFaSJXdg_w', '38jcShGOQU43tEy-2okKLg']),
       ('1231231231231231231231', ARRAY[]::text[]);

INSERT INTO eats_restapp_menu.menus(id, base_id, place_id, items_hash, categories_hash, origin, status, errors_json, created_at, updated_at, applied_at)
VALUES (1, null, 109151, '1231231231231231231231', '1231231231231231231231', 'external', 'not_applicable', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (2, 1, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (3, 1, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'moderation', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (4, 3, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (5, 4, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (6, null, 109152, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'moderation', 'applied', '{"categories":[{"id":"103263","codes":[{"source":"moderation","code":"123","message":"CategoryMessage1"}]}]}', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (7, 5, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (8, 7, 109151, '1231231231231231231231', '1231231231231231231231', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (9, 8, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'moderation', 'applied',
        '{"categories":[{"id":"103263","codes":[{"source":"moderation","code":"123","message":"CategoryMessage1"}]},{"id":"323","codes":[{"source":"moderation","code":"333","message":"CategoryMessage2"}]}],'
        '"items":[{"id":"103263","codes":[{"source":"moderation","code":"555","message":"ItemMessage1"}]},{"id":"1234583","codes":[{"source":"moderation","code":"777","message":"ItemMessage2"}]}]}',
        '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (10, 9, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
       (11, 10, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ, '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ);

SELECT setval('eats_restapp_menu.menus_id_seq', 3, true);

INSERT INTO eats_restapp_menu.revision_transitions(place_id, old_revision, menu_id)
VALUES (109151, 'tr1', 1),
       (109151, 'tr2', 2),
       (109151, 'tr3', 3),
       (109151, 'tr4', 4),
       (109151, 'tr5', 5),
       (109152, 'tr6', 6),
       (109151, 'tr7', 7),
       (109151, 'tr8', 8),
       (109151, 'tr9', 9),
       (109151, 'tr10', 10),
       (109151, 'tr11', 11);
