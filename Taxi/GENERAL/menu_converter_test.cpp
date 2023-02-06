#include <userver/utest/utest.hpp>

#include "menu_converter.hpp"

namespace eats_restapp_menu::utils::tests {

std::string json_old = R"#--(
    {
    "items": [
        {
        "id": "Завтрак_Гречневая каша с авокадо",
        "vat": -1,
        "name": "Гречневая каша с авокадо и яйцом пашот",
        "price": 410.0,
        "images": [
            {
            "url": "https://eda.yandex/images/1368744/74d9c4647d1f89d3a65df806eed5fba5.jpeg"
            }
        ],
        "measure": 270.0,
        "available": true,
        "sortOrder": 101,
        "categoryId": "Завтрак",
        "menuItemId": 31280765,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1368744/74d9c4647d1f89d3a65df806eed5fba5-80x80.jpeg"
            }
        ],
        "description": "Гречневая каша, яйцо, авокадо, семена подсолнечника, голландский крем, петрушка",
        "measureUnit": "г",
        "modifierGroups": [
            {
            "id": "kgt27cab-yn89is7qjgk-edr6vt97p1i",
            "name": "Добавки",
            "modifiers": [
                {
                "id": "kgt2825m-6mrrz0s62vt-vgrra1wxwbe",
                "name": "Яйцо пашот",
                "price": 55.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 175775487
                },
                {
                "id": "kgt27ft7-9a4gz2bz5pd-j13vmf0jaqq",
                "name": "Креветки жареные (50 г)",
                "price": 300.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698587
                },
                {
                "id": "kgt28fgq-8nzf2uvkrb7-5x1bhthcstr",
                "name": "Авокадо (20 г)",
                "price": 90.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698592
                }
            ],
            "sortOrder": 100,
            "maxSelectedModifiers": 3,
            "minSelectedModifiers": 0,
            "menuItemOptionGroupId": 21737032
            }
        ]
        },
        {
        "id": "Завтрак_Сырники со сметаной и домашним вареньем",
        "vat": -1,
        "name": "Сырники со сметаной и домашним вареньем",
        "price": 460.0,
        "images": [
            {
            "url": "https://eda.yandex/images/1380157/90a12a4fd1c9c7b01f87c430b2e543ab.jpeg"
            }
        ],
        "measure": 240.0,
        "available": true,
        "sortOrder": 101,
        "categoryId": "Завтрак",
        "menuItemId": 31280770,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1380157/90a12a4fd1c9c7b01f87c430b2e543ab-80x80.jpeg"
            }
        ],
        "description": "Творог, мука пшеничная, масло, сметана, мята, сахарная пудра",
        "measureUnit": "г",
        "modifierGroups": [
            {
            "id": "10635280",
            "name": "Варенье на выбор",
            "modifiers": [
                {
                "id": "86520255",
                "name": "Вишневое",
                "price": 0.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 86520255
                },
                {
                "id": "86520260",
                "name": "Яблочно-брусничное",
                "price": 0.0,
                "available": false,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 86520260
                },
                {
                "id": "86520265",
                "name": "Клубничное",
                "price": 0.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 86520265
                }
            ],
            "sortOrder": 100,
            "maxSelectedModifiers": 1,
            "minSelectedModifiers": 1,
            "menuItemOptionGroupId": 10635280
            },
            {
            "id": "kgt29bo2-f19t1ri6535-sh32w8phqen",
            "name": "Добавки",
            "modifiers": [
                {
                "id": "kgt29eub-oyb4sglbfwq-hxxdt5tdq2f",
                "name": "Вишневое (50 г)",
                "price": 50.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698487
                },
                {
                "id": "kgt29t5q-2gl7bnw8dnp-z4imyhbibjh",
                "name": "Яблочно-брусничное (50 г)",
                "price": 50.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698492
                },
                {
                "id": "kgt2a2q9-iwretgfpcip-shcy5s0pc3f",
                "name": "Клубничное (50 г)",
                "price": 50.0,
                "available": true,
                "maxAmount": 0,
                "minAmount": 0,
                "menuItemOptionId": 1674698497
                },
                {
                "id": "kgt2afz7-fgy8ih1muh-hg79gqr9zp6",
                "name": "Молоко сгущенное (50 г)",
                "price": 100.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698502
                },
                {
                "id": "kgt2avmi-i4lij05iv-b2zzshlwfb",
                "name": "Сметана (50 г)",
                "price": 175.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698507
                }
            ],
            "sortOrder": 100,
            "maxSelectedModifiers": 5,
            "minSelectedModifiers": 0,
            "menuItemOptionGroupId": 123895102
            }
        ]
        },
        {
        "id": "Салаты_Салат с брокколи",
        "vat": -1,
        "name": "Салат Зеленый с брокколи, авокадо и спаржей",
        "price": 690.0,
        "images": [
            {
            "url": "https://eda.yandex/images/1380157/a508c2fd11203ada9d80b3be8337d75e.jpeg"
            }
        ],
        "measure": 270.0,
        "available": true,
        "sortOrder": 101,
        "categoryId": "Салаты",
        "menuItemId": 31280780,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1380157/a508c2fd11203ada9d80b3be8337d75e-80x80.jpeg"
            }
        ],
        "description": "Брокколи, авокадо, заправка имбирная, огурцы, шпинат, киноа, спаржа, сельдерей, томаты вяленые, горох зеленый, масло растительное",
        "measureUnit": "г",
        "modifierGroups": [
            {
            "id": "kgt2djj3-wwdsohyk4e-ag9s22oeroq",
            "name": "Добавки",
            "modifiers": [
                {
                "id": "kgt2dnuo-hwoq82bny9-qhyx0nfz52",
                "name": "Креветки жареные (50 г)",
                "price": 450.0,
                "available": true,
                "maxAmount": 1,
                "minAmount": 0,
                "menuItemOptionId": 1674698597
                }
            ],
            "sortOrder": 100,
            "maxSelectedModifiers": 1,
            "minSelectedModifiers": 0,
            "menuItemOptionGroupId": 21737042
            }
        ]
        },
        {
        "id": "Салаты_Салат из рукколы и тигровых креветок",
        "vat": -1,
        "name": "Салат из рукколы и тигровых креветок",
        "price": 750.0,
        "images": [
            {
            "url": "https://eda.yandex/images/1387779/79f33a489f265470db07d20710647a85.jpeg"
            }
        ],
        "measure": 210.0,
        "available": true,
        "sortOrder": 101,
        "categoryId": "Салаты",
        "menuItemId": 31280785,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1387779/79f33a489f265470db07d20710647a85-80x80.jpeg"
            }
        ],
        "description": "Рукола, креветки, черри, авокадо, ремулад из сельдерея, огурцы, грана падано, масло бальзамическое, укроп, соль морская, перец черный (горошек), масло растительное, масло чили, базилик",
        "measureUnit": "г",
        "modifierGroups": []
        },
        {
        "id": "31280790",
        "vat": -1,
        "name": "Салат из томатов и авокадо со страчателлой",
        "price": 790.0,
        "images": [
            {
            "url": "https://eda.yandex/images/1387779/b20de8abd58e311165942b4715317d01.jpeg"
            }
        ],
        "measure": 250.0,
        "available": true,
        "sortOrder": 100,
        "categoryId": "Салаты",
        "menuItemId": 31280790,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1387779/b20de8abd58e311165942b4715317d01-80x80.jpeg"
            }
        ],
        "description": "Помидоры розовые, страчателла, авокадо, горошек, кинза, базилик, соль, перец",
        "measureUnit": "г",
        "modifierGroups": []
        },
        {
        "id": "Горячие блюда_Домашние пельмени с телятиной",
        "vat": -1,
        "name": "Домашние пельмени с телятиной",
        "price": 490.0,
        "images": [
            {
            "url": "https://eda.yandex/images/1387779/018efaea6a98c4e2600db25d7b6ba359.jpeg"
            }
        ],
        "measure": 270.0,
        "available": true,
        "sortOrder": 101,
        "categoryId": "Горячие блюда",
        "menuItemId": 31280795,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1387779/018efaea6a98c4e2600db25d7b6ba359-80x80.jpeg"
            }
        ],
        "description": "Со сметаной, петрушкой и солью",
        "measureUnit": "г",
        "modifierGroups": []
        }
    ],
    "categories": [
        {
        "id": "Завтрак",
        "name": "Завтрак",
        "available": true,
        "sortOrder": 140,
        "reactivatedAt": "2022-04-14T05:00:00+00:00"
        },
        {
        "id": "Салаты",
        "name": "Салаты",
        "available": true,
        "sortOrder": 160
        },
        {
        "id": "Горячие блюда",
        "name": "Горячие блюда",
        "available": true,
        "sortOrder": 370
        }
    ]
    }
   )#--";

std::string json_new = R"#--(
    {
    "categories": [
        {
        "origin_id": "Завтрак",
        "name": "Завтрак",
        "available": true,
        "sort": 140,
        "reactivate_at": "2022-04-14T05:00:00+00:00"
        },
        {
        "origin_id": "Салаты",
        "name": "Салаты",
        "available": true,
        "sort": 160
        },
        {
        "origin_id": "Горячие блюда",
        "name": "Горячие блюда",
        "available": true,
        "sort": 370
        }
    ],
    "items": [
        {
        "origin_id": "Завтрак_Гречневая каша с авокадо",
        "vat": "-1",
        "name": "Гречневая каша с авокадо и яйцом пашот",
        "price": "410",
        "pictures": [
            {
            "url": "https://eda.yandex/images/1368744/74d9c4647d1f89d3a65df806eed5fba5.jpeg"
            }
        ],
        "available": true,
        "sort": 101,
        "category_origin_ids": [
            "Завтрак"
        ],
        "legacy_id": 31280765,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1368744/74d9c4647d1f89d3a65df806eed5fba5-80x80.jpeg"
            }
        ],
        "description": "Гречневая каша, яйцо, авокадо, семена подсолнечника, голландский крем, петрушка",
        "options_groups": [
            {
            "origin_id": "kgt27cab-yn89is7qjgk-edr6vt97p1i",
            "name": "Добавки",
            "options": [
                {
                "origin_id": "kgt2825m-6mrrz0s62vt-vgrra1wxwbe",
                "name": "Яйцо пашот",
                "price": "55",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 175775487
                },
                {
                "origin_id": "kgt27ft7-9a4gz2bz5pd-j13vmf0jaqq",
                "name": "Креветки жареные (50 г)",
                "price": "300",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698587
                },
                {
                "origin_id": "kgt28fgq-8nzf2uvkrb7-5x1bhthcstr",
                "name": "Авокадо (20 г)",
                "price": "90",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698592
                }
            ],
            "sort": 100,
            "max_selected_options": 3,
            "min_selected_options": 0,
            "legacy_id": 21737032
            }
        ],
        "weight": {
            "value": "270",
            "unit": "г"
        }
        },
        {
        "origin_id": "Завтрак_Сырники со сметаной и домашним вареньем",
        "vat": "-1",
        "name": "Сырники со сметаной и домашним вареньем",
        "price": "460",
        "pictures": [
            {
            "url": "https://eda.yandex/images/1380157/90a12a4fd1c9c7b01f87c430b2e543ab.jpeg"
            }
        ],
        "available": true,
        "sort": 101,
        "category_origin_ids": [
            "Завтрак"
        ],
        "legacy_id": 31280770,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1380157/90a12a4fd1c9c7b01f87c430b2e543ab-80x80.jpeg"
            }
        ],
        "description": "Творог, мука пшеничная, масло, сметана, мята, сахарная пудра",
        "options_groups": [
            {
            "origin_id": "10635280",
            "name": "Варенье на выбор",
            "options": [
                {
                "origin_id": "86520255",
                "name": "Вишневое",
                "price": "0",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 86520255
                },
                {
                "origin_id": "86520260",
                "name": "Яблочно-брусничное",
                "price": "0",
                "available": false,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 86520260
                },
                {
                "origin_id": "86520265",
                "name": "Клубничное",
                "price": "0",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 86520265
                }
            ],
            "sort": 100,
            "max_selected_options": 1,
            "min_selected_options": 1,
            "legacy_id": 10635280
            },
            {
            "origin_id": "kgt29bo2-f19t1ri6535-sh32w8phqen",
            "name": "Добавки",
            "options": [
                {
                "origin_id": "kgt29eub-oyb4sglbfwq-hxxdt5tdq2f",
                "name": "Вишневое (50 г)",
                "price": "50",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698487
                },
                {
                "origin_id": "kgt29t5q-2gl7bnw8dnp-z4imyhbibjh",
                "name": "Яблочно-брусничное (50 г)",
                "price": "50",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698492
                },
                {
                "origin_id": "kgt2a2q9-iwretgfpcip-shcy5s0pc3f",
                "name": "Клубничное (50 г)",
                "price": "50",
                "available": true,
                "max_amount": 0,
                "min_amount": 0,
                "legacy_id": 1674698497
                },
                {
                "origin_id": "kgt2afz7-fgy8ih1muh-hg79gqr9zp6",
                "name": "Молоко сгущенное (50 г)",
                "price": "100",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698502
                },
                {
                "origin_id": "kgt2avmi-i4lij05iv-b2zzshlwfb",
                "name": "Сметана (50 г)",
                "price": "175",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698507
                }
            ],
            "sort": 100,
            "max_selected_options": 5,
            "min_selected_options": 0,
            "legacy_id": 123895102
            }
        ],
        "weight": {
            "value": "240",
            "unit": "г"
        }
        },
        {
        "origin_id": "Салаты_Салат с брокколи",
        "vat": "-1",
        "name": "Салат Зеленый с брокколи, авокадо и спаржей",
        "price": "690",
        "pictures": [
            {
            "url": "https://eda.yandex/images/1380157/a508c2fd11203ada9d80b3be8337d75e.jpeg"
            }
        ],
        "available": true,
        "sort": 101,
        "category_origin_ids": [
            "Салаты"
        ],
        "legacy_id": 31280780,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1380157/a508c2fd11203ada9d80b3be8337d75e-80x80.jpeg"
            }
        ],
        "description": "Брокколи, авокадо, заправка имбирная, огурцы, шпинат, киноа, спаржа, сельдерей, томаты вяленые, горох зеленый, масло растительное",
        "options_groups": [
            {
            "origin_id": "kgt2djj3-wwdsohyk4e-ag9s22oeroq",
            "name": "Добавки",
            "options": [
                {
                "origin_id": "kgt2dnuo-hwoq82bny9-qhyx0nfz52",
                "name": "Креветки жареные (50 г)",
                "price": "450",
                "available": true,
                "max_amount": 1,
                "min_amount": 0,
                "legacy_id": 1674698597
                }
            ],
            "sort": 100,
            "max_selected_options": 1,
            "min_selected_options": 0,
            "legacy_id": 21737042
            }
        ],
        "weight": {
            "value": "270",
            "unit": "г"
        }
        },
        {
        "origin_id": "Салаты_Салат из рукколы и тигровых креветок",
        "vat": "-1",
        "name": "Салат из рукколы и тигровых креветок",
        "price": "750",
        "pictures": [
            {
            "url": "https://eda.yandex/images/1387779/79f33a489f265470db07d20710647a85.jpeg"
            }
        ],
        "available": true,
        "sort": 101,
        "category_origin_ids": [
            "Салаты"
        ],
        "legacy_id": 31280785,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1387779/79f33a489f265470db07d20710647a85-80x80.jpeg"
            }
        ],
        "description": "Рукола, креветки, черри, авокадо, ремулад из сельдерея, огурцы, грана падано, масло бальзамическое, укроп, соль морская, перец черный (горошек), масло растительное, масло чили, базилик",
        "options_groups": [],
        "weight": {
            "value": "210",
            "unit": "г"
        }
        },
        {
        "origin_id": "31280790",
        "vat": "-1",
        "name": "Салат из томатов и авокадо со страчателлой",
        "price": "790",
        "pictures": [
            {
            "url": "https://eda.yandex/images/1387779/b20de8abd58e311165942b4715317d01.jpeg"
            }
        ],
        "available": true,
        "sort": 100,
        "category_origin_ids": [
            "Салаты"
        ],
        "legacy_id": 31280790,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1387779/b20de8abd58e311165942b4715317d01-80x80.jpeg"
            }
        ],
        "description": "Помидоры розовые, страчателла, авокадо, горошек, кинза, базилик, соль, перец",
        "options_groups": [],
        "weight": {
            "value": "250",
            "unit": "г"
        }
        },
        {
        "origin_id": "Горячие блюда_Домашние пельмени с телятиной",
        "vat": "-1",
        "name": "Домашние пельмени с телятиной",
        "price": "490",
        "pictures": [
            {
            "url": "https://eda.yandex/images/1387779/018efaea6a98c4e2600db25d7b6ba359.jpeg"
            }
        ],
        "available": true,
        "sort": 101,
        "category_origin_ids": [
            "Горячие блюда"
        ],
        "legacy_id": 31280795,
        "thumbnails": [
            {
            "url": "https://eda.yandex/images/1387779/018efaea6a98c4e2600db25d7b6ba359-80x80.jpeg"
            }
        ],
        "description": "Со сметаной, петрушкой и солью",
        "options_groups": [],
        "weight": {
            "value": "270",
            "unit": "г"
        }
        }
    ]
    }
   )#--";

TEST(ConversionV1ToV2, Basic) {
  auto result = MenuConvertV1ToV2(formats::json::FromString(json_old));
  ASSERT_EQ(result, formats::json::FromString(json_new));
}

TEST(ConversionV2ToV1, Basic) {
  auto result = MenuConvertV2ToV1(formats::json::FromString(json_new));
  ASSERT_EQ(result, formats::json::FromString(json_old));
}

}  // namespace eats_restapp_menu::utils::tests
