const NEWS = 0,
    WEATHER = 1,
    TRAFFIC = 2;
const map = {
    'news-old': NEWS,
    weather2: WEATHER,
    traffic: TRAFFIC
};

function getPage(blocks, zen, wide) {
    return () => {
        const arr = [],
            pageClass = [
                'b-page b-page_visible_yes',
                wide ? 'b-page_width_wide' : '',
                `b-page_zen_${zen ? 'yes' : 'no'}`
            ].join(' '),
            mainClass = ['main'];
        Object.keys(map).forEach(name => {
            const on = (blocks & map[name]) === map[name]; // eslint-disable-line
            if (on && name !== 'bro-zen') {
                arr.push(name);
            }
            mainClass.push(` main_${name}_${on ? 'yes' : 'no'}  main_${name}_${on ? 'yes' : 'no'}`);
        });

        const blocksHtml = arr.map(name => `<div class="main__item main__${name} main__${name}"><div class="label ${name}"></div></div>`).join('');

        return `<style>
            body {
                font-family: 'YS Text', 'Helvetica Neue', Arial, sans-serif;
                --item-width: 136px;
                --item-height: calc(13 * var(--item-width) / 22);
                --item-gap: 8px;
                --item-text-main: 12px;
                --item-text-header: 18px;
                --page-width: 728px;
            }
            .main__news-old .label {
                background: lime;
            }
            .main__weather2 .label {
                background: green;
            }
            .main__traffic .label {
                background: cyan;
            }
            .news-old {
                min-width: 30em;
            }
            </style>
            <div class="${pageClass || ''}"><div class="${mainClass.join(' ')} content">${blocksHtml}</div></div>`;
    };
}

module.exports = {
    newsWeatherTrafficZenNormal: getPage(NEWS + WEATHER + TRAFFIC, true, false),
    newsWeatherTrafficNormal: getPage(NEWS + WEATHER + TRAFFIC, false, false),
    newsWeatherNormal: getPage(NEWS + WEATHER, false, false),

    newsWeatherTrafficZenWide: getPage(NEWS + WEATHER + TRAFFIC, true, true),
    newsWeatherTrafficWide: getPage(NEWS + WEATHER + TRAFFIC, false, true),
    newsWeatherWide: getPage(NEWS + WEATHER, false, true)
};
