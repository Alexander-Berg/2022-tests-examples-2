const chai = require('chai');
const e2eUtils = require('../../utils');

describe('Bro Transport', function () {
    const baseUrl = 'test/broTransport/broTransport.hbs';
    const counterId = 24226447;

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .execute((defaultRequestRegEx) => {
                const requestRegEx = new RegExp(defaultRequestRegEx);
                const namespace = {};

                namespace.sendPersistentBeacon = function method(url, data) {
                    if (this !== namespace) {
                        setTimeout(() => {
                            throw new Error(
                                'sendPersistentBeacon called on wrong context',
                            );
                        });
                        return;
                    }

                    if (requestRegEx.test(url)) {
                        window.onRequest({ url, data });
                    }
                };

                window.yandex = {};
                window.yandex.private = {
                    user: {
                        getRegion: () => Promise.resolve(true),
                    },
                };
                window.yandex.experimental = {
                    navigator: namespace,
                };
            }, e2eUtils.defaultRequestRegEx);
    });

    it('should work if offline', function () {
        return this.browser
            .setNetworkConnection(0) // switches browser to offline mode
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.onRequest = done;
                        const counter = new Ya.Metrika2(options.counterId);
                        counter.params({ ok: true });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: { url, data } }) => {
                const {
                    url: parsedUrl,
                    body,
                    brInfo,
                    params,
                    telemetry,
                } = e2eUtils.getRequestParams({
                    url,
                    body: data,
                });
                chai.expect(parsedUrl).to.eq(
                    `${e2eUtils.baseUrl}/watch/${counterId}/1`,
                );
                chai.expect(decodeURIComponent(body), 'no params sent').to.eq(
                    'site-info={"ok":true}',
                );
                chai.expect(brInfo, 'no brinfo url param sent').to.exist;
                chai.expect(params['page-url'], 'no page-url url param sent').to
                    .exist;
                chai.expect(params.charset, 'no charset url param sent').to
                    .exist;
                chai.expect(telemetry.ti).to.eq('0');
            });
    });

    it('should work if sendBeacon API is missing', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window.yandex.experimental.navigator.sendPersistentBeacon =
                            null;
                        serverHelpers.collectRequests(
                            2000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2(options.counterId);
                        counter.params({ ok: true });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: data }) => {
                const requests = data.map(e2eUtils.getRequestParams);
                const [request1, request2] = requests;
                chai.expect(request1.params.wmode).to.eq('7');
                chai.expect(request2.siteInfo).to.deep.eq({ ok: true });
                requests.forEach(({ telemetry }) => {
                    chai.expect(
                        telemetry.ti,
                        'broTransport set telemetry.ti incorrectly',
                    ).to.eq('1');
                });
            });
    });
});
