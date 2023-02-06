const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('UrlReferrer e2e test', function () {
    const baseUrlPath = 'test/urlReferrer';
    const res = 'urlReferrer.hbs';
    const baseUrl = `${baseUrlPath}/${res}`;
    const fullBaseUrl = `${e2eUtils.baseUrl}/${baseUrl}`;

    const testUrl = 'test.hbs';
    const testHttpUrl = `http://${testUrl}`;

    const testReferrer = 'referrer.hbs';
    const testHttpReferrer = `http://${testReferrer}`;

    const testHitUrl = 'http://test/urlReferrer/hit.hbs';
    const testGoal = 'testGoal';

    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });
    it('should trim referer', function () {
        return this.browser
            .url(fullBaseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        Object.defineProperty(document, 'referrer', {
                            get() {
                                return '  http://zen.yandex.ru  ';
                            },
                        });
                        new Ya.Metrika2(options.counterId);
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(fullBaseUrl);
                chai.expect(params['page-ref']).to.be.eq(
                    'http://zen.yandex.ru',
                );
            });
    });

    it('should send http request with default referrer and url', function () {
        return this.browser
            .url(fullBaseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                        });

                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                }),
            )

            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(fullBaseUrl);
                chai.expect(params['page-ref']).to.be.not.ok;
            });
    });

    it('should send http request with referrer and url', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            url: options.testUrl,
                            referrer: options.testReferrer,
                        });
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    testUrl,
                    testReferrer,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.baseUrl}/${baseUrlPath}/${testUrl}`,
                );
                chai.expect(params['page-ref']).to.be.equal(
                    `${e2eUtils.baseUrl}/${baseUrlPath}/${testReferrer}`,
                );
            });
    });

    it('should send http request with referrer and url with protocol', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            url: options.testHttpUrl,
                            referrer: options.testHttpReferrer,
                        });
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    testHttpUrl,
                    testHttpReferrer,
                }),
            )

            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(testHttpUrl);
                chai.expect(params['page-ref']).to.be.equal(testHttpReferrer);
            });
    });

    it('should send request without referrer on artificial hit', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            url: options.testUrl,
                            referrer: options.testReferrer,
                        });

                        let sendHit = false;
                        serverHelpers.onRequest(function (request) {
                            if (!sendHit) {
                                sendHit = true;
                                counter.hit(options.testHitUrl);
                            } else {
                                done(request);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    testUrl,
                    testReferrer,
                    testHitUrl,
                }),
            )

            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(testHitUrl);
                chai.expect(params['page-ref']).to.be.undefined;
            });
    });

    it('should send request with referrer on artificial hit', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            url: options.testUrl,
                            referrer: options.testReferrer,
                        });

                        let sendHit = false;
                        serverHelpers.onRequest(function (request) {
                            if (!sendHit) {
                                sendHit = true;
                                counter.hit(
                                    options.testHitUrl,
                                    '',
                                    options.testHttpReferrer,
                                );
                            } else {
                                done(request);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    testUrl,
                    testHttpReferrer,
                    testReferrer,
                    testHitUrl,
                }),
            )

            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(testHitUrl);
                chai.expect(params['page-ref']).to.be.equal(testHttpReferrer);
            });
    });

    it('should send request with referrer on reachGoal', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            url: options.testUrl,
                            referrer: options.testReferrer,
                        });

                        let sendGoal = false;
                        serverHelpers.onRequest(function (request) {
                            if (!sendGoal) {
                                sendGoal = true;
                                counter.reachGoal(options.testGoal);
                            }

                            if (request.url.indexOf('page-url=goal') !== -1) {
                                done(request);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    testUrl,
                    testReferrer,
                    testHitUrl,
                    testGoal,
                }),
            )

            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.goalUrl}/${testGoal}`,
                );
                chai.expect(params['page-ref']).to.be.equal(fullBaseUrl);
            });
    });

    it('should send request with utl on notBounce', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            url: options.testUrl,
                            accurateTrackBounce: 1000,
                        });

                        let sendNotBounce = false;
                        serverHelpers.onRequest(function (request) {
                            if (!sendNotBounce) {
                                sendNotBounce = true;
                            } else {
                                done(request);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    testUrl,
                }),
            )

            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { params, brInfo } = e2eUtils.getRequestParams(request);

                chai.expect(brInfo.nb).to.be.equal('1');
                chai.expect(params['page-url']).to.be.equal(fullBaseUrl);
                chai.expect(params['page-ref']).to.be.undefined;
            });
    });
});
