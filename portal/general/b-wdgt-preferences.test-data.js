exports.weather = (execView) => '<style>' +
    '.b-wdgt-preferences__spin {' +
        // 'animation-duration: 1s !important;' +
        // 'animation-play-state: paused;' +
        'animation-fill-mode: both;' +
    '}' +
'</style><script>' +
    `$(function () {
        window.mocks = {
            weatherForm: ${JSON.stringify(require('./mocks/weather-form.json'))},
            weatherSuggest: ${JSON.stringify(require('./mocks/weather-suggest.json'))}
        };

        Widget.Framework._id['_weather-1'] = window.widget = {
            getId: function () {
                return '_weather-1';
            },
            getWidgetId: function () {
                return '_weather-1';
            },
            getAuth: function () {
                return '';
            },
            params: {
            }
        };
        window.popup = $('.b-wdgt-preferences').bem('b-wdgt-preferences');
        window.xhr = sinon.useFakeXMLHttpRequest();
        window.requests = [];

        xhr.onCreate = function (xhr) {
            requests.push(xhr);
        };

        var oldAjax = $.ajax;
        window.jsonps = [];
        $.ajax = function (opts) {
            if (opts.url.indexOf('suggest-geo') > -1) {
                var res = $.Deferred();
                window.jsonps.push(res);
                return res;
            }
            return oldAjax.apply(this, arguments);
        };
    });` +
'</script>' + execView('BWdgtPreferences', {
    TemplatePrimordial: 'v14'
});

exports.tv = (execView) => '<script>' +
    `$(function () {
        window.mocks = {
            tvForm: ${JSON.stringify(require('./mocks/tv-form.json'))}
        };

        Widget.Framework._id['_tv-1'] = window.widget = {
            getId: function () {
                return '_tv-1';
            },
            getWidgetId: function () {
                return '_tv-1';
            },
            getAuth: function () {
                return '';
            },
            params: {
            }
        };
        window.popup = $('.b-wdgt-preferences').bem('b-wdgt-preferences');
        window.xhr = sinon.useFakeXMLHttpRequest();
        window.requests = [];

        xhr.onCreate = function (xhr) {
            requests.push(xhr);
        };
    });` +
    '</script>' + execView('BWdgtPreferences', {
    TemplatePrimordial: 'v14'
});


exports.stocks = (execView) => '<script>' +
    `$(function () {
        window.mocks = {
            stocksForm: ${JSON.stringify(require('./mocks/stocks-form.json'))}
        };

        Widget.Framework._id['_stocks-1'] = window.widget = {
            getId: function () {
                return '_stocks-1';
            },
            getWidgetId: function () {
                return '_stocks-1';
            },
            getAuth: function () {
                return '';
            },
            params: {
            }
        };
        window.popup = $('.b-wdgt-preferences').bem('b-wdgt-preferences');
        window.xhr = sinon.useFakeXMLHttpRequest();
        window.requests = [];

        xhr.onCreate = function (xhr) {
            requests.push(xhr);
        };
    });` +
    '</script>' + execView('BWdgtPreferences', {
    TemplatePrimordial: 'v14'
});
