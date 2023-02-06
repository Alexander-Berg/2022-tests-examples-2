exports.simple = function (execView) {
    return '<style>.weather__icon{background-color:purple;}</style><div class="rows"><div class="rows__cell rows__cell_header">' + execView('Header', {}, {
        'BigCityName': 'Москва',
        'Weather': {
            't2name': 'вечер',
            'iconalt': 'пасмурно',
            'iv3u1': 'bkn_d',
            'geoid': '213',
            't1': '+15',
            'moburl': 'https://yandex.ru/pogoda/moscow',
            'color': '#f6f3d6',
            't2': '+13',
            'url': 'https://yandex.ru/pogoda/moscow',
            'Xivas': [
                {
                    'ch': 'weather_v2',
                    'ts': 1505991600,
                    'key': '213'
                }
            ],
            't3name': 'ночь',
            'show': 1,
            't3': '+9',
            'processed': 1,
            'generate_ts': 1505993220,
            'notice_url': 'https://yandex.ru/pogoda/moscow/details#tomorrow'
        },
        'Traffic': {
            'time': '14:28',
            'mobile': {
                'lang': 'all',
                'geo': '213',
                'url': 'http://mobile.yandex.ru/maps/',
                'mordatype': 'all',
                'linkid': 'mobile'
            },
            'future_description': 'К 19 часам пробки вырастут до  7 баллов',
            'rate': '4',
            'future': [
                {
                    'hour': '15',
                    'jams': 4
                },
                {
                    'hour': '16',
                    'jams': 5
                },
                {
                    'hour': '17',
                    'jams': 5
                },
                {
                    'hour': '18',
                    'jams': 6
                },
                {
                    'hour': '19',
                    'jams': 7
                }
            ],
            'href': 'https://yandex.ru/maps/213/moscow/probki',
            'personal': 1,
            '_href_raw': 'https://yandex.ru/maps/213/moscow/probki',
            'show': 1,
            'personal_link': 1,
            'processed': 1,
            'future_enabled': 1,
            'descr': 'Местами затруднения',
            'rateaccus': 'балла',
            'future_max': 7,
            'class': 'yw',
            'trf': 0
        },
        'Stocks': {
            'show': '1',
            'processed': 1,
            'lite': [
                {
                    'symbol': '$',
                    'history': [
                        '58.2242',
                        '58.1290',
                        '58.0993',
                        '57.6242',
                        '57.5336',
                        '57.7706',
                        '57.6679'
                    ],
                    'alt': 'курс ЦБ РФ на 22/09',
                    'value': '58,22',
                    'is_hot': '',
                    'delta_raw': '0.09',
                    'datetime_full': '22/09',
                    'delta': '+0,09',
                    'text': 'USD',
                    'href': 'https://news.yandex.ru/quotes/1.html',
                    'alt_template': 'курс ЦБ РФ на %d',
                    'id': '1',
                    'Xivadata': {
                        'dt': 1337,
                        'ts': 1506027600,
                        'ch': 'XDATA.stocks',
                        'key': '1_10000'
                    }
                },
                {
                    'symbol': '€',
                    'history': [
                        '69.2635',
                        '69.7664',
                        '69.6785',
                        '68.7514',
                        '68.5801',
                        '68.6950',
                        '69.0977'
                    ],
                    'alt': 'курс ЦБ РФ на 22/09',
                    'value': '69,26',
                    'is_hot': '',
                    'delta_raw': '-0.51',
                    'datetime_full': '22/09',
                    'delta': '−0,51',
                    'text': 'EUR',
                    'href': 'https://news.yandex.ru/quotes/23.html',
                    'alt_template': 'курс ЦБ РФ на %d',
                    'id': '23',
                    'Xivadata': {
                        'dt': 1337,
                        'ts': 1506027600,
                        'ch': 'XDATA.stocks',
                        'key': '23_10000'
                    }
                },
                {
                    'symbol': '🛢',
                    'history': [
                        '55.8800',
                        '56.2000',
                        '55.4200',
                        '55.4400',
                        '55.5500',
                        '55.2800',
                        '55.1300'
                    ],
                    'alt': 'цена на 21/09 14:17',
                    'value': '55,88',
                    'is_hot': '',
                    'delta_raw': '-0.57',
                    'datetime_full': '21/09 14:17',
                    'delta': '−0,57%',
                    'text': 'Нефть',
                    'href': 'https://news.yandex.ru/quotes/1006.html',
                    'alt_template': 'цена на %d %t',
                    'id': '1006',
                    'Xivadata': {
                        'dt': 1337,
                        'ts': 1505992620,
                        'ch': 'XDATA.stocks',
                        'key': '1006_10000'
                    }
                }
            ]
        },
        'MordaZone': 'ru'
    }) + '</div></div>';
};
