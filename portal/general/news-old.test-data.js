const simpleStocks = [{
        alt: 'курс MOEX на 03/10 18:48',
        alt_template: 'курс MOEX на %d %t',
        datetime_full: '03/10 18:48',
        delta: '+0,18',
        delta_raw: '0.18',
        history: ['65.6825', '65.5000', '65.0000', '65.5350', '65.6225', '65.8000', '65.8925'],
        href: 'https://news.yandex.ru/',
        id: '2002',
        is_hot: '',
        short_caps: '<c>USD</c>',
        symbol: '$',
        text: 'USD MOEX',
        value: '65,68'
    }, {
        alt: 'курс MOEX на 03/10 18:48',
        alt_template: 'курс MOEX на %d %t',
        datetime_full: '03/10 18:48',
        delta: '-0,08',
        delta_raw: '-0.08',
        history: ['75.7025', '75.6200', '75.2000', '76.1000', '76.3750', '77.2600', '77.5550'],
        href: 'https://news.yandex.ru/',
        id: '2000',
        is_hot: '1',
        short_caps: '<c>EUR</c>',
        symbol: '€',
        text: 'EUR MOEX',
        value: '75,70'
    }],
    stocksWithNscale = [{
        alt: 'курс MOEX на 03/10 18:48',
        alt_template: 'курс MOEX на %d %t',
        datetime_full: '03/10 18:48',
        delta: '+0,18',
        delta_raw: '0.18',
        history: ['65.6825', '65.5000', '65.0000', '65.5350', '65.6225', '65.8000', '65.8925'],
        href: 'https://news.yandex.ru/',
        id: '2002',
        is_hot: '1',
        short_caps: '<c>USD</c>',
        symbol: '$',
        text: 'USD MOEX',
        value: '65,68'
    }, {
        alt: 'курс MOEX на 03/10 18:48',
        alt_template: 'курс MOEX на %d %t',
        datetime_full: '03/10 18:48',
        delta: '0,00',
        delta_raw: '0.00',
        history: ['75.7025', '75.6200', '75.2000', '76.1000', '76.3750', '77.2600', '77.5550'],
        href: 'https://news.yandex.ru/',
        id: '2000',
        is_hot: '',
        short_caps: '<c>EUR</c>',
        symbol: '€',
        text: 'EUR MOEX',
        value: '75,70'
    }, {
        alt: 'цена на 03/10 18:44',
        alt_template: 'цена на %d %t',
        datetime_full: '03/10 18:44',
        delta: '+0,71%',
        delta_raw: '0.71',
        history: ['85.2800', '84.6800', '85.1100', '82.8600', '81.2700', '81.6500', '81.5000'],
        href: 'https://news.yandex.ru/',
        id: '1006',
        is_hot: '1',
        short_caps: 'Нефть',
        symbol: '&#128738;',
        text: 'Нефть',
        value: '85,28',
        nscale: 'за 100'

    }],
    simple = {
        Topnews: {
            BigDay: '4',
            BigMonth: 'октября',
            BigWday: 'четверг',
            default_tab_index: 0,
            exp: null,
            fulltime: '12:46 04/10/2018',
            href: 'https://news.yandex.ru/',
            id: '1538645822',
            iter_timestamp: '1538645822',
            numbers: {
                show: 1
            },
            processed: 1,
            save_tab: null,
            show: 1,
            tabs: [{
                'default': 1,
                href: 'https://news.yandex.ru/',
                href_mobile: 'https://news.yandex.ru/',
                id: 'glob_225',
                idx: 0,
                key: 'news',
                name: 'news',
                news: [{
                    href: 'https://news.yandex.ru/',
                    hreftext: 'погиб в авиакатастрофе',
                    i: 1,
                    id: '4240da11',
                    ishot: null,
                    text: 'Заместитель Юрия Чайки '
                }, {
                    href: 'https://news.yandex.ru/',
                    hreftext: 'из-за границы с Чечней открыли стрельбу',
                    i: 2,
                    id: '5643cfb5',
                    ishot: null,
                    text: 'В Ингушетии на протестах '
                }, {
                    href: 'https://news.yandex.ru/',
                    hreftext: 'о бое в Керченском проливе',
                    i: 3,
                    id: '165c2413',
                    ishot: 1,
                    text: 'В Крыму не восприняли всерьез слова Украины '
                }, {
                    href: '/',
                    hreftext: 'персоной нон грата консула Венгрии в Берегове',
                    i: 4,
                    id: '363f272b',
                    ishot: null,
                    text: 'МИД Украины объявил '
                }, {
                    href: 'https://news.yandex.ru/',
                    hreftext: 'полки в плацкарте на капсулы',
                    i: 5,
                    id: '66026cd4',
                    ishot: null,
                    text: 'РЖД может заменить '
                }],
                statid: 'news.news',
                title: 'Сейчас в СМИ',
                ts: '1538645822'
            }, {
                alias: 'Moscow',
                geo: '213',
                href: 'https://news.yandex.ru/',
                href_mobile: 'https://news.yandex.ru/',
                id: 'geo_213',
                idx: 1,
                key: 'region',
                name: 'region',
                news: [{
                    href: 'https://news.yandex.ru/',
                    hreftext: 'около 40% месячной нормы осадков',
                    i: 1,
                    id: 'dea261d6',
                    ishot: null,
                    text: 'В Москве за сутки выпало '
                }],
                statid: 'news.region',
                title: 'в Москве',
                ts: '1538645822'
            }],
            time: '12:46',
            topnews_stocks: simpleStocks,
            topnews_stocks_title: 'Наличные курсы, продажа:'
        }
    },
    multiline = {
        Topnews: {
            BigDay: '4',
            BigMonth: 'октября',
            BigWday: 'четверг',
            default_tab_index: 0,
            exp: null,
            fulltime: '12:46 04/10/2018',
            href: 'https://news.yandex.ru/',
            id: '1538645822',
            iter_timestamp: '1538645822',
            numbers: {
                show: 1
            },
            processed: 1,
            save_tab: null,
            show: 1,
            tabs: [{
                'default': 1,
                href: 'https://news.yandex.ru/',
                href_mobile: 'https://news.yandex.ru/',
                id: 'glob_225',
                idx: 0,
                key: 'news',
                name: 'news',
                news: [{
                    href: 'https://news.yandex.ru/',
                    hreftext: 'погиб в авиакатастрофе',
                    i: 1,
                    id: '4240da11',
                    ishot: null,
                    text: 'Заместитель Юрия Чайки '
                }, {
                    href: 'https://news.yandex.ru/',
                    hreftext: 'из-за границы с Чечней открыли стрельбу',
                    i: 2,
                    id: '5643cfb5',
                    ishot: null,
                    text: 'В Ингушетии на протестах '
                }, {
                    href: 'https://news.yandex.ru/',
                    hreftext: 'о бое в Керченском проливе персоной консула из-за границы МИД Украины',
                    i: 3,
                    id: '165c2413',
                    ishot: 1,
                    text: 'В Крыму не восприняли всерьез слова Украины '
                }, {
                    href: '/',
                    hreftext: 'персоной нон грата консула Венгрии в Берегове',
                    i: 4,
                    id: '363f272b',
                    ishot: null,
                    text: 'МИД Украины объявил '
                }, {
                    href: 'https://news.yandex.ru/',
                    hreftext: 'полки в плацкарте на капсулы',
                    i: 5,
                    id: '66026cd4',
                    ishot: null,
                    text: 'РЖД может заменить '
                }],
                statid: 'news.news',
                title: 'Сейчас в СМИ',
                ts: '1538645822'
            }, {
                alias: 'Moscow',
                geo: '213',
                href: 'https://news.yandex.ru/',
                href_mobile: 'https://news.yandex.ru/',
                id: 'geo_213',
                idx: 1,
                key: 'region',
                name: 'region',
                news: [{
                    href: 'https://news.yandex.ru/',
                    hreftext: 'около 40% месячной нормы осадков',
                    i: 1,
                    id: 'dea261d6',
                    ishot: null,
                    text: 'В Москве за сутки выпало '
                }],
                statid: 'news.region',
                title: 'в Москве',
                ts: '1538645822'
            }],
            time: '12:46',
            topnews_stocks: stocksWithNscale
        }
    },
    covidGroups = [
        {
            'blocks': [
                {
                    'chat_id': '1/0/5683a013',
                    'icon': 'covid_mos_icon',
                    'subtitle': 'Оперштаб Москвы',
                    'timestamp': 1585209662000018,
                    'title': 'В России зафиксировано',
                    'url': '/e8547709-000',
                    'url_subtitle': '/e8547709'
                },
                {
                    'chat_id': '1/0/5683a013',
                    'icon': 'covid_mos_icon',
                    'subtitle': 'Оперштаб Москвы',
                    'timestamp': 1585209302000018,
                    'title': 'Коронавирус. Закрытие ресторанов и парков, и всех-всех-все-всех-всех и ещё других и собак',
                    'url': '/e8547709-111',
                    'url_subtitle': 'e8547709'
                },
                {
                    'chat_id': '1/0/d68d12f0',
                    'icon': 'covid_rus_icon',
                    'subtitle': 'Коронавирус в России',
                    'timestamp': 1585210027000022,
                    'title': '182 новых случая',
                    'url': '/02b9f3b2-000',
                    'url_subtitle': '/02b9f3b2'
                },
                {
                    'chat_id': '1/0/d68d12f0',
                    'icon': 'covid_rus_icon',
                    'subtitle': 'Коронавирус в России',
                    'timestamp': 1585203567000022,
                    'title': 'Россия с 27 марта прекратит',
                    'url': '/02b9f3b2-111',
                    'url_subtitle': '/02b9f3b2'
                }
            ],
            'tab_id': 'main',
            'title': 'Коронавирус',
            'url_title': '/panic!'
        }
    ],
    covidList = [
        {
            'blocks': [
                {
                    'block_id': 'b1',
                    'title': 'Рекомендации приезжающим',
                    'url': 'https://yandex.ru/search',
                    'url_subtitle': 'https://yandex.ru/search'
                },
                {
                    'block_id': 'b2',
                    'title': 'Симптомы коронавируса',
                    'url': '/gaq',
                    'url_subtitle': 'https://yandex.ru'
                },
                {
                    'block_id': 'b3',
                    'subtitle': '8-800-2000-112',
                    'title': 'Горячая линия Роспотребнадзора',
                    'url': '/searchchch'
                },
                {
                    'block_id': 'b4',
                    'title': 'Рекомендации ВОЗ для людей на карантине для людей на карантине для людей на карантине',
                    'url': '/gohome'
                }
            ],
            'tab_id': 'question',
            'title': 'Важное'
        }
    ],
    covidLinks = [
        {
            'tab_id': 'map',
            'title': 'Карта',
            'url_title': '/map'
        },
        {
            'tab_id': 'news',
            'title': 'Сейчас в СМИ',
            'url_title': '/news'
        }
    ],
    simpleWithIcons = addIcons(simple),
    multilineWithIcons = addIcons(multiline);

function addIcons(data) {
    const news = data.Topnews;
    const dummyimage = require('../../../../frontend-node/lib/dummyimage').patternRedBorder,
        iconUrl = `${dummyimage}&color=rgb(200,200,255)&w=20&h=20`;

    return {
        Topnews: {
            ...news,
            tabs: [
                {
                    ...news.tabs[0],
                    news: news.tabs[0].news.map((item, i) => {
                        return {
                            agency_logo: i ? iconUrl : '/badurl',
                            agency_title: 'test agency',
                            ...item
                        };
                    })
                },
                {
                    ...news.tabs[1],
                    news: news.tabs[1].news.map(item => {
                        return {
                            agency_logo: iconUrl,
                            agency_title: 'test agency',
                            ...item
                        };
                    })
                }
            ]
        }
    };
}

function view(html, htmlClass, hd) {
    return `<style>
    body {
        --item-width: 136px;
        --item-height: calc(var(--item-width) * 96 / 136);
        --item-gap: 8px;
        --item-text-main: 12px;
        --item-text-header: 18px;
        background: #3de;
    }
    .b-page {
        visibility: visible;
    }
    .b-page_hd_yes {
        --item-width: 164px;
        --item-ratio: 1.205;
        --item-height: calc(var(--item-width) * 112 / 164);
    }
    .content {
        width: calc(4.2 * var(--item-width));
    }
    .fonts_loaded_yes {
        font-family: 'YS Text', 'Helvetica Neue', Arial, sans-serif;
    }
    </style>
    <div class="${htmlClass || ''} b-page b-page_hd_${hd ? 'yes' : 'no'}"><div class="content">
        <div class="main__item main__news">
            ${html}
        </div>
    </div></div>`;
}

function all(suffix = '') {
    const thisMock = '/?datafile=white/blocks/yabro/news-old/news-old.test-data.js&dataname=';

    const getFrame = name => {
            return `<a href="${thisMock}${name}" target="${name}">${name}
                <iframe name="${name}" src="${thisMock}${name}"></iframe>
                </a>`;
        },
        frames = [
            'simpleArial' + suffix,
            'simpleYS' + suffix,
            'multilineArial' + suffix,
            'multilineYS' + suffix,
            'iconsArial' + suffix,
            'iconsYS' + suffix,
            'iconsMultilineArial' + suffix,
            'iconsMultilineYS' + suffix,
            'stub' + suffix
        ];

    return `<!doctype html>
        <style>
            html, body {
                margin: 0;
                padding: 0;
            }
            .content {
                display: grid;
                padding: 1em;
                grid-template-columns: repeat(1, 1fr);
                grid-auto-rows: 300px;
                grid-gap: 1em;
            }
            iframe {
                width: 100%;
                height: 95%;
        </style>
        <body>
            <div class="content">
                ${frames.map(getFrame).join('')}
            </div>
        </body>`;
}
module.exports = {
    simpleArial: (execView) => {
        return view(execView('NewsOld', simple));
    },
    simpleYS: (execView) => {
        return view(execView('NewsOld', simple), 'fonts_loaded_yes');
    },
    simpleArialHd: (execView) => {
        return view(execView('NewsOld', simple), '', true);
    },
    simpleYSHd: (execView) => {
        return view(execView('NewsOld', simple), 'fonts_loaded_yes', true);
    },
    multilineArial: (execView) => {
        return view(execView('NewsOld', multiline), '');
    },
    multilineYS: (execView) => {
        return view(execView('NewsOld', multiline), 'fonts_loaded_yes');
    },
    multilineArialHd: (execView) => {
        return view(execView('NewsOld', multiline), '', true);
    },
    multilineYSHd: (execView) => {
        return view(execView('NewsOld', multiline), 'fonts_loaded_yes', true);
    },
    stub: (execView) => {
        return view(execView('NewsOld__stub'));
    },
    stubHd: (execView) => {
        return view(execView('NewsOld__stub'), '', true);
    },
    iconsArial: (execView) => {
        return view(execView('NewsOld', simpleWithIcons));
    },
    iconsYS: (execView) => {
        return view(execView('NewsOld', simpleWithIcons), 'fonts_loaded_yes');
    },
    iconsArialHd: (execView) => {
        return view(execView('NewsOld', simpleWithIcons), '', true);
    },
    iconsYSHd: (execView) => {
        return view(execView('NewsOld', simpleWithIcons), 'fonts_loaded_yes', true);
    },
    iconsMultilineArial: (execView) => {
        return view(execView('NewsOld', multilineWithIcons), '');
    },
    iconsMultilineYS: (execView) => {
        return view(execView('NewsOld', multilineWithIcons), 'fonts_loaded_yes');
    },
    iconsMultilineArialHd: (execView) => {
        return view(execView('NewsOld', multilineWithIcons), '', true);
    },
    iconsMultilineYSHd: (execView) => {
        return view(execView('NewsOld', multilineWithIcons), 'fonts_loaded_yes', true);
    },
    covidGroups: (execView) => {
        return view(execView('NewsOld', Object.assign({}, simpleWithIcons, {
            Covid: {
                show: 1,
                tabs: covidGroups
            }
        })), 'fonts_loaded_yes', false);
    },
    covidList: (execView) => {
        return view(execView('NewsOld', Object.assign({}, simpleWithIcons, {
            Covid: {
                show: 1,
                tabs: covidList
            }
        })), 'fonts_loaded_yes', false);
    },
    covidMixed: (execView) => {
        return view(execView('NewsOld', Object.assign({}, simpleWithIcons, {
            Covid: {
                show: 1,
                tabs: [].concat(covidGroups, covidList, covidLinks)
            }
        })), 'fonts_loaded_yes', false);
    },
    covidGroupsHd: (execView) => {
        return view(execView('NewsOld', Object.assign({}, simpleWithIcons, {
            Covid: {
                show: 1,
                tabs: covidGroups
            }
        })), 'fonts_loaded_yes', true);
    },
    covidListHd: (execView) => {
        return view(execView('NewsOld', Object.assign({}, simpleWithIcons, {
            Covid: {
                show: 1,
                tabs: covidList
            }
        })), 'fonts_loaded_yes', true);
    },
    covidMixedHd: (execView) => {
        return view(execView('NewsOld', Object.assign({}, simple, {
            Covid: {
                show: 1,
                tabs: [].concat(covidGroups, covidList, covidLinks)
            }
        })), 'fonts_loaded_yes', true);
    },
    all: () => all(),
    allhd: () => all('Hd')
};
