const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Hit e2e test', function () {
    const baseUrl = 'test/hit/hit.hbs';
    const counterId = 26302566;

    const reffererTest = (referUrl) => {
        return function () {
            const testRef = `${e2eUtils.baseUrl}/${referUrl}`;
            return this.browser
                .url(referUrl)
                .then(() => {
                    return this.browser.click('.nextPage');
                })
                .getText('body')
                .then((innerText) => {
                    chai.expect(innerText).to.be.equal('Hit page');
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            serverHelpers.onRequest(function (request) {
                                done(request);
                            }, options.regexp.defaultRequestRegEx);
                            new Ya.Metrika2({
                                id: options.counterId,
                            });
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: request }) => {
                    if (!request.url) {
                        chai.assert(false, 'No hit');
                    } else {
                        const { params } = e2eUtils.getRequestParams(request);
                        chai.expect(params['page-ref']).to.be.equal(testRef);
                    }
                });
        };
    };

    const forceReffererTest = (referUrl) => {
        return function () {
            const testRef = `${e2eUtils.baseUrl}/${referUrl}`;
            const url = `${e2eUtils.baseUrl}/test/hit/hit.hbs/`;
            return this.browser
                .url(url)
                .getText('body')
                .then((innerText) => {
                    chai.expect(innerText).to.be.equal('Hit page');
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            serverHelpers.onRequest(function (request) {
                                done(request);
                            }, options.regexp.defaultRequestRegEx);
                            new Ya.Metrika2({
                                id: options.counterId,
                                referrer: options.testRef,
                            });
                        },
                        counterId,
                        testRef,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: request }) => {
                    if (!request.url) {
                        chai.assert(false, 'No hit');
                    } else {
                        const { params } = e2eUtils.getRequestParams(request);
                        chai.expect(params['page-ref']).to.be.equal(testRef);
                    }
                });
        };
    };

    beforeEach(function () {
        return this.browser.deleteCookie();
    });
    it('should work with Promise polyfil', function () {
        return this.browser
            .url(`${baseUrl}?promise=1`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request).to.be.lengthOf(1);
            });
    });
    it('should work with reduce polyfil', function () {
        return this.browser
            .url(`${baseUrl}?reduce=1`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request).to.be.lengthOf(1);
            });
    });
    // todo расскипать после METR-39063
    it.skip('should fail if wrong counterId', function () {
        return this.browser
            .url(`${baseUrl}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers) {
                        serverHelpers.collectRequests(500);
                        new Ya.Metrika2({
                            id: '',
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request).to.lengthOf(0);
            });
    });

    it(
        'should send http request with refferer without slash',
        reffererTest('test/hit/referer_hit.hbs'),
    );

    it(
        'should send http request with refferer with slash',
        reffererTest('test/hit/referer_hit.hbs/'),
    );

    it(
        'should send http request with refferer without slash from counter options',
        forceReffererTest('test/hit/referer_hit.hbs'),
    );

    it(
        'should send http request with refferer with slash from counter options',
        forceReffererTest('test/hit/referer_hit.hbs/'),
    );

    it('should send http request', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                if (!request.url) {
                    chai.assert(false, 'No hit');
                } else {
                    const { url, params, brInfo } =
                        e2eUtils.getRequestParams(request);
                    chai.assert(url.match(`watch/${counterId}`));
                    chai.expect(brInfo.t).to.be.equal('hit page title');
                    chai.expect(brInfo.pv).to.be.equal('1');
                    chai.expect(params.charset).to.be.equal('utf-8');
                    chai.expect(params['page-url']).to.be.equal(
                        `${e2eUtils.baseUrl}/${baseUrl}`,
                    );
                }
            });
    });
});
