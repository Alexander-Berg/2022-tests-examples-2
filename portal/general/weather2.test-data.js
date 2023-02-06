/* eslint max-params: 1 */
const allData = {
        Weather: {
            alert: {},
            extra_info: {
                humidity: '57%',
                pressure: '747 мм рт. ст.',
                wind: '1.0 м/с, ЮЗ'
            },
            color: '#f8f4d0',
            generate_ts: 1535718877,
            geoid: '2',
            iconalt: 'малооблачно',
            iv3u1: 'bkn_ra_d',
            notice_url: 'https://yandex.ru/pogoda/details?lat=59.958786&lon=30.406012#tomorrow',
            processed: 1,
            show: 1,
            t1: '+22',
            t2: '+15',
            t2icon: 'bkn_+ra_d',
            t2iconalt: 'облачно с прояснениями',
            t2name: 'днём',
            t3: '−3',
            t3icon: 'bkn_+ra_n',
            t3iconalt: 'пасмурно',
            t3name: 'вечером',
            t4: '+16',
            t4icon: 'skc_d',
            t4iconalt: 'пасмурно',
            t4name: 'ночью',
            url_map: 'https://ya.ru',
            url: 'https://yandex.ru/pogoda?lat=59.958786&lon=30.406012',
            forecast: [
                {
                    day: '+12',
                    night: '+10',
                    icon: 'bkn_ra_d',
                    iconalt: 'облачно',
                    week_day: 'Сб',
                    mday: 4,
                    mon: 'апр'
                },
                {
                    day: '−19',
                    night: '−12',
                    icon: 'bkn_ra_d',
                    iconalt: 'облачно',
                    week_day: 'Вс',
                    mday: 5,
                    mon: 'апр'
                },
                {
                    day: '+22',
                    night: '−15',
                    icon: 'bkn_d',
                    iconalt: 'облачно',
                    week_day: 'Пн',
                    mday: 6,
                    mon: 'апр'
                },
                {
                    day: '−44',
                    night: '+20',
                    icon: 'bkn_d',
                    iconalt: 'медленно',
                    week_day: 'Вт',
                    mday: 7,
                    mon: 'апр'
                }
            ]
        }
    },
    noData = {
        Weather: {
            processed: 1,
            show: 0
        }
    };

function req(home, data) {
    return Object.assign({
        isHermione: true,
        Timestamp: 123456789,
        GeoDetection: {
            lat: 56,
            lon: 34
        },
        getStaticURL: new home.GetStaticURL({
            s3root: 's3/home-static'
        })
    }, data);
}

function wrap (html, blocks, wide, hd) {
    const mainClass = ['traffic', 'weather2']
        .map(name => {
            return `main_${name}_${blocks.includes(name) || name === 'weather2' ? 'yes' : 'no'}`;
        })
        .join(' ');
    return `<style>
    body {
        font-family: 'YS Text', 'Helvetica Neue', Arial, sans-serif;
        --item-width: 136px;
        --item-height: calc(13 * var(--item-width) / 22);
        --item-gap: 8px;
        --item-text-main: 12px;
        --item-text-header: 18px;
        --combined-item-width: calc(2 * var(--item-width) + var(--item-gap));

        height: 500px;
        background: #3de;
    }
    .b-page {
        visibility: visible;
    }
    .b-page_hd_yes {
        --item-width: 164px;
        --item-ratio: 1.205;
    }
    .content{
        width: var(--item-width);
    }

    .b-page_width_wide .content{
        width: calc(var(--item-ratio) * var(--combined-item-width));
    }

    .main_traffic_no{
        height: calc(200px * var(--item-ratio));
    }

    .b-page_hd_yes .main_traffic_no{
        height: calc(232px);
    }

    .main_traffic_yes{
        height: calc(150px * var(--item-ratio));
    }

    .weather2 {
        height: 100%;
    }
    </style>
    <div class="b-page b-page_width_${wide ? 'wide' : 'normal'} b-page_hd_${hd ? 'yes' : 'no'}">
        <div class="${mainClass} content">${html}</div>
    </div>`;
}

function allStates(prefix) {
    const thisMock = '/?datafile=white/blocks/yabro/weather2/weather2.test-data.js&dataname=';

    const getFrame = name => {
            return `<a href="${thisMock}${name}" target="${name}">${name}
                <iframe name="${name}" src="${thisMock}${name}"></iframe>
                </a>`;
        },
        frames = [
            prefix + 'small',
            prefix + 'tall',
            prefix + 'thick',
            prefix + 'hdthick',
            prefix + 'huge',
            prefix + 'hdhuge'
        ].filter(Boolean);

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
                grid-auto-rows: 270px;
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
    alldatatall: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, allData)), []);
    },
    nodatatall: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, noData)), []);
    },

    alldatasmall: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, allData)), ['traffic']);
    },
    nodatasmall: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, noData)), ['traffic']);
    },

    alldatathick: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, allData)), ['traffic'], true);
    },
    nodatathick: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, noData)), ['traffic'], true);
    },
    alldatahdthick: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, allData)), ['traffic'], true, true);
    },
    nodatahdthick: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, noData)), ['traffic'], true, true);
    },

    alldatahuge: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, allData)), [], true);
    },
    nodatahuge: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, noData)), [], true);
    },
    alldatahdhuge: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, allData)), [], true, true);
    },
    nodatahdhuge: (execView, {home}) => {
        return wrap(execView('Weather2', req(home, noData)), [], true, true);
    },

    alldata: () => allStates('alldata'),
    nodata: () => allStates('nodata')
};
