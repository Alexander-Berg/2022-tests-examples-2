exports.simple = function (execView) {
    return execView('BRates', {}, {
        'Stocks': {
            'show': 1,
            'blocks': [
                {
                    'datename_max': [
                        null
                    ],
                    'titles': [
                        null
                    ],
                    'text': 'Курсы ЦБ РФ',
                    'type': 'currency',
                    'date_max': [
                        '20170923'
                    ],
                    'rows': [
                        {
                            'xivaformat': '',
                            'onlydate': '1',
                            'is_currency': 1,
                            'ispercent': '',
                            'short': 'USD',
                            'news_alt': '',
                            'text_caps': '<c>USD ЦБ</c>',
                            'groupname': 'x1',
                            'href': 'https://m.news.yandex.ru/quotes/1.html',
                            'text': 'USD ЦБ',
                            'popup': '1',
                            'id': '1',
                            'base_short': 'rub',
                            'i': 1,
                            'n': 1,
                            'symbol': '$',
                            'alt': 'kurs',
                            'geo': '225',
                            'klimit': '10',
                            'data': [
                                {
                                    'value4': '57,6527',
                                    'unofficial': 0,
                                    'date': '20170923',
                                    'value': '57,65',
                                    'delta2': '-0,57',
                                    'value2': '57,65',
                                    'deltaflag': -1,
                                    'datetime': '23/09',
                                    'is_hot': '',
                                    'delta4': '-0,5715',
                                    'delta': '-0,57',
                                    'name_key': 'today'
                                }
                            ],
                            'bank': 'ЦБ РФ',
                            'comment': '',
                            'tomorrow': '1',
                            'title': '',
                            'type': 'currency',
                            'precision': '4'
                        },
                        {
                            'xivaformat': '',
                            'onlydate': '1',
                            'is_currency': 1,
                            'ispercent': '',
                            'short': 'EUR',
                            'news_alt': '',
                            'text_caps': '<c>EUR ЦБ</c>',
                            'groupname': 'x1',
                            'href': 'https://m.news.yandex.ru/quotes/23.html',
                            'text': 'EUR ЦБ',
                            'popup': '1',
                            'id': '23',
                            'base_short': 'rub',
                            'i': 2,
                            'n': 2,
                            'symbol': '€',
                            'alt': 'kurs',
                            'geo': '225',
                            'klimit': '10',
                            'data': [
                                {
                                    'value4': '69,0737',
                                    'unofficial': 0,
                                    'date': '20170923',
                                    'value': '69,07',
                                    'delta2': '-0,19',
                                    'value2': '69,07',
                                    'deltaflag': -1,
                                    'datetime': '23/09',
                                    'is_hot': '',
                                    'delta4': '-0,1898',
                                    'delta': '-0,19',
                                    'name_key': 'today'
                                }
                            ],
                            'bank': 'ЦБ РФ',
                            'comment': '',
                            'tomorrow': '1',
                            'title': '',
                            'type': 'currency',
                            'precision': '4'
                        }
                    ]
                },
                {
                    'datename_max': [
                        '22/09'
                    ],
                    'titles': [
                        '22/09'
                    ],
                    'text': 'Биржевые курсы',
                    'type': 'indexes',
                    'date_max': [
                        '20170922'
                    ],
                    'rows': [
                        {
                            'xivaformat': '',
                            'onlydate': '',
                            'is_currency': 0,
                            'ispercent': '0',
                            'short': 'USD',
                            'news_alt': 'rates.alt.rateformsk',
                            'text_caps': '<c>USD MOEX</c>',
                            'groupname': 'x11',
                            'href': 'https://m.news.yandex.ru/quotes/2002.html',
                            'text': 'USD MOEX',
                            'popup': '1',
                            'id': '2002',
                            'base_short': 'rub',
                            'i': 3,
                            'n': 80,
                            'symbol': '$',
                            'alt': 'kurs',
                            'geo': '10000',
                            'klimit': '10',
                            'data': [
                                {
                                    'value4': '57,5000',
                                    'alt': 'курс MOEX на 22/09',
                                    'unofficial': 0,
                                    'date': '20170922',
                                    'value': '57,50',
                                    'name': '22/09',
                                    'delta2': '-0,40',
                                    'value2': '57,50',
                                    'deltaflag': -1,
                                    'datetime': '22/09',
                                    'is_hot': '',
                                    'delta4': '-0,4000',
                                    'datetime_full': '22/09',
                                    'delta': '-0,40',
                                    'alt_template': 'курс MOEX на %d'
                                }
                            ],
                            'bank': 'MOEX',
                            'comment': '',
                            'tomorrow': '',
                            'title': '',
                            'type': 'indexes',
                            'precision': '4'
                        },
                        {
                            'xivaformat': '',
                            'onlydate': '',
                            'is_currency': 0,
                            'ispercent': '0',
                            'short': 'EUR',
                            'news_alt': 'rates.alt.rateformsk',
                            'text_caps': '<c>EUR MOEX</c>',
                            'groupname': 'x11',
                            'href': 'https://m.news.yandex.ru/quotes/2000.html',
                            'text': 'EUR MOEX',
                            'popup': '1',
                            'id': '2000',
                            'base_short': 'rub',
                            'i': 4,
                            'n': 81,
                            'symbol': '€',
                            'alt': 'kurs',
                            'geo': '10000',
                            'klimit': '10',
                            'data': [
                                {
                                    'value4': '68,6975',
                                    'alt': 'курс MOEX на 22/09',
                                    'unofficial': 0,
                                    'date': '20170922',
                                    'value': '68,70',
                                    'name': '22/09',
                                    'delta2': '-0,45',
                                    'value2': '68,70',
                                    'deltaflag': -1,
                                    'datetime': '22/09',
                                    'is_hot': '',
                                    'delta4': '-0,4500',
                                    'datetime_full': '22/09',
                                    'delta': '-0,45',
                                    'alt_template': 'курс MOEX на %d'
                                }
                            ],
                            'bank': 'MOEX',
                            'comment': '',
                            'tomorrow': '',
                            'title': '',
                            'type': 'indexes',
                            'precision': '4'
                        }
                    ]
                },
                {
                    'datename_max': [
                        '22/09'
                    ],
                    'titles': [
                        '22/09'
                    ],
                    'text': 'Цены на сырьё',
                    'type': 'indexes',
                    'date_max': [
                        '20170922'
                    ],
                    'rows': [
                        {
                            'xivaformat': '',
                            'onlydate': '1',
                            'is_currency': 0,
                            'ispercent': '1',
                            'short': '',
                            'news_alt': '',
                            'text_caps': 'Нефть',
                            'groupname': 'x5',
                            'href': 'https://m.news.yandex.ru/quotes/1006.html',
                            'text': 'Нефть',
                            'popup': '1',
                            'id': '1006',
                            'base_short': '',
                            'i': 5,
                            'n': 122,
                            'symbol': '🛢',
                            'alt': 'ceni',
                            'geo': '983',
                            'klimit': '5',
                            'data': [
                                {
                                    'value4': '56,7900',
                                    'unofficial': 0,
                                    'date': '20170922',
                                    'value': '56,79',
                                    'name': '22/09',
                                    'delta2': '+0,53%',
                                    'value2': '56,79',
                                    'deltaflag': 1,
                                    'datetime': '22/09',
                                    'is_hot': '',
                                    'delta4': '+0,53%',
                                    'delta': '+0,53%'
                                }
                            ],
                            'bank': '',
                            'comment': '',
                            'tomorrow': '',
                            'title': '',
                            'type': 'indexes',
                            'precision': ''
                        }
                    ]
                }
            ],
            'processed': 1,
            'Xivadata': [
                {
                    'ch': 'XDATA.stocks',
                    'ts': 1506114000,
                    'dt': 1337,
                    'key': '1_10000'
                },
                {
                    'ch': 'XDATA.stocks',
                    'ts': 1506114000,
                    'dt': 1337,
                    'key': '23_10000'
                },
                {
                    'ch': 'XDATA.stocks',
                    'ts': 1506113063,
                    'dt': 1337,
                    'key': '2002_10000'
                },
                {
                    'ch': 'XDATA.stocks',
                    'ts': 1506113063,
                    'dt': 1337,
                    'key': '2000_10000'
                },
                {
                    'ch': 'XDATA.stocks',
                    'ts': 1506113400,
                    'dt': 1337,
                    'key': '1006_10000'
                }
            ],
            'adaptive': 1,
            'Xivas': [
                {
                    'ch': 'stocks',
                    'ts': 1506114000,
                    'key': '1'
                },
                {
                    'ch': 'stocks',
                    'ts': 1506114000,
                    'key': '23'
                },
                {
                    'ch': 'stocks',
                    'ts': 1506113063,
                    'key': '2002'
                },
                {
                    'ch': 'stocks',
                    'ts': 1506113063,
                    'key': '2000'
                },
                {
                    'ch': 'stocks',
                    'ts': 1506113400,
                    'key': '1006'
                }
            ]
        }
    });
};
