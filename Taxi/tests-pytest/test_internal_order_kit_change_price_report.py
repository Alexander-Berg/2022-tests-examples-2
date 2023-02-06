# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from taxi import config
from taxi.internal import dbh
from taxi.internal.order_kit import change_price_report


@pytest.mark.parametrize('use_recommended_cost', [False, True])
@pytest.mark.filldb(_fill=True)
@pytest.inline_callbacks
def test_use_recommended_cost(use_recommended_cost):
    order_proc = {
        '_id': 'order_id',
        'order': {
            'disp_cost': {
                'taximeter_cost': 100,
                'disp_cost': 200,
                'operator_login': 'test',
                'use_recommended_cost': use_recommended_cost,
            },
            'performer': {
                'taxi_alias': {
                    'id': 'ext_order',
                },
                'db_id': 'ext_park',
                'clid': 'park',
                'uuid': 'driver',
                'driver_license': '111222',
                'tariff': {
                    'class': 'econom',
                    'currency': 'RUB'
                }

            },
            'request': {
                'source': {
                    'fullname': 'отправление'
                },
                'destinations': [
                    {
                        'fullname': 'прибытие'
                    }
                ]
            }
        }
    }

    comment = yield change_price_report._create_change_price_ticket(
        'yataxi', dbh.order_proc.Doc(order_proc)
    )
    print(comment)
    assert bool(comment.get('ticket')) == (not use_recommended_cost)


@pytest.mark.parametrize('zendesk_id,order_proc,ticket_expected', [
    (
        'yataxi',
        {
            '_id': 'order_id',
            'order': {
                'disp_cost': {
                    'taximeter_cost': 100,
                    'disp_cost': 200,
                    'operator_login': 'test'
                },
                'performer': {
                    'taxi_alias': {
                        'id': 'ext_order',
                    },
                    'db_id': 'ext_park',
                    'clid': 'park',
                    'uuid': 'driver',
                    'driver_license': '111222',
                    'tariff': {
                        'class': 'econom',
                        'currency': 'RUB'
                    }

                },
                'request': {
                    'source': {
                        'fullname': 'отправление'
                    },
                    'destinations': [
                        {
                            'fullname': 'прибытие'
                        }
                    ]
                }
            }
        },
        {
            'ticket': {
                'requester': {
                    'email': 'park@park.ru',
                    'name': 'park@park.ru'
                },
                'comment': 'ID заказа ext_order\n'
                            'Сумма, на которую заказ закрыт фактически: 100 RUB\n'
                            'Сумма, которую выставил диспетчер: 200 RUB\n'
                            'Категория заказа: эконом\n'
                            'Точка А: отправление\n'
                            'Точка Б: прибытие\n'
                            'Водительское удостоверение: 111222\n',
                'subject': 'Заявка диспетчера на изменение стоимости по заказу ext_order',
                'priority': 'high',
                'group_id': 24399809,
                'form_id': 235645,
            }
        }
    ),
    (
        'yataxi',
        {
            '_id': 'order_id1',
            'order': {
                'disp_cost': {
                    'taximeter_cost': 100,
                    'operator_login': 'test'
                },
                'performer': {
                    'taxi_alias': {
                        'id': 'ext',
                    },
                    'db_id': 'ext_park',
                    'clid': 'park',
                    'uuid': 'driver',
                    'driver_license': '111222',
                    'tariff': {
                        'class': 'vip',
                        'currency': 'RUB'
                    }

                },
                'request': {
                    'source': {
                        'fullname': 'отправление'
                    },
                    'destinations': [
                        {
                            'fullname': 'прибытие'
                        },
                        {
                            'fullname': 'прибытие2'
                        }
                    ]
                }
            }
        },
        {
            'ticket': {
                'requester': {
                    'email': 'park@park.ru',
                    'name': 'park@park.ru'
                },
                'comment': 'ID заказа ext\n'
                            'Сумма, на которую заказ закрыт фактически: 100 RUB\n'
                            'Сумма, которую выставил диспетчер:  RUB\n'
                            'Категория заказа: бизнес\n'
                            'Точка А: отправление\n'
                            'Точка Б: прибытие\n'
                            'прибытие2\n'
                            'Водительское удостоверение: 111222\n',
                'subject': 'Заявка диспетчера на изменение стоимости по заказу ext',
                'priority': 'high',
                'group_id': 24399809,
                'form_id': 235645,
            }
        }
    ),
    (
        'yutaxi',
        {
            '_id': 'order_id2',
            'order': {
                'disp_cost': {
                    'taximeter_cost': 115,
                    'operator_login': 'test'
                },
                'performer': {
                    'taxi_alias': {
                        'id': 'ext',
                    },
                    'db_id': 'ext_park',
                    'clid': 'park',
                    'uuid': 'driver',
                    'driver_license': '111222',
                    'tariff': {
                        'class': 'vip',
                        'currency': 'EUR'
                    }

                },
                'request': {
                    'source': {
                        'fullname': 'отправление'
                    },
                    'destinations': [
                        {
                            'fullname': 'прибытие1'
                        },
                        {
                            'fullname': 'прибытие2'
                        }
                    ]
                }
            }
        },
        {
            'ticket': {
                'requester': {
                    'email': 'park@park.ru',
                    'name': 'park@park.ru'
                },
                'comment': 'ID заказа ext\n'
                           'Сумма, на которую заказ закрыт фактически:'
                           ' 115 EUR\n'
                           'Сумма, которую выставил диспетчер:  EUR\n'
                           'Категория заказа: бизнес\n'
                           'Точка А: отправление\n'
                           'Точка Б: прибытие1\n'
                           'прибытие2\n'
                           'Водительское удостоверение: 111222\n',
                'subject': 'Заявка диспетчера на изменение стоимости по '
                           'заказу ext',
                'priority': 'high',
                'group_id': 360000649231,
                'form_id': 360000038391,
            }
        }
    ),
    (
        'yataxi',
        {
            '_id': 'order_id',
            'order': {
                'disp_cost': {
                    'taximeter_cost': 100,
                    'driver_cost': 201,
                    'operator_login': 'test_driver'
                },
                'performer': {
                    'taxi_alias': {
                        'id': 'ext_order_1',
                    },
                    'db_id': 'ext_park',
                    'clid': 'park',
                    'uuid': 'driver',
                    'driver_license': '1112223',
                    'tariff': {
                        'class': 'econom',
                        'currency': 'RUB'
                    }

                },
                'request': {
                    'source': {
                        'fullname': 'отправление'
                    },
                    'destinations': [
                        {
                            'fullname': 'прибытие2'
                        }
                    ]
                }
            }
        },
        {
            'ticket': {
                'requester': {
                    'email': '1112223@taximeter.ru',
                    'name': '1112223@taximeter.ru'
                },
                'comment': 'ID заказа ext_order_1\n'
                           'Сумма, на которую заказ закрыт фактическ'
                           'и: 100 RUB\n'
                           'Сумма, которую выставил водитель: 201 RUB\n'
                           'Категория заказа: эконом\n'
                           'Точка А: отправление\n'
                           'Точка Б: прибытие2\n'
                           'Водительское удостоверение: 1112223\n',
                'subject': 'Заявка водителя на изменение стоимости по'
                           ' заказу ext_order',
                'priority': 'high',
                'group_id': 24399809,
                'form_id': 360000029765,
            }
        }
    ),
    (
        'yataxi',
        {
            '_id': 'order_id1',
            'order': {
                'disp_cost': {
                    'driver_cost': 100,
                    'operator_login': 'test'
                },
                'performer': {
                    'taxi_alias': {
                        'id': 'ext',
                    },
                    'db_id': 'ext_park',
                    'clid': 'park',
                    'uuid': 'driver',
                    'driver_license': '111222',
                    'tariff': {
                        'class': 'vip',
                        'currency': 'RUB'
                    }

                },
                'request': {
                    'source': {
                        'fullname': 'отправление'
                    },
                    'destinations': [
                        {
                            'fullname': 'прибытие'
                        },
                        {
                            'fullname': 'прибытие2'
                        }
                    ]
                }
            }
        },
        {
            'ticket': {
                'requester': {
                    'email': '111222@taximeter.ru',
                    'name': '111222@taximeter.ru'
                },
                'comment': 'ID заказа ext\n'
                           'Сумма, на которую заказ закрыт фактически:  RUB\n'
                           'Сумма, которую выставил водитель: 100 RUB\n'
                           'Категория заказа: бизнес\n'
                           'Точка А: отправление\n'
                           'Точка Б: прибытие\n'
                           'прибытие2\n'
                           'Водительское удостоверение: 111222\n',
                'subject': 'Заявка водителя на изменение стоимости по заказу ext',
                'priority': 'high',
                'group_id': 24399809,
                'form_id': 360000029765,
            }
        }
    ),
    (
        'yutaxi',
        {
            '_id': 'order_id2',
            'order': {
                'disp_cost': {
                    'taximeter_cost': 115,
                    'driver_cost': 150,
                    'operator_login': 'test'
                },
                'performer': {
                    'taxi_alias': {
                        'id': 'ext',
                    },
                    'db_id': 'ext_park',
                    'clid': 'park',
                    'uuid': 'driver',
                    'driver_license': '',
                    'tariff': {
                        'class': 'business',
                        'currency': 'EUR'
                    }

                },
                'request': {
                    'source': {
                        'fullname': 'отправление'
                    },
                    'destinations': [
                        {
                            'fullname': 'прибытие1'
                        },
                        {
                            'fullname': 'прибытие2'
                        }
                    ]
                }
            }
        },
        {
            'ticket': {
                'requester': {
                    'email': 'devnull@taximeter.ru',
                    'name': 'devnull@taximeter.ru'
                },
                'comment': 'ID заказа ext\n'
                           'Сумма, на которую заказ закрыт фактически: '
                           '115 EUR\n'
                           'Сумма, которую выставил водитель: 150 EUR\n'
                           'Категория заказа: комфорт\n'
                           'Точка А: отправление\n'
                           'Точка Б: прибытие1\n'
                           'прибытие2\n'
                           'Водительское удостоверение: \n',
                'subject': 'Заявка водителя на изменение стоимости по заказу '
                           'ext',
                'priority': 'high',
                'group_id': 360000649231,
                'form_id': 360000029765,
            }
        }
    ),
])
@pytest.mark.filldb(_fill=True)
@pytest.inline_callbacks
def test_make_change_price_ticket(zendesk_id, order_proc, ticket_expected):
    comment = yield change_price_report._create_change_price_ticket(
        zendesk_id, dbh.order_proc.Doc(order_proc)
    )
    assert comment['ticket']['comment'] == ticket_expected['ticket']['comment']
    assert comment['ticket']['requester'] == ticket_expected['ticket']['requester']
    assert comment['ticket']['priority'] == ticket_expected['ticket']['priority']
    assert comment['ticket']['form_id'] == ticket_expected['ticket']['form_id']
    assert comment['ticket']['group_id'] == ticket_expected['ticket']['group_id']


@pytest.mark.parametrize('zendesk_id,price_source,order_proc,kwargs,result', [
    (
        'yataxi',
        'dispatcher',
        {
            '_id': 'order_id',
            'order': {
                'city': 'Москва',
                'performer': {
                    'taxi_alias': {
                        'id': 'ext_order',
                    },
                    'driver_license': '111222',
                    'tariff': {
                        'class': 'econom',
                        'currency': 'RUB'
                    }
                },
            }
        },
        {
            'tariff': ''
        },
        {
            'city': 'Москва',
            'city_text': 'Москва',
            'order_id': 'ext_order',
            'license': '111222',
            'tariff': '',
            'ticket_theme': 'тикет_снятие_заказа_с_модерации',
            'parks_change_value': 'парки_заявка_на_изменение_стоимости',
            'change_value': 'заявка_на_изменение_стоимости',
            'taxipark': 'Таксопарк'
        }
    ),
    (
        'yataxi',
        'dispatcher',
        {
            '_id': 'order_id',
            'order': {
                'city': 'Ростов',
                'performer': {
                    'taxi_alias': {
                        'id': 'ext',
                    },
                    'driver_license': '1112322',
                    'tariff': {
                        'class': 'econom',
                        'currency': 'RUB'
                    }
                },
            }
        },
        {
            'tariff': 'Комбо'
        },
        {
            'city': 'Ростов',
            'city_text': 'Ростов',
            'order_id': 'ext',
            'license': '1112322',
            'tariff': 'Комбо',
            'ticket_theme': 'тикет_снятие_заказа_с_модерации',
            'parks_change_value': 'парки_заявка_на_изменение_стоимости',
            'change_value': 'заявка_на_изменение_стоимости',
            'taxipark': 'Таксопарк'
        }
    ),
    (
        'yataxi',
        'driver',
        {
            '_id': 'order_id',
            'order': {
                'city': 'Ростов',
                'performer': {
                    'taxi_alias': {
                        'id': 'ext_order_d',
                    },
                    'driver_license': '333444',
                    'tariff': {
                        'class': 'comfortplus',
                        'currency': 'RUB'
                    }
                },
            }
        },
        {
            'tariff': ''
        },
        {
            'city': 'Ростов',
            'city_text': 'Ростов',
            'order_id': 'ext_order_d',
            'license': '333444',
            'tariff': '',
            'ticket_theme': 'Заявка на изменение стоимости',
            'driver_change_value': 'Заявка на изменение стоимости',
            'driver': 'Водитель',
            'priority': 'Срочный',
            'taximeter': 'Таксометр'
        }
    ),
    (
        'yataxi',
        'driver',
        {
            '_id': 'order_id',
            'order': {
                'city': 'Ростов',
                'performer': {
                    'taxi_alias': {
                        'id': 'ext',
                    },
                    'driver_license': '1112322',
                    'tariff': {
                        'class': 'econom',
                        'currency': 'RUB'
                    }
                },
            }
        },
        {
            'tariff': 'Комфорт'
        },
        {
            'city': 'Ростов',
            'city_text': 'Ростов',
            'order_id': 'ext',
            'license': '1112322',
            'tariff': 'Комфорт',
            'ticket_theme': 'Заявка на изменение стоимости',
            'driver_change_value': 'Заявка на изменение стоимости',
            'driver': 'Водитель',
            'priority': 'Срочный',
            'taximeter': 'Таксометр'
        }
    ),
    (
        'yutaxi',
        'dispatcher',
        {
            '_id': 'order_id',
            'order': {
                'city': 'екатеринбург',
                'performer': {
                    'taxi_alias': {
                        'id': 'ext_1',
                    },
                    'driver_license': '11123223',
                    'tariff': {
                        'class': 'econom',
                        'currency': 'RUB'
                    }
                },
            }
        },
        {
            'tariff': 'Комбо'
        },
        {
            'city': 'екатеринбург',
            'city_text': 'екатеринбург',
            'order_id': 'ext_1',
            'license': '11123223',
            'tariff': 'Комбо',
            'ticket_theme': 'тикет_снятие_заказа_с_модерации',
            'parks_change_value': 'парки_заявка_на_изменение_стоимости',
            'change_value': 'заявка_на_изменение_стоимости',
            'taxipark': 'Таксопарк'
        }
    ),
    (
        'yutaxi',
        'driver',
        {
            '_id': 'order_id',
            'order': {
                'city': 'Казань',
                'performer': {
                    'taxi_alias': {
                        'id': 'ext_order_d',
                    },
                    'driver_license': '333444',
                    'tariff': {
                        'class': 'comfortplus',
                        'currency': 'RUB'
                    }
                },
            }
        },
        {
            'tariff': ''
        },
        {
            'city': 'Казань',
            'city_text': 'Казань',
            'order_id': 'ext_order_d',
            'license': '333444',
            'tariff': '',
            'ticket_theme': 'Заявка на изменение стоимости',
            'driver_change_value': 'Заявка на изменение стоимости',
            'driver': 'Водитель',
            'priority': 'Срочный',
            'taximeter': 'Таксометр'
        }
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_custom_fields(zendesk_id, price_source, order_proc, kwargs, result):
    if price_source == 'dispatcher':
        values = yield config.CHANGE_PRICE_CUSTOM_VALUES_SPLITTED.get()
    elif price_source == 'driver':
        values = yield config.ZENDESK_DRIVER_PRICE_CUSTOM_FIELDS_VALUES.get()
    zendesk_settings = change_price_report.ZendeskTicketSettings(
        custom_field_values=values[zendesk_id]
    )
    custom_fields = change_price_report._get_custom_fields(
        zendesk_settings, dbh.order_proc.Doc(order_proc), kwargs
    )
    assert custom_fields == result
