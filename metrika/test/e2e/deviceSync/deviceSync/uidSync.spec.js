const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('uidSync', function () {
    const baseUrl = 'https://yandex.ru/test/deviceSync/uidSync.hbs';

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('should request device at yandex if platform is iOs', function () {
        const counterId = 42080444;
        return this.browser
            .url(baseUrl)
            .execute(() => {
                // make native
                window.navigator.sendBeacon = function (url) {
                    window.onRequest({ url });
                }.bind();
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            sbp: {
                                                a: '1',
                                                b: '2',
                                            },
                                        },
                                    },
                                },
                            ],
                            function () {
                                window.onRequest = done;
                                Object.defineProperty(
                                    window.navigator,
                                    'platform',
                                    { value: 'iPhone' },
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: { url, data } }) => {
                const { url: parsedUrl, params } = e2eUtils.getRequestParams({
                    url,
                    body: data,
                });
                chai.expect(parsedUrl).to.eq(
                    'https://yandexmetrica.com:30103/i',
                );
                chai.expect(params.a).to.eq('1');
                chai.expect(params.b).to.eq('2');
                chai.expect(params.c).to.eq(counterId.toString());
            });
    });
});
