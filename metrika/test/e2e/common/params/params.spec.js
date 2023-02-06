const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Params e2e test', function () {
    const baseUrl = 'test/params/params.hbs';
    const fullUrl = `${e2eUtils.baseUrl}/${baseUrl}`;
    const counterId = 26302566;
    const testParams = {
        someParam: 'someVal',
        someNumber: 12323,
        someObj: {
            someList: [1, 23, '', null],
        },
    };
    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });
    it('should be ok with arrays', function () {
        const paramsList = [{ param1: 1 }, { param2: 2 }];
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2(options.counterId);
                        const requests = [];
                        counter.params(options.paramsList);
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                            if (requests.length === 2) {
                                done(requests);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    paramsList,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const paramsReq = requests
                    .map(e2eUtils.getRequestParams)
                    .find(({ brInfo }) => brInfo.pa);
                chai.expect(paramsReq).to.be.ok;
                chai.expect(paramsReq.siteInfo).to.be.deep.equal(paramsList);
            });
    });
    it('should be ok with another signature', function () {
        const arrayParams = ['first.key', 'second.key', 'value'];
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2(options.counterId);
                        const requests = [];
                        counter.params(...options.arrayParams);
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                            if (requests.length === 2) {
                                done(requests);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    arrayParams,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const paramsReq = requests
                    .map(e2eUtils.getRequestParams)
                    .find(({ brInfo }) => brInfo.pa);
                chai.expect(paramsReq).to.be.ok;
                chai.expect(paramsReq.siteInfo).to.be.deep.equal({
                    'first.key': {
                        'second.key': 'value',
                    },
                });
            });
    });
    it('should use artificial url', function () {
        const artHitUrl = `http://yandex.ru`;
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            defer: true,
                        });
                        counter.hit(options.artHitUrl);
                        setTimeout(function () {
                            counter.params(options.testParams);
                        }, 0);
                        const requests = [];
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                            if (requests.length === 3) {
                                done(requests);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    artHitUrl,
                    testParams,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const paramsReq = requests
                    .map(e2eUtils.getRequestParams)
                    .find(({ brInfo }) => brInfo.pa);

                const { params } = paramsReq;
                chai.expect(paramsReq.siteInfo).to.be.deep.equal(testParams);
                chai.expect(params['page-url']).to.be.equal(artHitUrl);
            });
    });
    it('should send big params separately from hit', function () {
        const bigParams = {
            testList: Array.apply(0, Array(100)).map(function () {
                return testParams;
            }),
        };
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                            params: options.bigParams,
                        });
                    },
                    bigParams,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const [, paramsReq] = requests;
                const { brInfo, params, siteInfo } =
                    e2eUtils.getRequestParams(paramsReq);
                chai.expect(brInfo.pa).to.be.equal('1');
                chai.expect(params['page-url']).to.be.equal(fullUrl);
                chai.expect(siteInfo).to.be.deep.equal(bigParams);
            });
    });
    it('should send params from constructor', function () {
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            params: options.testParams,
                        });
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                    },
                    testParams,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { siteInfo } = e2eUtils.getRequestParams(request);
                chai.expect(siteInfo).to.be.deep.equal(testParams);
            });
    });
    it('should skip params with defer request', function () {
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        new Ya.Metrika2({
                            id: options.counterId,
                            defer: true,
                            params: options.testParams,
                        });
                    },
                    testParams,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests).to.have.been.lengthOf(1);
                chai.expect(requests[0].siteInfo).to.be.not.ok;
            });
    });
    it('should send params from method', function () {
        return this.browser
            .then((innerText) => {
                chai.expect('Params page', innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2(options.counterId);
                        counter.params(options.testParams);
                    },
                    testParams,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(
                    e2eUtils.getRequestParams(requests[1]).siteInfo,
                ).to.be.deep.equal(testParams);
            });
    });
    it(`doesn't log callback's error`, function () {
        return this.browser
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

                        counter.params({}, () => {
                            throw new Error('user error');
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value.requests.length).to.be.equal(2);
                chai.expect(value.errors.usual.length).to.be.equal(1);
                chai.expect(value.errors.unhandledrejection.length).to.be.equal(
                    0,
                );
                chai.expect(value.errors.usual[0]).to.include('user error');
            });
    });
});
