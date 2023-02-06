INSERT INTO eats_restapp_menu.menu_content(place_id, menu_hash, menu_json)
VALUES (109151, 'same_hash', '
{
    "categories": [
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        },
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "nutrients": {
                "calories": "66.66",
                "carbohydrates": "99.99",
                "fats": "88.88",
                "is_deactivated": false,
                "proteins": "77.77"
            },
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ]
  }
'),
(109151, 'base_hash', '{"categories": [], "items": []}');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, base_revision, origin, status, menu_hash, created_at)
VALUES (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 'base_revision_hash', 'user_generated', 'processing', 'some_hash', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ),
(109151, 'base_revision_hash', NULL, 'external', 'not_applicable', 'base_hash', '2021-04-04T04:04:04.000+00:00'::TIMESTAMPTZ);


INSERT INTO eats_restapp_menu.menu_categories(hash, json, origin_id)
VALUES ('9xoXTI6nrE0D_cCXSj4eFA', '{"origin_id":"103263","name":"Завтрак","sort":130,"available":true}', '103263'),
       ('ZZkqt9Nu2AWK4_t5W0-s5g', '{"origin_id":"103265","name":"Закуски","sort":160,"available":true}', '103265');

INSERT INTO eats_restapp_menu.menu_to_categories(hash, hashes)
VALUES ('xVFstG2qgq8l1xT1PpIiRQ', ARRAY['9xoXTI6nrE0D_cCXSj4eFA', 'ZZkqt9Nu2AWK4_t5W0-s5g']),
       ('1231231231231231231231', ARRAY[]::text[]);

INSERT INTO eats_restapp_menu.menu_item_data_bases(hash, json)
VALUES ('3DYMsodJhgctIqBPqPB2sg', '{"name":"Сметана 20%","description":"","weight":{"value":"50","unit":"г"}}'),
       ('bKrzofHPCzLC3jbJJ6vSHg', '{"name":"Сухофрукты","description":"","weight":{"value":"35","unit":"г"}}');

INSERT INTO eats_restapp_menu.menu_item_data(hash, json)
VALUES ('J5KM3ksN3atJuLawCpHzZQ', '{"origin_id":"1234595","category_origin_ids":["103263"],"price":"100","vat":"0","sort":100,"legacy_id":37660168,"available":true,"adult":true,"shipping_types":["delivery","pickup"],"pictures":[{"avatarnica_identity":"1368744/9d2253f1d40f86ff4e525e998f49dfca"}]}'),
       ('bZh1-urGAsvDbG-yHfVQKw', '{"origin_id":"1234583","category_origin_ids":["103263"],"price":"100","vat":"0","sort":100,"legacy_id":37660163,"available":true,"adult":true,"shipping_types":["delivery","pickup"],"pictures":[{"avatarnica_identity":"1370147/36ca994761eb1fd00066ac634c96e0d9"}]}');

INSERT INTO eats_restapp_menu.menu_options_bases
VALUES ('11FxOYiYfpMxmANj4kGJzg', '[]'),
       ('PCibjWDrCRaCsOO-VTTQDg', '[{"name":"Дополнительные ингредиенты","options":[{"name":"Малина протертая с сахаром","min_amount":0,"max_amount":1,"multiplier":1}],"min_selected_options":0,"max_selected_options":6}]');

INSERT INTO eats_restapp_menu.menu_options
VALUES ('11FxOYiYfpMxmANj4kGJzg', '[]'),
       ('V8sB7DlXxN7V4mW4RLlIMg', '[{"origin_id":"2716078","options":[{"origin_id":"26778790","price":"100","available":true,"legacy_id":172641802}],"sort":100,"legacy_id":21171787}]');

INSERT INTO eats_restapp_menu.menu_items(hash, data_base_hash, data_hash, options_base_hash, options_hash, origin_id)
VALUES ('P6aKASeUld_5YQ04w1k8Nw', '3DYMsodJhgctIqBPqPB2sg', 'J5KM3ksN3atJuLawCpHzZQ', 'PCibjWDrCRaCsOO-VTTQDg', 'V8sB7DlXxN7V4mW4RLlIMg', '1234595'),
       ('38jcShGOQU43tEy-2okKLg', 'bKrzofHPCzLC3jbJJ6vSHg', 'bZh1-urGAsvDbG-yHfVQKw', '11FxOYiYfpMxmANj4kGJzg', '11FxOYiYfpMxmANj4kGJzg', '1234583');

INSERT INTO eats_restapp_menu.menu_to_items(hash, hashes)
VALUES ('cth27DbS0H_aZNL8gq_MGA', ARRAY['P6aKASeUld_5YQ04w1k8Nw', '38jcShGOQU43tEy-2okKLg']),
       ('1231231231231231231231', ARRAY[]::text[]);

INSERT INTO eats_restapp_menu.menus(id, base_id, place_id, items_hash, categories_hash, origin, status, errors_json)
VALUES (1, null, 109151, '1231231231231231231231', '1231231231231231231231', 'external', 'not_applicable', NULL),
       (2, 1, 109151, 'cth27DbS0H_aZNL8gq_MGA', 'xVFstG2qgq8l1xT1PpIiRQ', 'user_generated', 'applied', NULL);

SELECT setval('eats_restapp_menu.menus_id_seq', 2, true);

INSERT INTO eats_restapp_menu.revision_transitions(place_id, old_revision, menu_id)
VALUES (109151, 'base_revision_hash', 1),
       (109151, 'OTk5LjE1Nzc5MDk3MDEwMDAuWFla', 2);
