#include <userver/crypto/base64.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include "revision.hpp"

namespace eats_restapp_menu::utils::tests {

TEST(SerializeDeserializeRevision, Basic) {
  models::RevisionHash data1{"MS4xNTc3OTA5NzAxMDAwLlRFU1RfU1RSSU5H"};
  models::RevisionHash data2{"MS4xNTc3OTA5NzAyMDAwLg"};
  models::RevisionHash data3{"OTk5LjE1Nzc5MDk3MDMwMDAuWFla"};

  Revision rev1{data1};
  Revision rev2{data2};
  Revision rev3{data3};

  EXPECT_EQ(rev1.Version(), 1);
  EXPECT_EQ(rev2.Version(), 1);
  EXPECT_EQ(rev3.Version(), 999);
  EXPECT_EQ(rev1.DateTime(),
            ::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"));
  EXPECT_EQ(rev2.DateTime(),
            ::utils::datetime::Stringtime("2020-01-01T20:15:02Z", "UTC"));
  EXPECT_EQ(rev3.DateTime(),
            ::utils::datetime::Stringtime("2020-01-01T20:15:03Z", "UTC"));
  EXPECT_EQ(rev1.MenuHash(), models::MenuHash{"TEST_STRING"});
  EXPECT_EQ(rev2.MenuHash(), models::MenuHash{""});
  EXPECT_EQ(rev3.MenuHash(), models::MenuHash{"XYZ"});

  EXPECT_EQ(rev1.RevisionHash(), data1);
  EXPECT_EQ(rev2.RevisionHash(), data2);
  EXPECT_EQ(rev3.RevisionHash(), data3);

  EXPECT_EQ(Revision{rev1.RevisionHash()}.RevisionHash(), data1);
  EXPECT_EQ(Revision{rev2.RevisionHash()}.RevisionHash(), data2);
  EXPECT_EQ(Revision{rev3.RevisionHash()}.RevisionHash(), data3);
}

TEST(CalculateMenuHash, Basic) {
  std::string json1 = R"#--(
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
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
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
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ]
  }
  )#--";

  // difference from json1: object fields rearranged
  std::string json2 = R"#--(
    {
    "items": [
        {
            "measure": 35,            "measureUnit": "г",            "sortOrder": 100,
            "modifierGroups": [],
            "id": "1234583",            "categoryId": "103263",
            "name": "Сухофрукты",            "description": "",
            "price": 100,            "vat": 0,
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        },
        {
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "price": 100,
            "vat": 0,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168,
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": ""
        }
    ],
    "categories": [
        {
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "id": "103263",
            "parentId": null,
            "available": true
        },
        {
            "sortOrder": 160, "available": true, "reactivatedAt": null,
            "parentId": null, "name": "Закуски",
            "id": "103265"
        }
    ]
  }
  )#--";

  // difference from json1: 103263 => 103262
  std::string json3 = R"#--(
    {
    "categories": [
        {
            "id": "103262",
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
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
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
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ]
  }
  )#--";

  Revision rev1{::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"),
                formats::json::FromString(json1)};
  Revision rev2{::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"),
                formats::json::FromString(json2)};
  Revision rev2_dttm{
      ::utils::datetime::Stringtime("2020-01-02T20:15:01Z", "UTC"),
      formats::json::FromString(json2)};
  Revision rev3{::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"),
                formats::json::FromString(json3)};

  EXPECT_EQ(rev1.MenuHash(), models::MenuHash{"F2jGDtjKNJjuaCk72RXcPA"});
  EXPECT_EQ(rev2.MenuHash(), models::MenuHash{"F2jGDtjKNJjuaCk72RXcPA"});
  EXPECT_EQ(rev2_dttm.MenuHash(), models::MenuHash{"F2jGDtjKNJjuaCk72RXcPA"});
  EXPECT_EQ(rev1, rev2);
  EXPECT_NE(rev1, rev2_dttm);
  EXPECT_NE(rev2, rev2_dttm);

  EXPECT_EQ(rev3.MenuHash(), models::MenuHash{"gVCX8f0JdTJCS4k6hg8ziQ"});
  EXPECT_NE(rev1, rev3);

  EXPECT_EQ(rev1.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTA5NzAxMDAwLkYyakdEdGpLTkpqdWFDazcyUlhjUEE"});
  EXPECT_EQ(rev2.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTA5NzAxMDAwLkYyakdEdGpLTkpqdWFDazcyUlhjUEE"});
  EXPECT_EQ(rev2_dttm.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTk2MTAxMDAwLkYyakdEdGpLTkpqdWFDazcyUlhjUEE"});
  EXPECT_EQ(rev3.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTA5NzAxMDAwLmdWQ1g4ZjBKZFRKQ1M0azZoZzh6aVE"});
}

TEST(CalculateMenuHash, Second) {
  std::string json1 = R"#--(
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
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
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
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ],
    "lastChange": "2021-08-12T14:35:08.551854+00:00"
  }
  )#--";

  // difference from json1: some junk on top level
  std::string json2 = R"#--(
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
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
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
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ],
    "lastChange": "2021-08-12T14:36:02.148457+00:00"
  }
  )#--";

  // difference from json1: item and categories order are different
  std::string json3 = R"#--(
    {
    "categories": [
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        },
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
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        }
    ]
  }
  )#--";

  Revision rev1{::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"),
                formats::json::FromString(json1)};
  Revision rev2{::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"),
                formats::json::FromString(json2)};
  Revision rev3{::utils::datetime::Stringtime("2020-01-01T20:15:01Z", "UTC"),
                formats::json::FromString(json3)};

  EXPECT_EQ(rev1.MenuHash(), models::MenuHash{"F2jGDtjKNJjuaCk72RXcPA"});
  EXPECT_EQ(rev2.MenuHash(), models::MenuHash{"F2jGDtjKNJjuaCk72RXcPA"});
  EXPECT_EQ(rev3.MenuHash(), models::MenuHash{"F2jGDtjKNJjuaCk72RXcPA"});

  EXPECT_EQ(rev1, rev2);
  EXPECT_EQ(rev1, rev3);
  EXPECT_EQ(rev2, rev3);

  EXPECT_EQ(rev1.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTA5NzAxMDAwLkYyakdEdGpLTkpqdWFDazcyUlhjUEE"});
  EXPECT_EQ(rev2.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTA5NzAxMDAwLkYyakdEdGpLTkpqdWFDazcyUlhjUEE"});
  EXPECT_EQ(rev3.RevisionHash(),
            models::RevisionHash{
                "MS4xNTc3OTA5NzAxMDAwLkYyakdEdGpLTkpqdWFDazcyUlhjUEE"});
}

}  // namespace eats_restapp_menu::utils::tests
