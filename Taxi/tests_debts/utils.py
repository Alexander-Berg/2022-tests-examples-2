CONFIG_DEBSTATUSES_CONTENT = {
    'default': {
        'default': {
            'debt_info': {
                'title': {
                    'key': 'debts.debtstatuses.debt_info.title.debt.default',
                    'keyset': 'client_messages',
                },
                'action_buttons': [],
            },
        },
    },
    'debt': {
        'default': {
            'header': {
                'title': {
                    'text': {
                        'key': 'debts.debtstatuses.header.title.debt.default',
                        'keyset': 'client_messages',
                    },
                    'text_color': 'black',
                },
                'subtitle': {
                    'text': {
                        'key': (
                            'debts.debtstatuses.header.subtitle.debt.default'
                        ),
                        'keyset': 'client_messages',
                    },
                    'text_color': 'black',
                },
                'default_loading_next_step_text': {
                    'key': (
                        'debts.debtstatuses.header.title.processing.default'
                    ),
                    'keyset': 'client_messages',
                },
                'background_color': 'white',
                'is_loading': True,
            },
            'debt_info': {
                'title': {
                    'key': 'debts.debtstatuses.debt_info.title.debt.default',
                    'keyset': 'client_messages',
                },
                'subtitle': {
                    'key': (
                        'debts.debtstatuses.debt_info.subtitle.debt.default'
                    ),
                    'keyset': 'client_messages',
                },
                'action_buttons': [
                    {
                        'title': {
                            'text': {
                                'key': (
                                    'debts.debtstatuses.debt_info.'
                                    'cash_payment_action_button.title'
                                ),
                                'keyset': 'client_messages',
                            },
                            'text_color': 'cash_payment_button_title_color',
                        },
                        'subtitle': {
                            'text': {
                                'key': (
                                    'debts.debtstatuses.debt_info.'
                                    'cash_payment_action_button.subtitle'
                                ),
                                'keyset': 'client_messages',
                            },
                            'text_color': 'cach_payment_button_subtitle_color',
                        },
                        'background_color': 'cash_payment_background_color',
                        'type': 'move_to_cash',
                    },
                    {
                        'title': {
                            'text': {
                                'key': (
                                    'debts.debtstatuses.debt_info.'
                                    'pay_debt_action_button.title'
                                ),
                                'keyset': 'client_messages',
                            },
                            'text_color': 'pay_debt_button_title_color',
                        },
                        'subtitle': {
                            'text': {
                                'key': (
                                    'debts.debtstatuses.debt_info.'
                                    'pay_debt_action_button.subtitle'
                                ),
                                'keyset': 'client_messages',
                            },
                            'text_color': 'pay_debt_button_subtitle_color',
                        },
                        'background_color': 'pay_debt_button_background_color',
                        'type': 'pay_debt',
                    },
                ],
                'is_separator_visible': True,
                'payment_method_action_enabled': True,
            },
        },
    },
}

CLIENT_MESSAGES = {
    'debts.debtstatuses.header.title.debt.default': {
        'ru': 'У вас долг %(amount)s',
    },
    'debts.debtstatuses.header.title.processing.default': {
        'ru': 'Оплата долга',
    },
    'debts.debtstatuses.header.subtitle.debt.default': {
        'ru': 'В вашем регионе нет оплаты наличными',
    },
    'debts.debtstatuses.header.subtitle.cash_available': {
        'ru': 'Поездки и доставка только за наличные',
    },
    'debts.debtstatuses.debt_info.subtitle.debt.default': {
        'ru': 'В вашем регионе нельзя оплачивать наличными',
    },
    'debts.debtstatuses.debt_info.title.debt.default': {
        'ru': 'У вас долг за поездку',
    },
    'debts.debtstatuses.debt_info.ride_info.title.ride': {
        'ru': 'Поездка %(date)s',
    },
    'debts.debtstatuses.debt_info.ride_info.title.delivery': {
        'ru': 'Доставка %(date)s',
    },
    'debts.debtstatuses.debt_info.ride_info.general.title': {
        'ru': '%(trips_count)s поездок',
    },
    'debts.debtstatuses.debt_info.ride_info.date_format': {
        'ru': '%d.%m.%Y %H:%M',
    },
    'debts.debtstatuses.debt_info.cash_payment_action_button.title': {
        'ru': 'Заказать за наличные',
    },
    'debts.debtstatuses.debt_info.cash_payment_action_button.subtitle': {
        'ru': 'Заказать за наличные (подзаголовок)',
    },
    'debts.debtstatuses.debt_info.pay_debt_action_button.title': {
        'ru': 'Оплатить %(amount)s',
    },
    'debts.debtstatuses.debt_info.pay_debt_action_button.subtitle': {
        'ru': 'Оплатить (подзаголовок)',
    },
}

ORDER_PROC_BULK_GET_FIELDS = [
    'order.request.destinations.short_text',
    'order.performer.tariff.class',
    'order.created',
    'order.nz',
    'payment_tech.hold_initiated',
    'payment_tech.type',
    'order_info.statistics.status_updates.q',
    'order_info.statistics.status_updates.a.status',
    'payment_tech.need_cvn',
]

TARIFF_TRANSLATIONS = {
    'currency.rub': {'ru': 'руб'},
    'currency.usd': {'ru': 'usd'},
    'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
    'currency_sign.rub': {'ru': '₽'},
    'currency_sign.usd': {'ru': '$'},
}
