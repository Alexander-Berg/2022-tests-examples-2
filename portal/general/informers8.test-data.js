/* eslint-env es6 */

const freeRateMoney = require('./mocks/free-rate-money.json'),
    ratesMails = require('./mocks/rate-down-money-no-mails.json'),
    rateDownMoneyNoMails = require('./mocks/no-forecast.json'),
    noRateMailPromo = require('./mocks/no-rate-mail-promo.json'),
    rateMails = require('./mocks/rate-mails.json'),
    margin = '<style>body {margin: 20px 0 0}</style>',
    routeReq = `<script>
    window.mocks = {
        route: ${JSON.stringify(require('./mocks/route.json'))},
        routeInverse: ${JSON.stringify(require('./mocks/route_inverse.json'))}
    };

    var server = window.server = sinon.fakeServer.create();

    XMLHttpRequest.prototype.overrideMimeType = function () {};

    server.respondImmediately = true;
    server.respondWith(/yandex\\.ru\\/geohelper.+points=30\\.3888105547/, JSON.stringify(window.mocks.route));
    server.respondWith(/yandex\\.ru\\/geohelper.+points=30\\.3929405703/, JSON.stringify(window.mocks.routeInverse));
    </script>`;

function informers(data) {
    return function (execView, {home}) {
        const getStaticURL = new home.GetStaticURL({
            s3root: 's3/home-static'
        });
        const req = Object.assign({JSON: {}, getStaticURL}, JSON.parse(JSON.stringify(data)));
        const resources = new home.Resources('touch', req, execView);
        req.resources = resources;
        return routeReq +
            margin +
            execView.withReq('Informers8', {}, req) +
            execView.withReq('Resources__weatherIcons', {}, req) +
            '<script>' + req.settingsJs.getRawScript(req) + '</script>' +
            resources.getHTML('head');
    };
}


exports.freeRateMoney = informers(freeRateMoney);
exports.ratesMails = informers(ratesMails);
exports.rateDownMoneyNoMails = informers(rateDownMoneyNoMails);
exports.noRateMailPromo = informers(noRateMailPromo);
exports.rateMails = informers(rateMails);
