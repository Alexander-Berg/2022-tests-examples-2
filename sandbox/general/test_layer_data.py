# -*- coding: utf-8 -*-

"""
GEOPROD-949
The module serves ONLY for generating of special maps layer requested by geo search project.
It is NOT for putting here arbitrary testing data of other modules.
"""

# noinspection SpellCheckingInspection
REAL_COMPANIES = [
    {
        "permalinks": {"nn": 1076558537, "msc": 1106972147},
        "name": "Интел",
        "url": "http://intel.ru",
    },
    {
        "permalinks": {"nn": 1705600225, "msc": 1124715036, "spb": 1043844566},
        "name": "Яндекс",
        "url": "http://yandex.ru",
    },
    {
        "permalinks": {"nn": 1195379217, "msc": 1213124576, "spb": 1183699244},
        "name": "Неткрэкер",
        "url": "http://netcracker.com",
    },
    {
        "permalinks": {"spb": 141902206096},
        "name": "JetBrains",
        "url": "https://jetbrains.ru",
    },
]

# noinspection SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection
TEST_ADVERTS = [
    {
        "id": 9223372036854775807,
        "type": "TEXT_ADVERT",
        "body": {
            "link": "yandex.ru",
            "text": "Только сегодня и только у нас!",
            "title": "Заголовок текстового о"
        }
    },
    {
        "id": 1,
        "type": "TEXT_ADVERT",
        "body": {
            "link": "text advert url",
            "text": "text advert text",
            "title": "text advert title"
        }
    },
    {
        "id": 3,
        "type": "TEXT_ADVERT",
        "body": {
            "link": "yandex.ru",
            "text": "Только сегодня и только у нас!",
            "title": "Заголовок текстового о"
        }
    },
    {
        "id": 4,
        "type": "PRODUCT_LIST",
        "body": []
    },
    {
        "id": 1,
        "type": "PRODUCT_LIST",
        "body": [
            {
                "url": "",
                "photo": {
                    "href": "https://avatars.mdst.yandex.net/get-tycoon/65823/"
                            "2a000001687f82b6e7a4ccb63151452d34f5/product",
                    "width": 240,
                    "height": 240
                },
                "price": "234 234 234",
                "title": "product1 title"
            },
            {
                "url": "",
                "photo": {
                    "href": "https://avatars.mdst.yandex.net/get-tycoon/65823/"
                            "2a000001687f82b6e7a4ccb63151452d34f5/product",
                    "width": 240,
                    "height": 240
                },
                "price": "234 234 234",
                "title": "product2 title"
            }
        ]
    },
    {
        "id": 3,
        "type": "PRODUCT_LIST",
        "body": []
    },
    {
        "id": 4,
        "type": "PROMOTION",
        "body": {}
    },
    {
        "id": 1,
        "type": "PROMOTION",
        "body": {
            "link": "https://l7test.yandex.ru/business/priority/promotion/4141?fakeuseruid=124497405",
            "image": {
                "href": "https://avatars.mdst.yandex.net/get-tycoon/5345/2a00000169a050ef03b48c37b2510803a2a5/banner",
                "width": 600,
                "height": 320
            },
            "date_to": "2025-04-21",
            "date_from": "2019-03-21",
            "description": "promo description",
            "announcement": "promo announcement"
        }
    },
    {
        "id": 3,
        "type": "PROMOTION",
        "body": {}
    },
    {
        "id": 5,
        "type": "BRANDING",
        "body": {}
    },
    {
        "id": 4,
        "type": "BRANDING",
        "body": {
            "branding_transformed": {}
        }
    },
    {
        "id": 1,
        "type": "BRANDING",
        "body": {
            "branding_transformed": {
                "fake_field": "Branding that should appear in ad_order"
            },
            "image": {
                "href": "https://avatars.mdst.yandex.net/get-tycoon/65823/2a00000168a927b4e88c3fd39bb7160b9454/orig",
                "width": 168,
                "height": 187
            },
            "fill_color": "#00E508",
            "border_color": "#E500BC"
        },
    },
    {
        "id": 6,
        "type": "CLICK_TO_ACTION",
        "body": {
            "title": "cta url",
            "link": "http://url"
        }
    },
    {
        "id": 7,
        "type": "HEADLINE",
        "body": {
            "logo": {
                "href": "https://avatars.mdst.yandex.net/get-tycoon/65823/2a0000016a4a2557104373f5444ad00b2879/logo",
                "width": 244,
                "height": 272
            },
            "photo": {
                "href": "https://avatars.mdst.yandex.net/get-tycoon/65823/2a0000016a4a2514cee810d303fdaa7b335f/main",
                "width": 420,
                "height": 272
            }
        }
    }
]

URL_SHOULD_RESOLVE = {
    "PROMOTION": {
        "id": 1,
        "body": {
            "link": "example.com?param=value"
        }
    },
    "PRODUCT_LIST": {
        "id": 2,
        "body": [{"url": "example.com"}]
    },
    "CLICK_TO_ACTION": {
        "id": 3,
        "body": {
            "link": "example.com?param=value#hash=mark"
        },
        "campaign_type": "SMVP"
    },
    "TEXT_ADVERT": {
        "id": 4,
        "body": {
            "link": "example.com",
            "text": "Только сегодня и только у нас!",
            "title": "Заголовок текстового о"
        }
    }
}

URL_SHOULD_NOT_RESOLVE = {
    "PROMOTION": {
        "id": 1,
        "body": {
            "link": "http://example.com?param=value"
        }
    },
    "PRODUCT_LIST": {
        "id": 2,
        "body": [{"url": "https://example.com"}]
    },
    "CLICK_TO_ACTION": {
        "id": 3,
        "body": {
            "link": "http://www.example.com?param=value#hash=mark"
        },
        "campaign_type": "SMVP"
    },
    "TEXT_ADVERT": {
        "id": 4,
        "body": {
            "link": "http://example.com"
        }
    }
}

BRANDING_BODY = {
    "image": {
        "href": "https://avatars.mds.yandex.net/get-tycoon/742106/2a00000173237d38f79690e1e15d05b7cc26/priority-branding",
        "width": 168,
        "height": 168
    },
    "fill_color": "#162E88",
    "border_color": "#CAE500",
    "branding_transformed": {
        "pin_search": {
            "standard": "http://storage.mds.yandex.net/get-geoadv/1336908/tycoon--479792--379095_pin_search_standard_2020-07-06T12_40_02--pin.svg",
            "standard_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/403382/379095_pin_search_standard_2020-07-06T12_40_02_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_pin_search_standard_2020-07-06T12_40_02/pin_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_pin_search_standard_2020-07-06T12_40_02/pin_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_pin_search_standard_2020-07-06T12_40_02/pin_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_pin_search_standard_2020-07-06T12_40_02/pin_x4"
                }
            }
        },
        "poi_pin_18": {
            "hover": "http://storage.mds.yandex.net/get-geoadv/225293/379095_poi_pin_18_hover_2020-07-06T12_40_05_x1.svg",
            "standard": "http://storage.mds.yandex.net/get-geoadv/1336908/379095_poi_pin_18_standard_2020-07-06T12_40_05_x1.svg"
        },
        "poi_pin_24": {
            "hover": "http://storage.mds.yandex.net/get-geoadv/1371672/379095_poi_pin_24_hover_2020-07-06T12_40_05_x1.svg",
            "standard": "http://storage.mds.yandex.net/get-geoadv/1371672/379095_poi_pin_24_standard_2020-07-06T12_40_05_x1.svg"
        },
        "drop_search": {
            "hover": "http://storage.mds.yandex.net/get-geoadv/1371672/tycoon--1654178--379095_drop_search_hover_2020-07-06T12_40--drop.svg",
            "visited": "http://storage.mds.yandex.net/get-geoadv/1371672/tycoon--1638958--379095_drop_search_visited_2020-07-06T12_40--drop.svg",
            "standard": "http://storage.mds.yandex.net/get-geoadv/1244551/tycoon--474201--379095_drop_search_standard_2020-07-06T12_40--drop.svg",
            "hover_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/1371672/379095_drop_search_hover_2020-07-06T12_40_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/1654178/379095_drop_search_hover_2020-07-06T12_40/drop_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/1654178/379095_drop_search_hover_2020-07-06T12_40/drop_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/1654178/379095_drop_search_hover_2020-07-06T12_40/drop_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/1654178/379095_drop_search_hover_2020-07-06T12_40/drop_x4"
                }
            },
            "visited_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/225293/379095_drop_search_visited_2020-07-06T12_40_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/1638958/379095_drop_search_visited_2020-07-06T12_40/drop_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/1638958/379095_drop_search_visited_2020-07-06T12_40/drop_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/1638958/379095_drop_search_visited_2020-07-06T12_40/drop_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/1638958/379095_drop_search_visited_2020-07-06T12_40/drop_x4"
                }
            },
            "standard_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/225293/379095_drop_search_standard_2020-07-06T12_40_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_drop_search_standard_2020-07-06T12_40/drop_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_drop_search_standard_2020-07-06T12_40/drop_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_drop_search_standard_2020-07-06T12_40/drop_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_drop_search_standard_2020-07-06T12_40/drop_x4"
                }
            }
        },
        "dust_search": {
            "hover": "http://storage.mds.yandex.net/get-geoadv/1371672/tycoon--479792--379095_dust_search_hover_2020-07-06T12_40_01--dust.svg",
            "visited": "http://storage.mds.yandex.net/get-geoadv/1336908/tycoon--1635364--379095_dust_search_visited_2020-07-06T12_40_01--dust.svg",
            "standard": "http://storage.mds.yandex.net/get-geoadv/225293/tycoon--474201--379095_dust_search_standard_2020-07-06T12_40_01--dust.svg",
            "hover_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/1371672/379095_dust_search_hover_2020-07-06T12_40_01_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_dust_search_hover_2020-07-06T12_40_01/dust_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_dust_search_hover_2020-07-06T12_40_01/dust_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_dust_search_hover_2020-07-06T12_40_01/dust_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/479792/379095_dust_search_hover_2020-07-06T12_40_01/dust_x4"
                }
            },
            "visited_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/1336908/379095_dust_search_visited_2020-07-06T12_40_01_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_dust_search_visited_2020-07-06T12_40_01/dust_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_dust_search_visited_2020-07-06T12_40_01/dust_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_dust_search_visited_2020-07-06T12_40_01/dust_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_dust_search_visited_2020-07-06T12_40_01/dust_x4"
                }
            },
            "standard_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/225293/379095_dust_search_standard_2020-07-06T12_40_01_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_dust_search_standard_2020-07-06T12_40_01/dust_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_dust_search_standard_2020-07-06T12_40_01/dust_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_dust_search_standard_2020-07-06T12_40_01/dust_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_dust_search_standard_2020-07-06T12_40_01/dust_x4"
                }
            }
        },
        "navi_drop_search": {
            "hover": "http://storage.mds.yandex.net/get-geoadv/225293/tycoon--474201--379095_navi_drop_search_hover_2020-07-06T12_40_05--drop-navi.svg",
            "visited": "http://storage.mds.yandex.net/get-geoadv/1336908/tycoon--474201--379095_navi_drop_search_visited_2020-07-06T12_40_05--drop-navi.svg",
            "standard": "http://storage.mds.yandex.net/get-geoadv/1244551/tycoon--1635364--379095_navi_drop_search_standard_2020-07-06T12_40_05--drop-navi.svg",
            "hover_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/403382/379095_navi_drop_search_hover_2020-07-06T12_40_05_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_hover_2020-07-06T12_40_05/drop-navi_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_hover_2020-07-06T12_40_05/drop-navi_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_hover_2020-07-06T12_40_05/drop-navi_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_hover_2020-07-06T12_40_05/drop-navi_x4"
                }
            },
            "visited_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/1244551/379095_navi_drop_search_visited_2020-07-06T12_40_05_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_visited_2020-07-06T12_40_05/drop-navi_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_visited_2020-07-06T12_40_05/drop-navi_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_visited_2020-07-06T12_40_05/drop-navi_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/474201/379095_navi_drop_search_visited_2020-07-06T12_40_05/drop-navi_x4"
                }
            },
            "standard_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/403382/379095_navi_drop_search_standard_2020-07-06T12_40_05_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_navi_drop_search_standard_2020-07-06T12_40_05/drop-navi_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_navi_drop_search_standard_2020-07-06T12_40_05/drop-navi_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_navi_drop_search_standard_2020-07-06T12_40_05/drop-navi_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/1635364/379095_navi_drop_search_standard_2020-07-06T12_40_05/drop-navi_x4"
                }
            }
        },
        "pin_bitmap_search": {
            "standard": "http://storage.mds.yandex.net/get-geoadv/225293/tycoon--1534662--379095_pin_bitmap_standard_2020-07-06T12_40_02--pin-desktop.svg",
            "standard_png": {
                "orig": "http://storage.mds.yandex.net/get-geoadv/1336908/379095_pin_bitmap_standard_2020-07-06T12_40_02_x10.svg",
                "size": {
                    "x1": "http://avatars.mds.yandex.net/get-tycoon/1534662/379095_pin_bitmap_standard_2020-07-06T12_40_02/pin-desktop_x1",
                    "x2": "http://avatars.mds.yandex.net/get-tycoon/1534662/379095_pin_bitmap_standard_2020-07-06T12_40_02/pin-desktop_x2",
                    "x3": "http://avatars.mds.yandex.net/get-tycoon/1534662/379095_pin_bitmap_standard_2020-07-06T12_40_02/pin-desktop_x3",
                    "x4": "http://avatars.mds.yandex.net/get-tycoon/1534662/379095_pin_bitmap_standard_2020-07-06T12_40_02/pin-desktop_x4"
                }
            }
        }
    }
}


def make_test_text_advert(company):
    return {
        "type": "TEXT_ADVERT",
        "body": {
            "title": company["name"],
            "link": company["url"],
            "text": company["about"] if company.get("about") else "IT-компания",
        }
    }


def make_test_branding():
    return {
        "type": "BRANDING",
        "body": BRANDING_BODY
    }
