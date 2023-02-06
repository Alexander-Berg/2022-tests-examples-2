/* eslint max-len: 0 */

const widget = {
    'widget': {
        'id': '_topnews-1',
        'xivas': false,
        'isWidgetList': false,
        'initParams': {
            'id': '_topnews-1',
            'params': {
                'wauth': '1..043oyC._topnews-1.1544018012854260.73855104.73855104..76715199.1406.64283b538cb24212d7f5abdee2204b8f',
                'type': 'raw',
                'height': 'auto',
                'prefs_src': '',
                'prefs_height': 'auto',
                'prefs_width': 'auto',
                'prefs': [
                    [
                        'customCatId',
                        ''
                    ],
                    [
                        'customCatComment',
                        ''
                    ],
                    [
                        'shownum',
                        'true'
                    ],
                    [
                        'autoreload',
                        'true'
                    ]
                ],
                'prefs_secure': [],
                'js': [],
                'css': [],
                'yandex': true,
                'prefs_get': {
                    'stocks_fill': '1'
                },
                'is_default': true,
                'usrCh': 0,
                'rebind': 300,
                'position': '1:1:1',
                'havePrefsFrom': 1,
                'open_settings_on_add': 0,
                'isWidgetWorkNormal': true,
                'title': '',
                'intid': '_topnews-1',
                'intclassid': '_topnews',
                'smart': false,
                'defplace': false
            }
        }
    }
};

exports.simple = (execView) => {
    let req = {
        JSON: {
            common: {}
        },
        Local: {
            hour: '13',
            min: '46'
        },
        BigMonth: 'ноября',
        BigDay: '30',
        BigWday: 'четверг',
        JSTimestamp: 'November 30, 2017, 13:46:43',
        MordaZone: 'ru',
        'Topnews': require('./mocks/news.json')
    };
    return '<script>' +
        `window.Widget.Framework.getByWrapperId = function () {return {
            id: '_topnews-1',
            params: {},
            getValue: function () {return 'false';}
        };};` +
    '</script>' + '<style>' +
        '.datetime__flicker{' +
            'opacity: 0' +
        '}' +
    '</style><div class="widget i-bem" data-bem="' + JSON.stringify(widget).replace(/"/g, '&quot;') + '">' +
        execView('News', req) +
        execView.withReq('NewsPopup', {}, req) +
    '</div>';
};
