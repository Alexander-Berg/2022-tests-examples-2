# -*- coding: utf-8 -*-

import copy

from passport.backend.core.builders.base.faker.fake_builder import BaseFakeBuilder
from passport.backend.vault.api.builders.staff import Staff


TEST_STAFF_EMPTY_RESPONSE = {
    'links': {},
    'page': 1,
    'limit': 50,
    'result': [],
    'total': 0,
    'pages': 0,
}

TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE = {
    "links": {
        "last": "https://staff-api.yandex-team.ru/v3/groups?_fields=id%2Curl%2Cname&_page=60&is_deleted=false&type=department",
        "next": "https://staff-api.yandex-team.ru/v3/groups?_fields=id%2Curl%2Cname&_page=2&is_deleted=false&type=department"
    },
    "page": 1, "limit": 1,
    "result": [
        {"is_deleted": False,
         "url": "virtual_robots_3137", "id": 87859, "name": "Mssngr"},
        {"is_deleted": False,
         "url": "yandex_distproducts_browserdev_mobile_taxi_9720_2944_9770",
         "name": u"Подгруппа разработки эффективности платформы 3", "id": 82381},
        {"is_deleted": False, "url": "yandex_biz_com_8856",
         "name": u"Подразделение по взаимодействию с партнерами РСЯ",
         "id": 84687},
        {"is_deleted": False, "url": "outstaff_2289_8265_5357",
         "name": u"Служба логистики Яндекс.Еды (Outstaff)",
         "id": 84878},
        {"is_deleted": False, "url": "yandex_rkub_discovery_rec_rank",
         "name": u"Группа качества рекомендаций и анализа контента",
         "id": 59086},
        {"is_deleted": False, "url": "yandex_rkub_discovery_rec_tech_5431_9475", "id": 93278,
         "name": u"Подгруппа интерфейсов паблишинговой платформы Дзена"},
        {"is_deleted": False, "url": "yandex_search_tech_sq",
         "name": u"Управление качества поисковых продуктов", "id": 38096},
        {"is_deleted": False, "url": "yandex_search_tech_spam",
         "name": u"Отдел безопасного поиска", "id": 236},
        {"is_deleted": False, "url": "yandex_search_tech_sq_analysis",
         "name": u"Служба аналитики и конвейеризации", "id": 38098},
        {"is_deleted": False, "url": "yandex_search_tech_quality_func",
         "name": u"Отдел функциональности поиска", "id": 24936},
        {"is_deleted": False, "url": "yandex_search_tech_quality",
         "name": u"Отдел ранжирования", "id": 64},
        {"is_deleted": False, "url": "yandex_search_tech_ont", "name": u"Отдел Web онтологии",
         "id": 32470},
        {"is_deleted": False, "url": "yandex_search_tech_sq_7195",
         "name": u"Отдел Яндекс.Видео", "id": 66040},
        {"is_deleted": False, "url": "yandex_search_tech_sq_8135",
         "name": u"Отдел Яндекс.Картинки", "id": 66046},
        {"is_deleted": False, "url": "yandex_search_tech_sq_3452",
         "name": u"Служба геопоиска и справочника", "id": 80036},
        {"is_deleted": False, "url": "yandex_search_tech_sq_interfaceandtools",
         "name": u"Поисковые интерфейсы и сервисы для организаций",
         "id": 82601},
        {"is_deleted": False, "url": "yandex_design_search_vertical",
         "name": u"Группа дизайна вертикальных сервисов поиска",
         "id": 29453},
        {"is_deleted": False, "url": "yandex_mnt_infra",
         "name": u"Инфраструктурный отдел",
         "id": 24},
        {"is_deleted": False, "url": "yandex_mnt_infra_itoffice",
         "name": u"Служба IT инфраструктуры офисов", "id": 45},
        {"is_deleted": False, "url": "as_opdir_8255",
         "name": u"Подгруппа операторов Справочника 5 (Outstaff)",
         "id": 67600},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_1683",
         "name": u"Служба поддержки в Воронеже",
         "id": 88933},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_6923",
         "name": u"Служба качества поддержки", "id": 78575},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_supvod_7398",
         "name": u"Группа поддержки финансовых обращений партнеров",
         "id": 82743},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_6923_5271", "id": 92015,
         "name": u"Группа контента пользователей"},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_supvod_3678",
         "name": u"Группа поддержки партнеров по вопросам правосудия и стандартов сервиса",
         "id": 82741},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_6035_1229", "id": 92018,
         "name": u"Группа работы с инцидентами"},
        {"is_deleted": False, "url": "yandex_proffice_support_comm_taxi_2913", "id": 92011,
         "name": u"Группа письменной поддержки пользователей Uber"},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_6923_2643", "id": 92013,
         "name": u"Группа обучения"},
        {"is_deleted": False, "url": "yandex_rkub_taxi_support_supvod",
         "name": u"Служба поддержки партнёров", "id": 42112},
        {"is_deleted": False, "url": "outstaff_2289_9459_8766_9989",
         "name": u"Группа международной поддержки пользователей (Outstaff)",
         "id": 87495},
        {"is_deleted": False, "url": "yandex_edu_personel_0289_8372",
         "name": u"Группа продуктов Яндекс.Просвещение",
         "id": 67071},
        {"is_deleted": False, "url": "ext_2027_3589",
         "name": u"Группа продуктов Яндекс.Просвещение СП",
         "id": 79093},
        {"is_deleted": False, "url": "yandex_edu_personel_5537", "name": u"Яндекс.Образование",
         "id": 83658},
        {"is_deleted": False, "url": "yandex_edu_personel_5537_0405",
         "name": u"Служба разработки online платформы",
         "id": 83659},
        {"is_deleted": False, "url": "yandex_edu_personel_5537_dep80665", "id": 93447,
         "name": u"Яндекс.Навыки"},
        {"is_deleted": False, "url": "yandex_edu_personel_5537_dep03987", "id": 93448,
         "name": u"Яндекс.Школа"},
        {"is_deleted": False, "url": "yandex_mrkt_mediamrkt_media_taxi_6258_0126", "id": 93796,
         "name": u"Подгруппа закупки наружной рекламы и брендирования "},
        {"is_deleted": False, "url": "ext_6887", "name": u"Внешние консультанты Яндекс.Еды",
         "id": 89623},
        {"is_deleted": False, "url": "outstaff_2289_8265_6121_1328",
         "name": u"Группа по работе с фотографиями (Outstaff)",
         "id": 90711},
        {"is_deleted": False, "url": "yandex_rkub_taxi_5151_8501_8241",
         "name": u"Группа маркетинговых коммуникаций Яндекс.Еды",
         "id": 84819},
        {"is_deleted": False, "url": "yandex_rkub_taxi_5151_8501_9053",
         "name": u"Служба маркетинга Яндекс.Еды",
         "id": 86477},
        {"is_deleted": False, "url": "yandex_rkub_taxi_cust",
         "name": u"Служба по работе с водителями Яндекс.Такси",
         "id": 44003},
        {"is_deleted": False, "url": "yandex_rkub_taxi_cust_supp",
         "name": u"Центры Яндекс.Такси", "id": 44283},
        {"is_deleted": False, "url": "yandex_distproducts_morda_commercial_prod_7642",
         "name": u"Группа проектов счастья водителя", "id": 73680},
        {"is_deleted": False, "url": "yandex_rkub_taxi_dev_5902",
         "name": u"Служба региональных центров по работе с водителями",
         "id": 74710},
        {"is_deleted": False, "url": "ext_yataxi_3452",
         "name": u"Внешние консультанты Колл-центра",
         "id": 82679},
        {"is_deleted": False, "url": "yandex_rkub_taxi_dev_3231",
         "name": u"Отдел активации и обучения водителей",
         "id": 83734},
        {"is_deleted": False, "url": "yandex_rkub_taxi_dev_5902_7922",
         "name": u"Группа международного развития центров", "id": 84278},
        {"is_deleted": False, "url": "yandex_rkub_taxi_dev_3231_1747",
         "name": u"Группа по коммуникациям с водителями", "id": 84280},
        {"is_deleted": False, "url": "yandex_rkub_taxi_dev_3231_6117",
         "name": u"Группа стратегического развития и аналитики",
         "id": 84281},
        {"is_deleted": False, "name": u"Группа аналитики и безопасности систем авторизации",
         "id": 2864,
         "url": "yandex_personal_com_aux_sec"},
        {"is_deleted": False, "name": u"Тестовая группа Секретницы 1",
         "id": 2,
         "url": "_vault_test_group_1"},
        {"is_deleted": False, "name": u"Тестовая группа Секретницы 2",
         "id": 4112,
         "url": "_vault_test_group_2"},
        ],
    "total": 1,
    "pages": 1,
}


def _make_disabled_staff_departments_response():
    result = copy.deepcopy(TEST_STAFF_GET_ALL_DEPARTMENTS_RESPONSE)
    for d in result['result']:
        d['is_deleted'] = True
    return result


TEST_DISABLED_STAFF_GET_ALL_DEPARTMENTS_RESPONSE = _make_disabled_staff_departments_response()

TEST_STAFF_GET_ALL_PERSONS_RESPONSE = {
    "links": {
        "prev": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepartm"
                "ent_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5&_page=9",
        "last": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepartm"
                "ent_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5&_page=11",
        "first": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepart"
                 "ment_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5",
        "next": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepartm"
                "ent_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5&_page=11",
    },
    "page": 10,
    "limit": 5,
    "result": [
        {
            "keys": [
                {
                    "fingerprint_sha256": "SHA256:+MzGJsakhNsRpDZXISpu2D0kviexSj/eZ4/C8VVyPxI",
                    "id": 9507,
                    "description": "mac",
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCx8Yc4+4RzhnUixVwixWlWvr0JuBgwJsPPiop4xF8MsgOu2FrOa5x"
                           "ksLd+xdzCqP+noJ87VEeIQxZY7uGar7wBf/wJ2QrjzA8iJZkFVa1XOxE3yvPxOpRVIN6HQPRbf3fbZzuCCGmAEOj1fG"
                           "Ye5xu8T3tXcoe0KTtn5KNuS2rhz9tfWfEJKnlFH0tShZBsrWBlib1GRGTjymot4SPpvCs7bYs32fiS2j8IjQ5b3O6tL"
                           "bz+fPh7gwRViLNOjixNRYRDHCf2KrTlz7lv/CoGwn17FADugLHRyDUliLlhcRrc1q/rR1nNfGR10ZNVWt60hBd0hCvx"
                           "GknIEHR3+4o5CCcB agniash@yandex-team.ru",
                    "fingerprint": "d9:61:e9:86:18:6b:77:1a:09:f1:ba:98:9e:b7:3c:8f",
                },
                {
                    "fingerprint_sha256": "SHA256:k7FkFT2Bmih17tLBCyL9zExChQ4auyYFzwXY5koQcEE",
                    "id": 10470,
                    "description": "agniash01",
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC30WOYKUzi09C8tRRt5HPcFBpGe8qhunSqKAio3b6SKdFrxopS3xc"
                           "4UbCOzQkaStcTPVLTAUXxMgC+B1ORru5A5NCbyG7rNUkVnamZOeLFkpiMD9gnMzDp6sAsI5WHLARkoZCYIErZwfO+ZH"
                           "7mqHU9hB2gpwKiwk8+CMxvVdZDmK31fmCpBZVwIhu3vKKKYTXiLnc4t4MqkgI+vyszAHhqZF4xvn1WfdHYB+NmF1HOZ"
                           "NXGQiGd0oFe0ZIkba1uz/79uvVQxfU2fLbxE3f/adfLAOIfuiYg6/aeBaHJ2i5L6qKuA92uC0QtWT1oM82SRZratUWt"
                           "rD5ODOR2hkMatcFX agniash@yandex-team.ru",
                    "fingerprint": "42:70:b5:a1:87:a3:2e:f1:74:77:3b:ca:db:fb:0b:ab",
                },
            ],
            "login": "agniash",
            "uid": "1120000000040289",
            "name": {
                "first": {
                    "ru": u"Павел",
                },
                "last": {
                    "ru": u"Агниашвили"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 3132,
                "ancestors": [
                    {
                        "id": 1,
                    },
                    {
                        "id": 4112,
                    },
                    {
                        "id": 3224,
                    },
                    {
                        "id": 3101,
                    },
                    {
                        "id": 62,
                    },
                    {
                        "id": 533,
                    },
                ],
            },
        },
        {
            "keys": [
                {
                    "fingerprint_sha256": "SHA256:NApR0gtWq2dRr+H1TFibdBvVYTkEDOZLbQ3gvShslyI",
                    "fingerprint": "4a:e3:55:05:38:46:a5:64:42:f4:0d:57:4b:54:2e:9d",
                    "id": 17727,
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwlsvK/ujXg1YcMSxjQZSEltZPzKqbgZimQc7S63GxWRa2bTApA9/"
                           "jji6CYw89XvbRY8j/2qF4Oay49zJ9h3E9WUOEe4jA0JoUoA5Jjxd05RynSDTK+gFCEw87xG32H8sdYC/vF1t2+3RcWG"
                           "wGs8VSkHmMddDb0LvCa83/XZYjSPwSlFpkZ8eVPYZLUUlZowdGQrdQpvA2CvSS65PYbhcK/fPdb72Ll6AwEhZOyw8Nf"
                           "c/foEZ6bOdnSCGDHWpkDNWql67h18kSsWPPYNiJwESMfSlPBTRc8XuJ1L6Vwt0+wnJ7UaFfuhyHn+GvFspHOOkeDvxm"
                           "qMc8b7AEaa12d4yB crossby@yandex-team.ru",
                    "description": "ns13",
                },
            ],
            "login": "crossby",
            "uid": "1120000000039954",
            "name": {
                "first": {
                    "ru": u"Валерий",
                },
                "last": {
                    "ru": u"Дужик"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 3491,
                "ancestors": [
                    {
                        "id": 1,
                    },
                    {
                        "id": 4112,
                    },
                    {
                        "id": 3224,
                    },
                    {
                        "id": 3101,
                    },
                    {
                        "id": 62,
                    },
                    {
                        "id": 533,
                    },
                ],
            },
        },
        {
            "keys": [{
                "fingerprint_sha256": "SHA256:aaa",
                "id": 8740,
                "description": "Strange key",
                "key": "strange-key ororo ppodolsky@213.180.218.205-red.dhcp.yndx.net",
                "fingerprint": "aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa",
            }, {
                "fingerprint_sha256": "SHA256:iNCb5cMwsSf/s5bp3WQnNBmSYbQDOYE4hEvgC5L4FiM",
                "id": 8741,
                "description": "Default Key ECDSA",
                "key": "ecdsa-sha2-nistp384 AAAAE2VjZHNhLXNoYTItbmlzdHAzODQAAAAIbmlzdHAzODQAAABhBMNu9svIGzrY4FInPdoLhe6"
                       "0WfKBMmfMZkllIEiFrTyuuNKUnX0gM77yNQJaqBLxdPzhkmW+eiCp7uvmHRwmH/UTXSkFp9espCnIeeCd0WTn55NSZrPccv"
                       "8cGr/WflBrwg== ppodolsky@213.180.218.205-red.dhcp.yndx.net",
                "fingerprint": "62:3b:5e:da:45:73:ad:5c:6e:69:a0:54:dd:d3:d6:d5",
            }, {
                "fingerprint_sha256": "SHA256:DfGirPT0N8xBx1ttKQdGusc64CbXJd9bQ24ys37aaxs",
                "id": 8740,
                "description": "Default Key",
                "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7EPwGIBqO4FUBoeQRcJLK/0dSMMjEik+pKIGV9eyUfm+5QhkAz8X2H86"
                       "AzM+/l9YmjyRnSDgq2umfVWfo/Kj61fvFwiO32MMuAAhU3mzwBH/d+7xVRJTkkeDvsXluuMIBkZUsIJKecuhAFoHlDL6aG0"
                       "fMZaeORKVajt7UIh9Jqudvafceay7hMh3HsyZmKkh0oNHojqAwDNHPDfGZ/Rw78fyy/W5p0NLcMeOYzm8LdRRkSRUUJX23u"
                       "jh2TbwWpa9AKO9oz/OpDcuDl/+QmvRbq7HFZCDGUdQuSogd2xDWV73cWBw8h2ZDo+Dm1qGmVpv8Zimh8GhNqNPEVtlw2SOL"
                       " ppodolsky@yandex-team.ru",
                "fingerprint": "45:08:4b:c2:7d:90:5d:c6:11:12:4a:24:83:8d:20:aa",
            }],
            "login": "ppodolsky",
            "uid": "1120000000038274",
            "name": {
                "first": {
                    "ru": u"Паша",
                },
                "last": {
                    "ru": u"Переведенцев"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 2864,
                "ancestors": [
                    {"id": 1},
                    {"id": 4112},
                    {"id": 5698},
                    {"id": 1538},
                    {"id": 3051},
                ],
            },
        },
        {
            "keys": [
                {
                    "fingerprint_sha256": "SHA256:HeqvEFi8VfeDTwpeURtlVMouwa0Ymh+nOXGWBnVoNds",
                    "description": "Dell Ubuntu",
                    "id": 7498,
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC5WbIQ1CsAfdB1SBlJjC5WYZqkByu4b/CZ5+0EjA7EUdEbd/8Hd8a"
                           "UXq1no7k24TbsNnSrJ6i+tjDELTv0rstKaqvYKNgG+ZftLGE39N8ga62gyhL2euEjyoIFULKKo+17YrlW4SgNqQ+q3B"
                           "wc9Vmwbd+kVDe0J5rgr1JWHxvKEE5rG0p/NI1hitzxTMez75xikB3rw38vr4i/bYSMIlFLX54xAagBQCOWLucXJ+2R0"
                           "J2OJW6F5AhpGT2Rtd6almzROib8yYiTYITgW8qEYYN2U3igkRlNxXqck1S05d/1Iu8rjnRjdlQnkWgxKxC6Rrd3zqyw"
                           "uogqq7aJWe/EiKYF ankineri@ankineri-ub14",
                    "fingerprint": "c2:28:a7:ad:94:13:e4:6e:2a:57:df:6a:8a:5b:bc:55",
                },
                {
                    "fingerprint_sha256": "SHA256:wM0aHkilEa+p3GpTfzcHxw+TVObuZZMKJZ28sEGpRhQ",
                    "description": "FactorDev",
                    "id": 7499,
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCayrrgZs9rLwhLwoDtmTTr8mmy9d4h5dh8XpPtpGVfBY8MM+jOIDc"
                           "eJDqBQwinBYelm8eIBbXsCFDD3kevW0Qw6xGFnlAwoYe45HGIKeyHcPx6RUmrvBxXFIluMpdM5DV/vz0qy1TIpiuu/H"
                           "zVAKneKz1+XPB/jchZxHTAA6BFB5WLEmIQDI2cqRY7OdwbpRoOordYSLyxN4zoHAmqJcQNvhWrXGkFd6dmt4Lr2eI6p"
                           "SSoGh0CpDJNFRl5UJyf8zF0b3Ji6ZaNDgG70WR75qWIhJY6d/u+DTkLPWOIfxauY7UMro9GM973fJmUZq/jqcjRX6+e"
                           "UFVyFTXNxaNMxjNr ankineri@factordev.search.yandex.net",
                    "fingerprint": "2a:97:27:b3:fe:d6:de:9a:69:42:d0:4b:5c:a4:2a:2e",
                },
                {
                    "fingerprint_sha256": "SHA256:9VLn/fPWBY+lq/bA6St4+w7IU4z4AHXP2LijRURUfVY",
                    "description": "FactorDev2",
                    "id": 9326,
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqeg+b53lU/ZQFgGx2I3dNuH7NtAfhBOZ7e8mtOkWbTY/dPrXILQk"
                           "QlaBL+FgbXSnnopL2BZu0W6bk7TkFjFsll9AZsKCcGgyucePp/5qpULNHzNf3iqtvLi2xlCwdcDKNXxQniP8AMZmFlV"
                           "7JPSrVpl2iJNhPTp5g0a9RRmKltBndbxmZ7ie3tDX+0KNPgu6RZURs9xCZSHrJN+ubXyl6Ncn/mkBKZBPufhPB4Dhor"
                           "VgYVFrti01UFJrQMYy6cyMsTXoL/GmFMaXt2ySd3U/m6mjYieEIxEQeKswaMhB0uIsclX6raJg6XuJbtxd8EeS66Htt"
                           "Hw5xIVYZ7IAhEtPj ankineri@factordev2.search.yandex.net",
                    "fingerprint": "44:30:f8:de:1a:33:4b:c9:53:03:29:b2:66:d9:4b:4b",
                },
                {
                    "fingerprint_sha256": "SHA256:oOrBqla5/UIsOBInKj9sE4urltjFlqXUGNMf6NPC/i8",
                    "description": "lenstra",
                    "id": 12354,
                    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDg4+GoCypqseVKHW0ZdkMAn5QIRvynteMv+p0kN96MqRYR53VjSOQ"
                           "6V/OlZ0RNUia1OTqXFN+/rFpJQPt3N7ZhGa2GWUpE2pzGhgUGxtrs57J+gFGSYdnmXbilH6C88g/GTFa+/oIKXBppUK"
                           "VHJRFFvH42fKPMgKCBDoksYcmoyNJ6xdybUYyKo9pW5QYuB5qCGGwa2j964ONPqQM8wGrpYk9tZXBF0bXn8KOuRmQnY"
                           "sdb1RBcanHV52W2cCP3kYWkVGZ1pS9rZs0ShIla2zZzW+e+f8WkWyRx+1OZCr3g4VwK+tfqS5WD3LcWQaDz6d9vXCuk"
                           "oJzuC2iaf1s1m5KqS9iIrjUIjG57Onx26gLzD3p+PfmnIs2rfULnO+/aaXiIN5r4xSSc8rRV4kKo9APclfME70iIU7K"
                           "eELoO3vd6HQdxBfE1gJGneTJLM6dH1dAlG3xoFWzcBtxgxu/gxe7s7AwBwpIEVpC4F4H84pdH5l4BZRyaDIC1LxULrx"
                           "j25OTFNlhhnXy6S2Fm4AmghYmDVi+XqxUPpJZcLuze+GtNCnCyO7H7XXiim0hwVOmG+VxXs8f9X4qcAHn7IV1Ux1vis"
                           "C7SSC5WCGantagGL3WCcvjfKTrgNqwqh1UAmmbCsaRPLJM4k4IEGRwzFquMdon2OfYA3eQBH+v50zJtSi8LRQ== ank"
                           "ineri@lenstra.search.yandex.net",
                    "fingerprint": "d7:83:8a:f6:18:5c:ff:0d:92:d8:46:cd:b5:33:af:35",
                },
            ],
            "login": "ankineri",
            "uid": "1120000000036175",
            "name": {
                "first": {
                    "ru": u"Андрей",
                },
                "last": {
                    "ru": u"Молчанов"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 422,
                "ancestors": [
                    {
                        "id": 1,
                    },
                    {
                        "id": 4112,
                    },
                    {
                        "id": 3224,
                    },
                    {
                        "id": 3101,
                    },
                    {
                        "id": 62,
                    },
                    {
                        "id": 533,
                    },
                ],
            },
        },
        {
            "keys": [],
            "login": "mesyarik",
            "uid": "1120000000035620",
            "name": {
                "first": {
                    "ru": u"Илья",
                },
                "last": {
                    "ru": u"Мещерин"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 4045,
                "ancestors": [
                    {
                        "id": 1,
                    },
                    {
                        "id": 4112,
                    },
                    {
                        "id": 3224,
                    },
                    {
                        "id": 3101,
                    },
                    {
                        "id": 62,
                    },
                    {
                        "id": 533,
                    },
                ],
            },
        },
        {
            "keys": [],
            "login": "vault-test-100",
            "uid": "100",
            "name": {
                "first": {
                    "ru": u"Vault",
                },
                "last": {
                    "ru": u"Test100"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 2,
                "ancestors": [
                    {
                        "id": 1,
                    },
                ],
            },
        },
        {
            "keys": [],
            "login": "vault-test-101",
            "uid": "101",
            "name": {
                "first": {
                    "ru": u"Vault",
                },
                "last": {
                    "ru": u"Test101"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 2,
                "ancestors": [
                    {
                        "id": 1,
                    },
                ],
            },
        },
        {
            "keys": [],
            "login": "vault-test-102",
            "uid": "102",
            "name": {
                "first": {
                    "ru": u"Vault",
                },
                "last": {
                    "ru": u"Test102"
                }
            },
            "is_deleted": False,
            'official': {'is_dismissed': False},
            "department_group": {
                "id": 2,
                "ancestors": [
                    {
                        "id": 1,
                    },
                ],
            },
        },
    ],
    "total": 50,
    "pages": 10,
}


def _make_disabled_staff_person_response():
    result = copy.deepcopy(TEST_STAFF_GET_ALL_PERSONS_RESPONSE)
    for d in result['result']:
        d['official']['is_dismissed'] = True
    return result

TEST_DISABLED_STAFF_GET_ALL_PERSONS_RESPONSE = _make_disabled_staff_person_response()


def staff_response(login, uid, key, first_name='Dummy', last_name='Jimmy', is_dismissed=False):
    return {
        "links": {
            "prev": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepartm"
                    "ent_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5&_page=9",
            "last": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepartm"
                    "ent_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5&_page=11",
            "first": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepart"
                     "ment_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5",
            "next": "https://staff-api.yandex-team.ru/v3/persons?_fields=department_group.ancestors.department.id%2Cdepartm"
                    "ent_group.department.id%2Cuid%2Clogin%2Ckeys&_limit=5&_page=11",
        },
        "page": 10,
        "limit": 1,
        "result": [
            {
                "keys": [
                    {
                        "fingerprint_sha256": "",
                        "id": 9507,
                        "description": "key",
                        "key": key,
                        "fingerprint": "",
                    },
                ],
                "login": login,
                "uid": uid,
                "name": {
                    "first": {
                        "ru": first_name,
                    },
                    "last": {
                        "ru": last_name
                    }
                },
                'official': {'is_dismissed': is_dismissed},
                'is_deleted': False,
                "department_group": {
                    "id": 422,
                    "ancestors": [
                        {
                            "id": 1,
                        },
                    ],
                },
            },
        ],
        "total": 10,
        "pages": 10,
    }


class FakeStaff(BaseFakeBuilder):
    def __init__(self):
        super(FakeStaff, self).__init__(Staff)

    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):
        if 'groups' in url:
            return 'get_all_departments'  # pragma: no cover
        return 'get_all_persons'  # pragma: no cover
