# -*- coding:  utf-8 -*-
import logging

from sandbox.projects.avia.fare_families import JsonToPbConverter

JSON_FARE_FAMILIES = [
    {
        "base_class": "ECONOMY",
        "tariff_code_pattern": "^.*$",
        "tariff_group_name": {
            "ru": "Эконом Базовый",
            "en": "Economy Basic"
        },
        "brand": "BASIC",
        "terms": [
            {
                "code": "open_return_date",
                "rules": [
                    {
                        "availability": "NOT_AVAILABLE"
                    }
                ]
            },
            {
                "code": "miles",
                "rules": [
                    {
                        "miles": ""
                    }
                ]
            },
            {
                "code": "refundable",
                "rules": [
                    {
                        "comment": "Тариф полностью невозвратный.",
                        "availability": "NOT_AVAILABLE"
                    }
                ]
            },
            {
                "code": "refundable_no_show",
                "rules": [
                    {
                        "comment": "Тариф полностью невозвратный.",
                        "availability": "NOT_AVAILABLE"
                    }
                ]
            },
            {
                "code": "changing_carriage",
                "rules": [
                    {
                        "comment": "Разрешены со сбором за операцию:  3 000 р. для рейсов по России, ",
                        "xpath": "//Leg/Seg[FromCountry = 'RU' and ToCountry = 'RU']",
                        "availability": "CHARGE",
                        "charge": {
                            "currency": "RUB",
                            "value": "3000"
                        }
                    },
                    {
                        "comment": "Разрешены со сбором за операцию:  40 евро для международных рейсов.",
                        "xpath": "//Leg/Seg[FromCountry != 'RU' or ToCountry != 'RU']",
                        "availability": "CHARGE",
                        "charge": {
                            "currency": "EUR",
                            "value": "40"
                        }
                    }
                ]
            },
            {
                "code": "changing_carriage_no_show",
                "rules": [
                    {
                        "comment": "Обмен после вылета запрещен.",
                        "availability": "NOT_AVAILABLE"
                    }
                ]
            },
            {
                "code": "baggage",
                "rules": [
                    {
                        "comment": "Платный",
                        "places": 0
                    }
                ]
            },
            {
                "code": "carry_on",
                "special_notes": [
                    {
                        "ru": "Ручная кладь, весом не более 10 кг, размер 55*40*23."
                    }
                ],
                "rules": [
                    {
                        "comment": "https://www.s7.ru/ru/info/baggage.dot",
                        "places": 1,
                        "weight": 10,
                        "size": "55x40x23"
                    }
                ]
            },
            {
                "code": "disclosure_url",
                "rules": [
                    {
                        "special_notes": [
                            {
                                "ru": "https://www.s7.ru/home/info/fares.dot"
                            }
                        ]
                    }
                ]
            }
        ]
    }
]


def test_converter():
    converter = JsonToPbConverter()
    result_fare_families = converter.convert(JSON_FARE_FAMILIES, 1)
    logging.getLogger(__name__).info('AirlineFareFamilies Result %s', result_fare_families)
    assert result_fare_families.AirlineId == 1
    assert len(result_fare_families.Values) == 1

    fare_family = result_fare_families.Values[0]
    assert fare_family.BaseClass == 'ECONOMY'
    assert fare_family.TariffCodePattern == '^.*$'
    assert len(fare_family.TariffGroupName.Values) == 2
    assert fare_family.TariffGroupName.Values['ru'] == 'Эконом Базовый'
    assert fare_family.TariffGroupName.Values['en'] == 'Economy Basic'
    assert fare_family.Brand == 'BASIC'
    assert fare_family.Terms
