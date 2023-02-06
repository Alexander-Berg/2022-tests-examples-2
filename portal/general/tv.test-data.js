/* eslint-env es6 */

exports.tv = (execView, {home}) => {
    const settingsJs = home.settingsJs({});
    return execView('Tv', {}, {
        'TV': {
            'af': 0,
            'announces': [
                {
                    'content': 'touch',
                    'domain': 'ru',
                    'from': '2018-08-20 19:00',
                    'geos': '225',
                    'id': 'tvpromo',
                    'lang': 'all',
                    'text': 'Смотрите «МУЗ-ТВ» в прямом эфире',
                    'to': '2018-10-30 19:00',
                    'url': 'https://www.yandex.ru/?stream_channel=897'
                }
            ],
            // eslint-disable-next-line max-len
            'delayed_tabs_url': '/portal/api/data/1/?block=tv&channel_ids=146%2C711%2C1593%2C162%2C427%2C187%2C1683%2C740%2C1000%2C649%2C18%2C79%2C304%2C698%2C1003%2C353&content=touch',
            'exp': '',
            'geo': '213',
            'href': 'https://m.tv.yandex.ru/?utm_source=yamain_touch&utm_medium=informer&utm_campaign=title',
            'processed': 1,
            'show': 1,
            'tabs': [
                {
                    'href': 'https://m.tv.yandex.ru/?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=now',
                    'programms': [
                        {
                            'ch_href': 'https://m.tv.yandex.ru/channels/1003',
                            'ch_id': 1003,
                            'channel': 'Пятница',
                            'end_ts': 1539958500,
                            'full': 'Проект Подиум',
                            'href': 'https://m.tv.yandex.ru/program/3724062?eventId=124286430&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=now',
                            'long_name': 'Проект Подиум',
                            'name': 'Проект Подиум',
                            'pr_id': '124286430',
                            'program_id': '3724062',
                            'start_ts': 1539954900,
                            'time': '16:15',
                            'title': '',
                            'type': ''
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/187',
                            'ch_id': 187,
                            'channel': 'Культура',
                            'end_ts': 1539960300,
                            'full': 'Новости, Экономика, Рынки, Наука, Спорт, Журнал',
                            'href': 'https://m.tv.yandex.ru/program/2367491?eventId=123979691&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=now',
                            'long_name': 'Богач, бедняк. 4-я серия - «Томас»',
                            'name': 'Богач, бедняк. 4-я серия - «Томас»',
                            'pr_id': '123979691',
                            'program_id': '2367491',
                            'start_ts': 1539955500,
                            'time': '16:25',
                            'title': 'Богач, бедняк. (4-я серия - «Томас»)',
                            'type': 'serial',
                            'image_base': '//avatars.mds.yandex.net/get-tv-shows/61190/2a000001667d2dc856f79b1c429f3d407982',
                            'stream': {
                                'content_id': '4ffad50cdae29287a8cda2c891e237ef'
                            }
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/162',
                            'ch_id': 162,
                            'channel': 'НТВ',
                            'end_ts': 1539958200,
                            'full': 'Место встречи. Журнал, No comment, Погода, Портал',
                            'href': 'https://m.tv.yandex.ru/program/2065157?eventId=123983097&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=now',
                            'long_name': 'Место встречи',
                            'name': 'Место встречи',
                            'pr_id': '123983097',
                            'program_id': '2065157',
                            'start_ts': 1539955800,
                            'time': '16:30',
                            'title': '',
                            'type': ''
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/18',
                            'ch_id': 18,
                            'channel': 'РЕН ТВ',
                            'end_ts': 1539957600,
                            'full': 'Новости',
                            'href': 'https://m.tv.yandex.ru/program/3396898?eventId=124100063&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=now',
                            'long_name': 'Новости',
                            'name': 'Новости',
                            'pr_id': '124100063',
                            'program_id': '3396898',
                            'start_ts': 1539955800,
                            'time': '16:30',
                            'title': '',
                            'type': '',
                            'stream': {
                                'content_id': '4ffad50cdae29287a8cda2c891e237ef'
                            }
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/698',
                            'ch_id': 698,
                            'channel': 'Deutsche Welle — Немецкий канал',
                            'end_ts': 1539957600,
                            'full': 'Гадалка',
                            'href': 'https://m.tv.yandex.ru/program/1070841?eventId=124102223&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=now',
                            'long_name': 'Гадалка. 672-я серия - «Неправильная любовь»',
                            'name': 'Гадалка. 672-я серия - «Неправильная…',
                            'pr_id': '124102223',
                            'program_id': '1070841',
                            'start_ts': 1539955800,
                            'time': '16:30',
                            'title': 'Гадалка (672-я серия - «Неправильная любовь»)',
                            'type': '',
                            'image_base': '//avatars.mds.yandex.net/get-tv-shows/61190/2a000001667d2dc856f79b1c429f3d407982',
                            'stream': {
                                'content_id': '4ffad50cdae29287a8cda2c891e237ef'
                            }
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/353',
                            'ch_id': 353,
                            'channel': 'ТНТ',
                            'end_ts': 1539957600,
                            'full': 'Универ. Новая общага',
                            'href': 'https://m.tv.yandex.ru/program/2944305?eventId=124100553&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=now',
                            'long_name': 'Универ. Новая общага. 48-я серия - «Кузина женитьба»',
                            'name': 'Универ. Новая общага. 48-я серия…',
                            'pr_id': '124100553',
                            'program_id': '2944305',
                            'start_ts': 1539955800,
                            'time': '16:30',
                            'title': 'Универ. Новая общага (48-я серия - «Кузина женитьба»)',
                            'type': 'serial'
                        }
                    ],
                    'title': 'Сейчас по ТВ',
                    'type': 'now'
                }, {
                    'href': 'https://m.tv.yandex.ru/?period=evening&utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=evening',
                    'programms': [
                        {
                            'ch_href': 'https://m.tv.yandex.ru/channels/649',
                            'ch_id': 649,
                            'channel': 'ТВ Центр',
                            'end_ts': 1539967200,
                            'full': 'Двое',
                            'href': 'https://m.tv.yandex.ru/program/803263?eventId=124130356&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=evening',
                            'long_name': 'Двое',
                            'name': 'Двое',
                            'pr_id': '124130356',
                            'program_id': '803263',
                            'start_ts': 1539960600,
                            'time': '17:50',
                            'title': '',
                            'type': 'film'
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/427',
                            'ch_id': 427,
                            'channel': 'Пятый канал',
                            'end_ts': 1539964200,
                            'full': 'Братаны-4',
                            'href': 'https://m.tv.yandex.ru/program/763592?eventId=124027107&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=evening',
                            'long_name': 'Братаны-4. 10-я серия',
                            'name': 'Братаны-4. 10-я серия',
                            'pr_id': '124027107',
                            'program_id': '763592',
                            'start_ts': 1539960900,
                            'time': '17:55',
                            'title': 'Братаны-4 (10-я серия)',
                            'type': 'serial'
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/353',
                            'ch_id': 353,
                            'channel': 'ТНТ',
                            'end_ts': 1539963000,
                            'full': 'Универ. Новая общага',
                            'href': 'https://m.tv.yandex.ru/program/2944305?eventId=124100556&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=evening',
                            'long_name': 'Универ. Новая общага. 51-я серия - «Учитель»',
                            'name': 'Универ. Новая общага. 51-я серия…',
                            'pr_id': '124100556',
                            'program_id': '2944305',
                            'start_ts': 1539961200,
                            'time': '18:00',
                            'title': 'Универ. Новая общага (51-я серия - «Учитель»)',
                            'type': 'serial'
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/427',
                            'ch_id': 427,
                            'channel': 'Пятый канал',
                            'end_ts': 1539967200,
                            'full': 'След',
                            'href': 'https://m.tv.yandex.ru/program/7552?eventId=124027108&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=evening',
                            'long_name': 'След. Человек года',
                            'name': 'След. Человек года',
                            'pr_id': '124027108',
                            'program_id': '7552',
                            'start_ts': 1539964200,
                            'time': '18:50',
                            'title': 'След (Человек года)',
                            'type': 'serial'
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/304',
                            'ch_id': 304,
                            'channel': 'Домашний',
                            'end_ts': 1539978300,
                            'full': 'Женщина-зима',
                            'href': 'https://m.tv.yandex.ru/program/257677?eventId=124101685&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=evening',
                            'long_name': 'Женщина-зима. 1-я и 2-я серии',
                            'name': 'Женщина-зима. 1-я и 2-я серии',
                            'pr_id': '124101685',
                            'program_id': '257677',
                            'start_ts': 1539964800,
                            'time': '19:00',
                            'title': 'Женщина-зима (1-я и 2-я серии)',
                            'type': 'film'
                        }, {
                            'ch_href': 'https://m.tv.yandex.ru/channels/79',
                            'ch_id': 79,
                            'channel': 'СТС',
                            'end_ts': 1539975600,
                            'full': 'Неподимый и несокрушимый меч короля Артура',
                            'href': 'https://m.tv.yandex.ru/program/3731485?eventId=124174457&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=evening',
                            'long_name': 'Неподимый и несокрушимый меч Артура',
                            'name': 'Неподимый и несокрушимый меч короля Артура',
                            'pr_id': '124174457',
                            'program_id': '3731485',
                            'start_ts': 1539966600,
                            'time': '19:30',
                            'title': '',
                            'type': 'film'
                        }
                    ],
                    'title': 'Вечером',
                    'type': 'evening'
                }, {
                    'channel': 1,
                    'channel_id': '146',
                    'chname': 'Первый',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/146?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '711',
                    'chname': 'Россия 1',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/711?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '1593',
                    'chname': 'Матч!',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/1593?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '162',
                    'chname': 'НТВ',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/162?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '427',
                    'chname': 'Пятый канал',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/427?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '187',
                    'chname': 'Культура',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/187?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '1683',
                    'chname': 'Россия 24',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/1683?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '740',
                    'chname': 'Карусель',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/740?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '1000',
                    'chname': 'ОТР',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/1000?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '649',
                    'chname': 'ТВ Центр',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/649?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '18',
                    'chname': 'РЕН ТВ',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/18?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '79',
                    'chname': 'СТС',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/79?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '304',
                    'chname': 'Домашний',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/304?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '698',
                    'chname': 'ТВ-3',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/698?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '1003',
                    'chname': 'Пятница',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/1003?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }, {
                    'channel': 1,
                    'channel_id': '353',
                    'chname': 'ТНТ',
                    'delayed_content': 1,
                    'href': 'https://m.tv.yandex.ru/channels/353?utm_source=yamain_touch&utm_medium=informer&utm_campaign=tabs&utm_content=channel',
                    'programms': [],
                    'type': 'channel'
                }
            ]
        },
        settingsJs
    }) + execView('IUa2', {}, {
        'BrowserDesc': {},
        ua: {
            'tabRole': 'test'
        },
        settingsJs
    }) + `<script>
        BEM.DOM.decl({block: 'swiper', modName: 'load-data', modVal: 'yes'}, {
            _loadExternalData: function () {}
        });
    </script>` +
    `<script>
        ${settingsJs.getRawScript()}
        home.partials.tv.data['evening'][0].full = 'Очень длинное название программы. Безумно длинное название программы.'
        home.partials.tv.data['146'] = [
            {
                channelId: '146',
                counter: 'tv.links.channel',
                full: 'Время покажет',
                href: 'http://m.tv.yandex.ru/program/998000?eventId=125100087&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=channel',
                inner__mod: '',
                itemParams: {
                    itemView: 'tv__item'
                },
                mod: '',
                noBlockDisplay: true,
                stat: ' data-statlog="tv.links.channel"',
                staticHost: '//yastatic.net',
                time: '12:15'
            }, {
                channelId: '146',
                counter: 'tv.links.channel',
                full: 'Время покажет 2. Очень длинное название. Безумно длинное название',
                href: 'http://m.tv.yandex.ru/program/998000?eventId=125100087&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=channel',
                inner__mod: '',
                itemParams: {
                    itemView: 'tv__item'
                },
                mod: '',
                noBlockDisplay: true,
                stat: ' data-statlog="tv.links.channel"',
                staticHost: '//yastatic.net',
                time: '15:00'
            }, {
                channelId: '146',
                counter: 'tv.links.channel',
                full: 'Время покажет 3',
                href: 'http://m.tv.yandex.ru/program/998000?eventId=125100087&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=channel',
                inner__mod: '',
                itemParams: {
                    itemView: 'tv__item'
                },
                mod: '',
                noBlockDisplay: true,
                stat: ' data-statlog="tv.links.channel"',
                staticHost: '//yastatic.net',
                time: '15:15'
            }, {
                'separator': 1,
                'type': 'separator'
            }, {
                channelId: '146',
                counter: 'tv.links.channel',
                full: 'Время покажет 4',
                href: 'http://m.tv.yandex.ru/program/998000?eventId=125100087&utm_source=yamain_touch&utm_medium=informer&utm_campaign=link&utm_content=channel',
                inner__mod: '',
                itemParams: {
                    itemView: 'tv__item'
                },
                mod: '',
                noBlockDisplay: true,
                stat: ' data-statlog="tv.links.channel"',
                staticHost: '//yastatic.net',
                time: '16:00'
            }
        ];
    </script>`;
};
