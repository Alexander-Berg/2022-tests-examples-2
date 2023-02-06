const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('ArtificalHit e2e test', function () {
    const baseDir = 'test/artificalHit';
    const pageTitle = 'ArtificalHit page title';
    const baseUrl = `${baseDir}/artificalHit.hbs`;
    const testUrl = 'contacts';
    const testReferer = 'http://example.com/main';
    const testTitle = 'Контактная информация';
    const counterId = 26302566;
    const goalParams = {
        order_price: 1000.35,
        currency: 'RUB',
    };
    const testCtx = {
        ctx: true,
    };

    const testOptions = {
        counterId,
        testUrl,
        testTitle,
        testReferer,
        goalParams,
        testCtx,
    };

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(3000);
    });

    it('should send http request', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.hit(options.testUrl);

                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf(options.testUrl) !== -1) {
                                done(request);
                            }
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request.url).to.be.ok;

                const { params, brInfo } = e2eUtils.getRequestParams(request);

                chai.expect(brInfo.t).to.be.equal(pageTitle);
                chai.expect(brInfo.ar).to.be.equal('1');
                chai.expect(brInfo.pv).to.be.equal('1');
                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.baseUrl}/${baseDir}/${testUrl}`,
                );
            });
    });
    it('should trim data url data', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.hit('   https://zen.yandex.ru   ');
                        serverHelpers.collectRequests(
                            500,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedReq = requests.map(e2eUtils.getRequestParams);
                const artificalHit = parsedReq.find(
                    (reqInfo) => reqInfo.brInfo.ar === '1',
                );
                chai.expect(artificalHit).to.be.ok;
                chai.expect(artificalHit.params['page-url']).to.be.eq(
                    'https://zen.yandex.ru',
                );
            });
    });
    it('should not send http request without url', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.hit('');
                        counter.hit();
                        serverHelpers.collectRequests(
                            500,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const haveArtificalHit = requests.some((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    return brInfo.ar === '1';
                });

                chai.expect(haveArtificalHit).to.be.false;
            });
    });

    it('should send http request with abs url', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.hit(`/${options.testUrl}`);

                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf(options.testUrl) !== -1) {
                                done(request);
                            }
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request.url).to.be.ok;
                const { params, brInfo } = e2eUtils.getRequestParams(request);

                chai.expect(brInfo.t).to.be.equal(pageTitle);
                chai.expect(brInfo.ar).to.be.equal('1');
                chai.expect(brInfo.pv).to.be.equal('1');
                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.baseUrl}/${testUrl}`,
                );
            });
    });

    it('should send http request with params', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.hit(options.testUrl, {
                            title: options.testTitle,
                            referer: options.testReferer,
                        });

                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf(options.testUrl) !== -1) {
                                done(request);
                            }
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request.url).to.be.ok;
                const { params, brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.t).to.be.equal(testTitle);
                chai.expect(brInfo.ar).to.be.equal('1');
                chai.expect(brInfo.pv).to.be.equal('1');
                chai.expect(params['page-ref']).to.be.equal(testReferer);
                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.baseUrl}/${baseDir}/${testUrl}`,
                );
            });
    });

    it('should send http request with goal params', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.hit(options.testUrl, {
                            title: options.testTitle,
                            referer: options.testReferer,
                            params: options.goalParams,
                        });

                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf(options.testUrl) !== -1) {
                                done(request);
                            }
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request.url).to.be.ok;
                const { params, brInfo, siteInfo } =
                    e2eUtils.getRequestParams(request);
                const siteParams = siteInfo;

                chai.expect(goalParams).to.be.deep.equal(siteParams);
                chai.expect(brInfo.t).to.be.equal(testTitle);
                chai.expect(brInfo.ar).to.be.equal('1');
                chai.expect(brInfo.pv).to.be.equal('1');
                chai.expect(params['page-ref']).to.be.equal(testReferer);
                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.baseUrl}/${baseDir}/${testUrl}`,
                );
            });
    });

    it('should use callback', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        function callback() {
                            done(true);
                        }

                        counter.hit(options.testUrl, {
                            callback,
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: callbackDone }) => {
                chai.expect(callbackDone).to.be.true;
            });
    });

    it('should use callback with ctx', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        function callback() {
                            done(this);
                        }

                        counter.hit(options.testUrl, {
                            callback,
                            ctx: options.testCtx,
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: callbackCtx }) => {
                chai.expect(callbackCtx).to.be.deep.equal(testCtx);
            });
    });

    it(`doesn't log callback's error`, function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            (requests, done) => {
                                done({
                                    requests,
                                    errors: getPageErrors(),
                                });
                            },
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.hit(options.testUrl, {
                            callback() {
                                throw new Error('user error');
                            },
                        });
                    },
                    ...testOptions,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value.requests.length).to.be.equal(2);
                chai.expect(value.errors.usual.length).to.be.equal(1);
                if (value.errors.unhandledrejection.length) {
                    throw value.errors.unhandledrejection[0];
                }
                chai.expect(value.errors.unhandledrejection.length).to.be.equal(
                    0,
                );
                chai.expect(value.errors.usual[0]).to.include('user error');
            });
    });
});
