/* eslint-env es6 */
/* eslint max-len: 0 */
const mocks = require('./mocks/mocks');

function getAdsReq(obj = {}) {
    return {
        ads: {
            hasBanner(name) {
                return name === 'popup';
            },
            banner() {
                return Object.assign({}, mocks.simple, obj);
            },
            getShowUrl() {
                return 'https://yandex.ru/empty.html';
            }
        },
        cookie_set_gif: 'https://yandex.ru/empty.html'
    };
}

const colors = mocks.colors;
const designTypes = ['old-2b', 'new-1b', 'new-2b'];

designTypes.forEach(designType => {
    colors.forEach((color, index) => {
        const id = `${designType}-${color}`;

        exports[id] = function(execView) {
            let buttonColor = undefined;

            if (['new-1b', 'new-2b'].includes(designType) && index < 3) {
                buttonColor = 'FFFFFF';
            }

            return execView('DistPopup', {}, getAdsReq({
                color,
                'button_color': buttonColor,
                design_type: designType
            }));
        };
    });
});

exports['old-2b'] = function(execView) {
    const popups = colors.map(color => execView('DistPopup', {}, getAdsReq({color}))).join('');

    return popups + execView('Style', {
        content: `
        body[class] {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-gap: 5px;
            overflow-y: scroll;
        }
        .dist-popup {
            position: relative;
            margin: auto;
            display: inline-block;
        }`
    });
};

exports['new-1b'] = function(execView) {
    const popups = colors.map((color, index) => execView('DistPopup', {}, getAdsReq({
        color,
        'button_color': index < 3 ? 'FFFFFF' : undefined,
        'design_type': 'new-1b'
    }))).join('');

    return popups + execView('Style', {
        content: `
        body[class] {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-gap: 5px;
            overflow-y: scroll;
        }
        .dist-popup {
            position: relative;
            margin: auto;
            display: inline-block;
        }`
    });
};

exports['new-2b'] = function(execView) {
    const popups = colors.map((color, index) => execView('DistPopup', {}, getAdsReq({
        color,
        'button_color': index < 3 ? 'FFFFFF' : undefined,
        'design_type': 'new-2b'
    }))).join('');

    return popups + execView('Style', {
        content: `
        body[class] {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-gap: 5px;
            overflow-y: scroll;
        }
        .dist-popup {
            position: relative;
            margin: auto;
            display: inline-block;
        }`
    });
};

exports.ie11Download = function (execView) {
    return '<style>.i-install-download__arrow{animation-name:none;}</style>' + execView('DistPopup', {}, {
        ads: {
            hasBanner(name) {
                return name === 'popup';
            },
            banner() {
                return Object.assign({}, mocks.ie11);
            },
            getShowUrl() {
                return 'https://yandex.ru/empty.html';
            }
        },
        cookie_set_gif: 'https://yandex.ru/empty.html'
    });
};

exports.ffDownload = function (execView) {
    return '<style>.i-install-download__arrow{animation-name:none;}</style>' + execView('DistPopup', {}, {
        ads: {
            hasBanner(name) {
                return name === 'popup';
            },
            banner() {
                return Object.assign({}, mocks.ff);
            },
            getShowUrl() {
                return 'https://yandex.ru/empty.html';
            }
        },
        cookie_set_gif: 'https://yandex.ru/empty.html'
    });
};
