const simple = {
        Traffic: {
            forecast: [
                {
                    hour: 12,
                    icon: 'green',
                    rate: 3
                },
                {
                    hour: 13,
                    icon: 'yellow',
                    rate: 5
                },
                {
                    hour: 14,
                    icon: 'red',
                    rate: 7
                },
                {
                    hour: 15,
                    icon: 'green',
                    rate: 8
                },
                {
                    hour: 16,
                    icon: 'green',
                    rate: 9
                }
            ],
            forecast_description: 'Ближайшие 5&nbsp;часов дороги свободны',
            forecast_enabled: 1,
            forecast_max: 4,
            href: 'https://yandex.ru/maps/213/moscow/probki',
            processed: 1,
            rate: 3,
            show: 1
        }
    },
    noForecast = {
        Traffic: {
            description: 'Местами затруднения',
            href: 'https://yandex.ru/maps/213/moscow/probki',
            icon: 'yellow',
            processed: 1,
            rate: 4,
            show: 1
        }
    },
    covid = {
        Covid_isolation: {
            'color': '#FFC400',
            'icon': '2a3_yellow',
            'icon_version': '13',
            'processed': 1,
            'score': '3,2',
            'show': 1,
            'text': 'Большинство людей дома. И вы оставайтесь.',
            'text_short': 'мало',
            'title': 'Самоизоляция',
            'url': 'https://yandex.ru/maps/'
        }
    };

function view (html, blocks, wide, hd) {
    const mainClass = ['traffic', 'weather2']
        .map(name => {
            return `main_${name}_${blocks.includes(name) || name === 'traffic' ? 'yes' : 'no'}`;
        })
        .join(' ');
    return `<style>
    body {
        font-family: 'YS Text', 'Helvetica Neue', Arial, sans-serif;
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
    .main__item {
        display: inline-grid;
        height: 64px;
    }
    .b-page_hd_yes .main__item {
        height: 76px;
    }
    </style>
    <div class="b-page b-page_width_${wide ? 'wide' : 'normal'} b-page_hd_${hd ? 'yes' : 'no'}">
        <div class="${mainClass} content">
            <div class="main__item main__traffic">${html}</div>
        </div>
    </div>`;
}

function getAll(suffix = '') {
    const thisMock = '/?datafile=white/blocks/yabro/traffic/traffic.test-data.js&dataname=';

    const getFrame = name => {
            return `<a href="${thisMock}${name}" target="${name}">${name}
                <iframe name="${name}" src="${thisMock}${name}"></iframe>
                </a>`;
        },
        frames = [
            'simpleSmall' + suffix,
            'simpleWide' + suffix,
            'noForecastSmall' + suffix,
            'noForecastWide' + suffix
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
                grid-template-columns: repeat(2, 1fr);
                grid-auto-rows: 250px;
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

    simpleSmall: (execView) => {
        return view(execView('Traffic', simple), ['weather2']);
    },
    simpleWide: (execView) => {
        return view(execView('Traffic', simple), ['weather2'], true);
    },

    simpleSmallHd: (execView) => {
        return view(execView('Traffic', simple), ['weather2'], false, true);
    },
    simpleWideHd: (execView) => {
        return view(execView('Traffic', simple), ['weather2'], true, true);
    },

    noForecastSmall: (execView) => {
        return view(execView('Traffic', noForecast), ['weather2']);
    },
    noForecastWide: (execView) => {
        return view(execView('Traffic', noForecast), ['weather2'], true);
    },
    noForecastSmallHd: (execView) => {
        return view(execView('Traffic', noForecast), ['weather2'], false, true);
    },
    noForecastWideHd: (execView) => {
        return view(execView('Traffic', noForecast), ['weather2'], true, true);
    },

    covidSmall: (execView) => {
        return view(execView('Traffic', Object.assign({}, covid, simple)), ['weather2']);
    },
    covidWide: (execView) => {
        return view(execView('Traffic', Object.assign({}, covid, simple)), ['weather2'], true);
    },

    all: () => getAll(),
    allhd: () => getAll('Hd')
};

